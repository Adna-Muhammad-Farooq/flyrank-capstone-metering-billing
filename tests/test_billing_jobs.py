from unittest.mock import MagicMock

from app.billing_jobs import calculate_monthly_bill


def test_monthly_bill_calculation():
    db = MagicMock()

    # Simulate 2,500,000 microdollars ($2.50)
    db.query.return_value.filter.return_value.scalar.return_value = 2_500_000

    result = calculate_monthly_bill(
        db=db,
        tenant_id=1,
        year=2026,
        month=10,
    )

    assert result["tenant_id"] == 1
    assert result["year"] == 2026
    assert result["month"] == 10
    assert result["total_cost_micro_usd"] == 2_500_000
    assert result["total_cost_usd"] == "2.500000"

from types import SimpleNamespace

from app import billing_jobs


def test_run_monthly_billing_job(monkeypatch):
    db = MagicMock()

    # Simulate two customers
    db.query.return_value.all.return_value = [
        SimpleNamespace(id=1),
        SimpleNamespace(id=2),
    ]

    monkeypatch.setattr(
        billing_jobs,
        "SessionLocal",
        lambda: db,
    )

    def fake_calculate(db, tenant_id, year, month):
        return {
            "tenant_id": tenant_id,
            "year": year,
            "month": month,
            "total_cost_micro_usd": 1000,
            "total_cost_usd": "0.001000",
        }

    monkeypatch.setattr(
        billing_jobs,
        "calculate_monthly_bill",
        fake_calculate,
    )

    results = billing_jobs.run_monthly_billing_job(
        year=2026,
        month=10,
    )

    assert len(results) == 2
    assert results[0]["tenant_id"] == 1
    assert results[1]["tenant_id"] == 2

    db.close.assert_called_once()