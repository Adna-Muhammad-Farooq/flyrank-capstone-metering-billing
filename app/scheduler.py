from datetime import datetime, timezone

from apscheduler.schedulers.blocking import BlockingScheduler

from app.billing_jobs import run_monthly_billing_job


def process_previous_month():
    """Calculate billing reports for the previous month."""

    now = datetime.now(timezone.utc)

    if now.month == 1:
        year = now.year - 1
        month = 12
    else:
        year = now.year
        month = now.month - 1

    reports = run_monthly_billing_job(year, month)

    print(f"Monthly billing reports for {year}-{month:02d}")

    for report in reports:
        print(report)


def start_scheduler():
    scheduler = BlockingScheduler(timezone="UTC")

    scheduler.add_job(
        process_previous_month,
        trigger="cron",
        day=1,
        hour=0,
        minute=5,
        id="monthly_billing",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )

    print("Monthly billing scheduler started.")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()