import pytest
from fastapi import HTTPException

from app.stripe_checkout import CheckoutRequest, create_checkout


def test_checkout_without_credentials(monkeypatch):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.delenv("STRIPE_PRO_PRICE_ID", raising=False)

    with pytest.raises(HTTPException) as error:
        create_checkout(CheckoutRequest(tenant_id=1))

    assert error.value.status_code == 503
    assert error.value.detail == "Stripe Checkout is not configured"


def test_checkout_disabled_in_local_mode(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
    monkeypatch.setenv("STRIPE_PRO_PRICE_ID", "price_test_placeholder")
    monkeypatch.setenv("STRIPE_LOCAL_TEST_MODE", "true")

    with pytest.raises(HTTPException) as error:
        create_checkout(CheckoutRequest(tenant_id=1))

    assert error.value.status_code == 503
    assert error.value.detail == "Real Checkout is disabled in local test mode"