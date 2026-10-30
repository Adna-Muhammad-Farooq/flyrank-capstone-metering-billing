from datetime import datetime, timezone
from unittest.mock import patch

from app import scheduler


def test_previous_month_billing():
    fake_now = datetime(2026, 10, 30, tzinfo=timezone.utc)

    with patch("app.scheduler.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now

        with patch(
            "app.scheduler.run_monthly_billing_job",
            return_value=[],
        ) as mock_job:
            scheduler.process_previous_month()

    mock_job.assert_called_once_with(2026, 9)


def test_previous_month_in_january():
    fake_now = datetime(2027, 1, 1, tzinfo=timezone.utc)

    with patch("app.scheduler.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now

        with patch(
            "app.scheduler.run_monthly_billing_job",
            return_value=[],
        ) as mock_job:
            scheduler.process_previous_month()

    mock_job.assert_called_once_with(2026, 12)