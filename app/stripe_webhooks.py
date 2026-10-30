import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import StripeWebhookEvent
from app.subscription_service import (
    update_subscription,
    cancel_subscription,
)

load_dotenv()

router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    if not webhook_secret:
        raise HTTPException(
            status_code=503,
            detail="Stripe webhook secret is not configured",
        )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=webhook_secret,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(
            status_code=400,
            detail="Invalid Stripe webhook",
        )

    event_id = event["id"]
    event_type = event["type"]

    db = SessionLocal()

    try:
        existing_event = (
            db.query(StripeWebhookEvent)
            .filter(
                StripeWebhookEvent.stripe_event_id == event_id
            )
            .first()
        )

        if existing_event:
            return {
                "received": True,
                "duplicate": True,
                "event_id": event_id,
                "event_type": event_type,
            }

        # Local simulation only
        if (
            event_type == "customer.subscription.created"
            and os.getenv("STRIPE_LOCAL_TEST_MODE") == "true"
        ):
            data = event["data"]["object"].to_dict()
            metadata = data.get("metadata", {})

            tenant_id = int(metadata["tenant_id"])
            plan_name = metadata["plan_name"]
            subscription_id = data["id"]
            status = data["status"]

            update_subscription(
                db=db,
                tenant_id=tenant_id,
                plan_name=plan_name,
                stripe_subscription_id=subscription_id,
                status=status,
            )

        elif (
            event_type == "customer.subscription.deleted"
            and os.getenv("STRIPE_LOCAL_TEST_MODE") == "true"
        ):
            data = event["data"]["object"].to_dict()

            cancel_subscription(
                db=db,
                stripe_subscription_id=data["id"],
            )

        db.add(
            StripeWebhookEvent(
                stripe_event_id=event_id,
                event_type=event_type,
            )
        )

        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Webhook event conflict",
            )

        return {
            "received": True,
            "duplicate": False,
            "event_id": event_id,
            "event_type": event_type,
        }

    except (ValueError, KeyError, TypeError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid subscription event: {exc}",
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()