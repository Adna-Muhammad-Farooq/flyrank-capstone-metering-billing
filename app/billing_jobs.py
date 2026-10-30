from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import UsageEvent


def calculate_monthly_bill(
    db: Session,
    tenant_id: int,
    year: int,
    month: int,
):
    """Calculate a tenant's monthly usage cost."""

    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    if not 1 <= year <= 9999:
        raise ValueError("Invalid year")

    month_start = datetime(
        year, month, 1, tzinfo=timezone.utc
    )

    if month == 12:
        month_end = datetime(
            year + 1, 1, 1, tzinfo=timezone.utc
        ) if year < 9999 else datetime.max.replace(
            tzinfo=timezone.utc
        )
    else:
        month_end = datetime(
            year, month + 1, 1, tzinfo=timezone.utc
        )

    result = (
        db.query(
            func.coalesce(
                func.sum(UsageEvent.cost_micro_usd), 0
            )
        )
        .filter(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.created_at >= month_start,
            UsageEvent.created_at < month_end,
        )
        .scalar()
    )

    total_micro_usd = int(result or 0)

    return {
        "tenant_id": tenant_id,
        "year": year,
        "month": month,
        "total_cost_micro_usd": total_micro_usd,
        "total_cost_usd": f"{total_micro_usd / 1_000_000:.6f}",
    }

from app.database import SessionLocal
from app.models import Tenant


def run_monthly_billing_job(year: int, month: int):
    """Calculate monthly usage costs for all tenants."""

    db = SessionLocal()

    try:
        tenants = db.query(Tenant).all()
        reports = []

        for tenant in tenants:
            report = calculate_monthly_bill(
                db=db,
                tenant_id=tenant.id,
                year=year,
                month=month,
            )
            reports.append(report)

        return reports

    finally:
        db.close()