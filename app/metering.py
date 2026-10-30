
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Tenant, UsageEvent, Subscription, Plan
from app.schemas import UsageRequest
from app.pricing import calculate_token_cost


def record_usage(db: Session, request: UsageRequest):

    # Calculate the cost of AI tokens
    cost_micro_usd = 0

    if request.usage_type == "ai_tokens":
        pricing = calculate_token_cost(
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens,
            cached_tokens=request.cached_tokens,
            reasoning_tokens=request.reasoning_tokens
        )
        cost_micro_usd = pricing["total_cost_micro_usd"]

    # Check whether this request was already recorded
    existing_event = db.query(UsageEvent).filter(
        UsageEvent.tenant_id == request.tenant_id,
        UsageEvent.idempotency_key == request.idempotency_key
    ).first()

    if existing_event:
        return duplicate_response(existing_event, request, cost_micro_usd)

    # Check that the customer exists
    tenant = db.query(Tenant).filter(
        Tenant.id == request.tenant_id
    ).first()

    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant not found"
        )

    # Lock the tenant row while checking quota and saving usage
    db.query(Tenant).filter(
        Tenant.id == request.tenant_id
    ).with_for_update().first()

    # Check again after acquiring the lock
    existing_event = db.query(UsageEvent).filter(
        UsageEvent.tenant_id == request.tenant_id,
        UsageEvent.idempotency_key == request.idempotency_key
    ).first()

    if existing_event:
        db.rollback()
        return duplicate_response(existing_event, request, cost_micro_usd)

    # Check quota before recording usage
    try:
        check_quota(
            db,
            request.tenant_id,
            request.usage_type,
            request.quantity
        )

        # Create a new usage event
        event = UsageEvent(
        tenant_id=request.tenant_id,
        usage_type=request.usage_type,
        quantity=request.quantity,
        idempotency_key=request.idempotency_key,
        cost_micro_usd=cost_micro_usd,
        input_tokens=request.input_tokens,
        output_tokens=request.output_tokens,
        cached_tokens=request.cached_tokens,
        reasoning_tokens=request.reasoning_tokens
    )

        db.add(event)
        db.commit()
        db.refresh(event)

    except IntegrityError:
        db.rollback()

        # Handle a duplicate request
        existing_event = db.query(UsageEvent).filter(
            UsageEvent.tenant_id == request.tenant_id,
            UsageEvent.idempotency_key == request.idempotency_key
        ).first()

        if existing_event:
            return duplicate_response(existing_event, request, cost_micro_usd)

        raise

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Usage recorded successfully",
        "tenant_id": event.tenant_id,
        "usage_type": event.usage_type,
        "quantity": event.quantity,
        "usage_event_id": event.id,
        "cost_micro_usd": event.cost_micro_usd
    }


def duplicate_response(event, request, cost_micro_usd):

        if (
        event.usage_type != request.usage_type
        or event.quantity != request.quantity
        or event.cost_micro_usd != cost_micro_usd
        or event.input_tokens != request.input_tokens
        or event.output_tokens != request.output_tokens
        or event.cached_tokens != request.cached_tokens
        or event.reasoning_tokens != request.reasoning_tokens
    ):
            raise HTTPException(
            status_code=409,
            detail="Idempotency key already used for different usage"
        )
        
        return {
        "message": "Usage recorded successfully",
        "tenant_id": event.tenant_id,
        "usage_type": event.usage_type,
        "quantity": event.quantity,
        "usage_event_id": event.id,
        "cost_micro_usd": event.cost_micro_usd
    }


def check_quota(db: Session, tenant_id: int, usage_type: str, quantity: int):

    if usage_type not in ("api_call", "ai_tokens"):
        raise HTTPException(
            status_code=422,
            detail="Usage type must be api_call or ai_tokens"
        )

    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.tenant_id == tenant_id,
            Subscription.status == "active"
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=402,
            detail="No active subscription. Please upgrade or activate a plan."
        )

    plan = db.query(Plan).filter(
        Plan.id == subscription.plan_id
    ).first()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    used = (
        db.query(func.coalesce(func.sum(UsageEvent.quantity), 0))
        .filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.usage_type == usage_type,
            UsageEvent.created_at >= month_start,
            UsageEvent.created_at <= now
        )
        .scalar()
    )

    limit = (
        plan.api_call_limit
        if usage_type == "api_call"
        else plan.token_limit
    )

    if used + quantity > limit:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Monthly usage quota exceeded",
                "plan": plan.name,
                "used": int(used),
                "requested": quantity,
                "limit": limit
            }
        )
