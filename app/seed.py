
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Tenant, Plan, Subscription


def seed_database():
    db = SessionLocal()

    try:
        # Create or update subscription plans
        plan_details = [
            ("Free", 1000, 100000),
            ("Pro", 10000, 1000000),
        ]

        for name, api_limit, token_limit in plan_details:
            plan = db.scalar(
                select(Plan).where(Plan.name == name)
            )

            if plan is None:
                plan = Plan(
                    name=name,
                    api_call_limit=api_limit,
                    token_limit=token_limit,
                )
                db.add(plan)
            else:
                plan.api_call_limit = api_limit
                plan.token_limit = token_limit

        db.flush()

        free_plan = db.scalar(
            select(Plan).where(Plan.name == "Free")
        )

        # Use a fixed demo tenant ID so rerunning is safe
        tenant = db.get(Tenant, 1)

        if tenant is None:
            tenant = Tenant(id=1, name="Demo Customer")
            db.add(tenant)
            db.flush()

        # Create a subscription only when none exists
        existing_subscription = db.scalar(
            select(Subscription).where(
                Subscription.tenant_id == tenant.id
            )
        )

        if existing_subscription is None:
            db.add(
                Subscription(
                    tenant_id=tenant.id,
                    plan_id=free_plan.id,
                    status="active",
                )
            )

        db.commit()
        print("Database seeded successfully.")
        print("Demo tenant ID:", tenant.id)
        print("Free and Pro plans are available.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
