from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UsageRequest, UsageResponse
from app.metering import record_usage

from sqlalchemy import func
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models import UsageEvent, Subscription, Plan, Tenant
from app.stripe_webhooks import router as stripe_router
from app.stripe_checkout import router as checkout_router

app = FastAPI(
    title="Usage Metering & Billing Engine",
    description="FlyRank Backend AI Engineering Capstone",
    version="1.0.0"
)

app.include_router(stripe_router)
app.include_router(checkout_router)

@app.get("/")
def home():
    return {
        "message": "Usage Metering & Billing Engine API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/usage", response_model=UsageResponse)
def create_usage(
    request: UsageRequest,
    db: Session = Depends(get_db)
):
    return record_usage(db, request)

@app.get("/usage")
def get_usage(tenant_id: int, db: Session = Depends(get_db)):

    tenant = db.query(Tenant).filter(
        Tenant.id == tenant_id
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == tenant_id,
        Subscription.status == "active"
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=402,
            detail="No active subscription"
        )

    plan = db.query(Plan).filter(
        Plan.id == subscription.plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found"
        )

    now = datetime.now(timezone.utc)
    month_start = datetime(
        now.year, now.month, 1, tzinfo=timezone.utc
    )

    def monthly_usage(usage_type):
        return int(
            db.query(
                func.coalesce(func.sum(UsageEvent.quantity), 0)
            )
            .filter(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.usage_type == usage_type,
                UsageEvent.created_at >= month_start,
                UsageEvent.created_at <= now
            )
            .scalar()
        )

    api_calls = monthly_usage("api_call")
    ai_tokens = monthly_usage("ai_tokens")
    
    total_cost_micro_usd = int(
        db.query(
            func.coalesce(func.sum(UsageEvent.cost_micro_usd), 0)
        )
        .filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.usage_type == "ai_tokens",
            UsageEvent.created_at >= month_start,
            UsageEvent.created_at <= now
        )
        .scalar()
    )

    return {
        "tenant_id": tenant_id,
        "plan": plan.name,
        "month": now.strftime("%Y-%m"),
        "api_calls": {
            "used": api_calls,
            "limit": plan.api_call_limit,
            "remaining": max(0, plan.api_call_limit - api_calls)
        },

                "billing": {
            "total_cost_micro_usd": total_cost_micro_usd
        },

        "ai_tokens": {
            "used": ai_tokens,
            "limit": plan.token_limit,
            "remaining": max(0, plan.token_limit - ai_tokens)
        }
    }