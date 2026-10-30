import json
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import stripe_webhooks


def make_request(payload, signature=None):
    """Create a fake HTTP request."""

    body = json.dumps(payload).encode("utf-8")

    headers = []
    if signature:
        headers.append(
            (b"stripe-signature", signature.encode("utf-8"))
        )

    async def receive():
        return {
            "type": "http.request",
            "body": body,
            "more_body": False,
        }

    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/webhooks/stripe",
            "headers": headers,
        },
        receive,
    )


def make_event(event_id, event_type, data=None):
    """Create a fake Stripe event."""

    obj = MagicMock()
    obj.to_dict.return_value = data or {}

    return {
        "id": event_id,
        "type": event_type,
        "data": {"object": obj},
    }


@pytest.mark.asyncio
async def test_missing_webhook_secret(monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET", raising=False)

    request = make_request({"id": "evt_001"}, "test_signature")

    with pytest.raises(HTTPException) as error:
        await stripe_webhooks.stripe_webhook(request)

    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_missing_signature(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")

    request = make_request({"id": "evt_002"})

    with pytest.raises(HTTPException) as error:
        await stripe_webhooks.stripe_webhook(request)

    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_invalid_signature(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")

    request = make_request(
        {"id": "evt_003"},
        "invalid_signature",
    )

    with pytest.raises(HTTPException) as error:
        await stripe_webhooks.stripe_webhook(request)

    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_duplicate_webhook_event(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")

    event = make_event(
        "evt_duplicate",
        "checkout.session.completed",
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = (
        MagicMock()
    )

    monkeypatch.setattr(stripe_webhooks, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        stripe_webhooks.stripe.Webhook,
        "construct_event",
        lambda **kwargs: event,
    )

    request = make_request({"id": "evt_duplicate"}, "test_signature")
    result = await stripe_webhooks.stripe_webhook(request)

    assert result["received"] is True
    assert result["duplicate"] is True
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.close.assert_called_once()


@pytest.mark.asyncio
async def test_subscription_created(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setenv("STRIPE_LOCAL_TEST_MODE", "true")

    event = make_event(
        "evt_upgrade",
        "customer.subscription.created",
        {
            "id": "sub_test_001",
            "status": "active",
            "metadata": {
                "tenant_id": "1",
                "plan_name": "Pro",
            },
        },
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    update_mock = MagicMock()

    monkeypatch.setattr(stripe_webhooks, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        stripe_webhooks,
        "update_subscription",
        update_mock,
    )
    monkeypatch.setattr(
        stripe_webhooks.stripe.Webhook,
        "construct_event",
        lambda **kwargs: event,
    )

    request = make_request({"id": "evt_upgrade"}, "test_signature")
    result = await stripe_webhooks.stripe_webhook(request)

    assert result["duplicate"] is False
    update_mock.assert_called_once_with(
        db=db,
        tenant_id=1,
        plan_name="Pro",
        stripe_subscription_id="sub_test_001",
        status="active",
    )
    db.commit.assert_called_once()
    db.close.assert_called_once()


@pytest.mark.asyncio
async def test_subscription_canceled(monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setenv("STRIPE_LOCAL_TEST_MODE", "true")

    event = make_event(
        "evt_cancel",
        "customer.subscription.deleted",
        {"id": "sub_test_001"},
    )

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    cancel_mock = MagicMock()

    monkeypatch.setattr(stripe_webhooks, "SessionLocal", lambda: db)
    monkeypatch.setattr(
        stripe_webhooks,
        "cancel_subscription",
        cancel_mock,
    )
    monkeypatch.setattr(
        stripe_webhooks.stripe.Webhook,
        "construct_event",
        lambda **kwargs: event,
    )

    request = make_request({"id": "evt_cancel"}, "test_signature")
    result = await stripe_webhooks.stripe_webhook(request)

    assert result["duplicate"] is False
    cancel_mock.assert_called_once_with(
        db=db,
        stripe_subscription_id="sub_test_001",
    )
    db.commit.assert_called_once()
    db.close.assert_called_once()