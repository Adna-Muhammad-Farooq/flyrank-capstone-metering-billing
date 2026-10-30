# Usage Metering & Billing Engine

## Project Overview

This project is developed as part of the FlyRank Backend AI Engineering Capstone.

The Usage Metering & Billing Engine is a backend application built with Python and FastAPI. It records API usage, tracks AI token consumption, calculates usage costs, manages subscription plans, and checks monthly usage limits.

The project also includes Stripe webhook integration, local webhook simulation, and a monthly billing calculation job.

## Technologies Used

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Stripe Python SDK
- APScheduler
- Pytest

## Main Features

### 1. Usage Metering
The system records API requests and AI token usage for each tenant. It also calculates the cost of token consumption.

### 2. Subscription Plans
The system supports Free and Pro plans with different monthly API and token limits.

### 3. Quota Management
The application checks usage limits before accepting new usage events. Requests exceeding the allowed quota are rejected.

### 4. Idempotency
The system uses idempotency keys to help prevent duplicate usage records.

### 5. Stripe Webhooks
The application verifies Stripe webhook signatures and processes supported subscription events.

For development and testing, Stripe events are simulated locally using signed requests. No real payment processing has been completed.

### 6. Monthly Billing
The application calculates monthly usage costs from stored usage events.

### 7. Billing Scheduler
APScheduler runs a scheduled job to calculate usage totals for the previous month.

The current implementation produces billing reports in the application output. It does not create or send real invoices.

### 8. Automated Testing
The project includes automated tests for pricing, metering, subscription webhook handling, billing calculations, scheduling, and checkout configuration.

## Project Structure

```text
metering-billing-engine/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── metering.py
│   ├── pricing.py
│   ├── subscription_service.py
│   ├── stripe_webhooks.py
│   ├── stripe_checkout.py
│   ├── billing_jobs.py
│   └── scheduler.py
├── migrations/
├── scripts/
│   └── test_stripe_webhook.py
├── tests/
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

## Local Setup

### 1. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```


### 2. Install Dependencies

After activating the Python virtual environment, install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

All required Python packages and their versions are listed in `requirements.txt`.


### 3. Configure Environment Variables

Create a `.env` file with your local database configuration and Stripe development settings.

Never commit real passwords or API secrets to GitHub.

### 4. Apply Database Migrations

```powershell
alembic upgrade head
```

### 5. Start the FastAPI Server

```powershell
uvicorn app.main:app --reload
```

Open the API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application root |
| GET | `/health` | Health check |
| POST | `/usage` | Record API and token usage |
| GET | `/usage` | View usage and quota information |
| POST | `/webhooks/stripe` | Receive and verify Stripe webhooks |
| POST | `/billing/checkout` | Create a Stripe checkout session when configured |

## Run Automated Tests

```powershell
python -m pytest tests/ -v
```

## Run the Monthly Billing Scheduler

```powershell
python -m app.scheduler
```

The scheduler runs separately from the FastAPI server.

## Important Limitations

This project is a capstone implementation, not a production-ready billing platform.

- Stripe subscription events have been tested through local simulation.
- Real payments and checkout have not been verified.
- Monthly billing reports are not stored as invoices.
- Production authentication, authorization, and billing reconciliation still need to be implemented.

## Conclusion

This project helped me gain practical experience with backend API development, PostgreSQL, usage tracking, subscription management, Stripe webhook handling, automated testing, and scheduled background jobs.

It demonstrates how a backend application can track service usage and calculate billing costs for different subscription plans.