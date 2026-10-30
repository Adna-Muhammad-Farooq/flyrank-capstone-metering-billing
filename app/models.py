from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey, BigInteger, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    subscriptions = relationship("Subscription", back_populates="tenant")
    usage_events = relationship("UsageEvent", back_populates="tenant")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    api_call_limit = Column(Integer, nullable=False)
    token_limit = Column(BigInteger, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    status = Column(String(30), default="active")
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)

    tenant = relationship("Tenant", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    usage_type = Column(String(30), nullable=False)
    quantity = Column(BigInteger, nullable=False)
    idempotency_key = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Store AI usage cost in microdollars
    cost_micro_usd = Column(BigInteger, nullable=False, default=0)
    
    input_tokens = Column(BigInteger, nullable=False, default=0)
    output_tokens = Column(BigInteger, nullable=False, default=0)
    cached_tokens = Column(BigInteger, nullable=False, default=0)
    reasoning_tokens = Column(BigInteger, nullable=False, default=0)

    tenant = relationship("Tenant", back_populates="usage_events")

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_tenant_idempotency_key"
        ),
    )

class StripeWebhookEvent(Base):
    __tablename__ = "stripe_webhook_events"

    id = Column(Integer, primary_key=True, index=True)

    stripe_event_id = Column(
        String(255),
        unique=True,
        nullable=False
    )

    event_type = Column(String(100), nullable=False)

    processed_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )