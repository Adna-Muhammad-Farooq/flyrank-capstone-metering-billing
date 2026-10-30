import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

router = APIRouter()


class CheckoutRequest(BaseModel):
    tenant_id: int


@router.post("/billing/checkout")
def create_checkout(request: CheckoutRequest):
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    price_id = os.getenv("STRIPE_PRO_PRICE_ID")

    if not secret_key or not price_id:
        raise HTTPException(
            status_code=503,
            detail="Stripe Checkout is not configured"
        )

    if os.getenv("STRIPE_LOCAL_TEST_MODE") == "true":
        raise HTTPException(
            status_code=503,
            detail="Real Checkout is disabled in local test mode"
        )

    stripe.api_key = secret_key

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1
                }
            ],
            client_reference_id=str(request.tenant_id),
            subscription_data={
                "metadata": {
                    "tenant_id": str(request.tenant_id),
                    "plan_name": "Pro"
                }
            },
            success_url="http://localhost:8000/docs",
            cancel_url="http://localhost:8000/docs",
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id
        }

    except stripe.StripeError:
        raise HTTPException(
            status_code=502,
            detail="Unable to create Stripe Checkout session"
        )