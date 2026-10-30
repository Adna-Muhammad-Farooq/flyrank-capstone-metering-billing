from sqlalchemy.orm import Session

from app.models import Plan, Subscription


def update_subscription(
    db: Session,
    tenant_id: int,
    plan_name: str,
    stripe_subscription_id: str,
    status: str = "active",
):
    # Find the requested plan
    plan = db.query(Plan).filter(
        Plan.name == plan_name
    ).first()

    if not plan:
        raise ValueError(f"Plan '{plan_name}' not found")

    # Find the tenant's existing subscription
    subscription = db.query(Subscription).filter(
        Subscription.tenant_id == tenant_id
    ).with_for_update().first()

    if not subscription:
        raise ValueError("Subscription not found")

    # Prevent assigning an existing Stripe subscription
    # to a different tenant
    if subscription.stripe_subscription_id not in (
        None,
        stripe_subscription_id,
    ):
        raise ValueError("Stripe subscription ID mismatch")

    subscription.plan_id = plan.id
    subscription.status = status
    subscription.stripe_subscription_id = stripe_subscription_id

    db.flush()

    return subscription

def cancel_subscription(
    db: Session,
    stripe_subscription_id: str,
):
    # Find the subscription using its Stripe ID
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.stripe_subscription_id
            == stripe_subscription_id
        )
        .with_for_update()
        .first()
    )

    if not subscription:
        raise ValueError("Stripe subscription not found")

    # Avoid processing an already canceled subscription again
    if subscription.status == "canceled":
        return subscription

    subscription.status = "canceled"

    db.flush()

    return subscription