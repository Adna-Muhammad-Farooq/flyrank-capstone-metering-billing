from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.metering import duplicate_response


def test_duplicate_usage_returns_original_event():
    event = SimpleNamespace(
        id=10,
        tenant_id=1,
        usage_type="api_call",
        quantity=1,
        cost_micro_usd=0,
        input_tokens=0,
        output_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0,
    )

    request = SimpleNamespace(
        tenant_id=1,
        usage_type="api_call",
        quantity=1,
        input_tokens=0,
        output_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0,
    )

    result = duplicate_response(event, request, 0)

    assert result["message"] == "Usage recorded successfully"
    assert result["usage_event_id"] == 10
    assert result["cost_micro_usd"] == 0


def test_duplicate_with_different_quantity_rejected():
    event = SimpleNamespace(
        id=10,
        tenant_id=1,
        usage_type="api_call",
        quantity=1,
        cost_micro_usd=0,
        input_tokens=0,
        output_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0,
    )

    request = SimpleNamespace(
        tenant_id=1,
        usage_type="api_call",
        quantity=2,
        input_tokens=0,
        output_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0,
    )

    with pytest.raises(HTTPException) as error:
        duplicate_response(event, request, 0)

    assert error.value.status_code == 409

from unittest.mock import MagicMock

from app.metering import check_quota


def test_no_active_subscription():
    db = MagicMock()

    # Simulate no active subscription
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as error:
        check_quota(
            db=db,
            tenant_id=1,
            usage_type="api_call",
            quantity=1,
        )

    assert error.value.status_code == 402

def test_monthly_quota_exceeded():
    db = MagicMock()

    # Simulate an active subscription
    subscription = SimpleNamespace(
        plan_id=1,
        status="active"
    )

    # Free plan allows 1,000 API calls
    plan = SimpleNamespace(
        name="Free",
        api_call_limit=1000,
        token_limit=100000
    )

    # Customer already used 999 API calls
    used_calls = 999

    db.query.return_value.filter.return_value.first.side_effect = [
        subscription,
        plan
    ]

    db.query.return_value.filter.return_value.scalar.return_value = used_calls

    # Customer requests 2 more calls, exceeding the limit
    with pytest.raises(HTTPException) as error:
        check_quota(
            db=db,
            tenant_id=1,
            usage_type="api_call",
            quantity=2,
        )

    assert error.value.status_code == 429
    assert error.value.detail["limit"] == 1000
    assert error.value.detail["used"] == 999
    assert error.value.detail["requested"] == 2

def make_quota_db(used, plan=None, subscription=None):
    """Create a fake database for quota testing."""
    db = MagicMock()

    if subscription is None:
        subscription = SimpleNamespace(
            plan_id=1,
            status="active"
        )

    if plan is None:
        plan = SimpleNamespace(
            name="Free",
            api_call_limit=1000,
            token_limit=100000
        )

    db.query.return_value.filter.return_value.first.side_effect = [
        subscription,
        plan
    ]

    db.query.return_value.filter.return_value.scalar.return_value = used

    return db


# Step 107: Exact quota limit should be allowed
def test_exact_quota_limit_allowed():
    db = make_quota_db(used=999)

    check_quota(
        db=db,
        tenant_id=1,
        usage_type="api_call",
        quantity=1
    )


# Step 108: AI token quota exceeded
def test_ai_token_quota_exceeded():
    db = make_quota_db(used=99999)

    with pytest.raises(HTTPException) as error:
        check_quota(
            db=db,
            tenant_id=1,
            usage_type="ai_tokens",
            quantity=2
        )

    assert error.value.status_code == 429
    assert error.value.detail["limit"] == 100000
    assert error.value.detail["used"] == 99999


# Step 109: Invalid usage type
def test_invalid_usage_type():
    db = MagicMock()

    with pytest.raises(HTTPException) as error:
        check_quota(
            db=db,
            tenant_id=1,
            usage_type="invalid_type",
            quantity=1
        )

    assert error.value.status_code == 422


# Step 110: Subscription plan not found
def test_subscription_plan_not_found():
    db = MagicMock()

    subscription = SimpleNamespace(
        plan_id=999,
        status="active"
    )

    db.query.return_value.filter.return_value.first.side_effect = [
        subscription,
        None
    ]

    with pytest.raises(HTTPException) as error:
        check_quota(
            db=db,
            tenant_id=1,
            usage_type="api_call",
            quantity=1
        )

    assert error.value.status_code == 404


# Step 111: Duplicate key with different token cost
def test_duplicate_with_different_token_cost():
    event = SimpleNamespace(
        id=20,
        tenant_id=1,
        usage_type="ai_tokens",
        quantity=100,
        cost_micro_usd=100,
        input_tokens=100,
        output_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0
    )

    request = SimpleNamespace(
        tenant_id=1,
        usage_type="ai_tokens",
        quantity=100,
        input_tokens=100,
        output_tokens=0,
        cached_tokens=0,
        reasoning_tokens=0
    )

    with pytest.raises(HTTPException) as error:
        duplicate_response(
            event,
            request,
            cost_micro_usd=200
        )

    assert error.value.status_code == 409