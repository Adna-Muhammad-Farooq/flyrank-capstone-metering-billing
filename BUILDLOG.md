# Build Log — Usage Metering & Billing Engine

## Project Information

**Track:** FlyRank Backend AI Engineering  
**Project:** Usage Metering & Billing Engine  
**Type:** Capstone

## Phase 1 — Project Setup

I started by creating a Python virtual environment and setting up a FastAPI backend.

I installed the required libraries and connected the application to a local PostgreSQL database.

I used SQLAlchemy for database operations and Alembic for database migrations.

## Phase 2 — Database Development

I created database models for:

- Tenants
- Subscription plans
- Subscriptions
- Usage events
- Stripe webhook events

I also created and applied database migrations.

## Phase 3 — Usage Metering

I implemented an API endpoint to record usage events.

The system tracks API calls and AI token consumption. It calculates token usage costs and stores the results in PostgreSQL.

I also implemented idempotency checks to help prevent duplicate usage records.

## Phase 4 — Subscription and Quota Management

I added Free and Pro subscription plans with different monthly usage limits.

The application checks usage quotas before accepting new events.

It rejects usage requests when the monthly quota is exceeded or when the subscription is not active.

## Phase 5 — Stripe Webhook Integration

I implemented a Stripe webhook endpoint with signature verification.

I tested subscription creation and cancellation using locally simulated signed webhook events.

I also implemented webhook event deduplication.

Real Stripe payments were not tested.

## Phase 6 — Monthly Billing

I developed a billing service that calculates monthly usage costs.

I added an APScheduler job to calculate billing totals for the previous month.

The current scheduler prints billing reports rather than creating persistent invoices.

## Phase 7 — Automated Testing

I created automated tests for the main backend functionality.

I ran the following command:

```powershell
python -m pytest tests/ -q
```

**Result: 30 passed in 0.99 seconds.**

## Phase 8 — Git Version Control

I initialized a Git repository and configured `.gitignore` to exclude private environment files, the virtual environment, and Python cache files.

I checked the staged files for exposed credentials before preparing the project for GitHub.

## Challenges and Solutions

**Challenge 1: Preventing duplicate usage records**

I implemented idempotency keys and database checks.

**Challenge 2: Managing monthly usage limits**

I added quota validation using stored usage events.

**Challenge 3: Testing Stripe without real payments**

I used locally generated webhook events with valid signatures to test supported subscription events.

**Challenge 4: Automating monthly billing**

I used APScheduler to run the previous month's billing calculation on a schedule.

## Current Limitations

- Real Stripe payments have not been verified.
- The billing scheduler does not create persistent invoices.
- Production authentication and authorization are not implemented.
- The application has not been verified in a production deployment.

## AI Assistance and Learning

### How I Used AI

I used ChatGPT as a learning and development assistant during this capstone.

AI helped me understand backend concepts, plan the project structure, write and review Python code, understand database models, and develop automated tests.

I also used AI to understand Stripe webhook signatures, idempotency, quota enforcement, and monthly billing calculations.

### Problems and Corrections

During development, I faced problems with the Stripe webhook implementation. At one point, test code was accidentally placed inside the webhook application file. I corrected the file and ran the tests again.

I also reviewed the Git repository before committing files to avoid exposing private database passwords and Stripe configuration.

### What I Learned

I learned that AI-generated code must be checked carefully. I cannot assume that code is correct just because it was suggested by AI.

I used terminal commands, automated tests, and manual API testing to check the implementation.

The project passed 30 automated tests, but real Stripe payments and production deployment have not been verified.

### My Contribution

I worked on the project setup, database configuration, API development, testing, debugging, and documentation with AI assistance.

I reviewed the implementation and used test results to check whether the main features worked.

## Conclusion

This capstone helped me improve my practical skills in Python, FastAPI, PostgreSQL, SQLAlchemy, Stripe webhooks, automated testing, and backend billing logic.

I developed a working local backend implementation and verified its main features through automated tests.