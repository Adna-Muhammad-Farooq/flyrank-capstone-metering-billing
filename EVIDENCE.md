# Evidence — Usage Metering & Billing Engine

## 1. Project Information

**Project:** Usage Metering & Billing Engine  
**Track:** FlyRank Backend AI Engineering  
**Project Type:** Capstone

## 2. Features Implemented

The backend includes:

- API usage recording
- AI token usage and cost calculation
- Free and Pro subscription plans
- Monthly quota enforcement
- Idempotency handling
- PostgreSQL database integration
- Alembic database migrations
- Stripe webhook signature verification
- Local subscription creation and cancellation simulation
- Monthly billing calculations
- Scheduled monthly billing reports
- Automated tests

## 3. API Testing

The FastAPI application provides interactive API documentation through Swagger UI.

**Local URL:** `http://127.0.0.1:8000/docs`

The application includes endpoints for recording usage, viewing usage information, receiving Stripe webhooks, and creating checkout sessions when configured.

## 4. Database Evidence

PostgreSQL is used to store tenant, plan, subscription, usage event, and webhook event information.

Alembic migrations manage database schema changes.

## 5. Stripe Webhook Testing

Stripe subscription events were simulated locally using signed webhook requests.

The implementation verifies webhook signatures and handles supported subscription creation and cancellation events.

No real Stripe payment transaction was performed.

## 6. Monthly Billing Evidence

The billing service calculates monthly costs from recorded usage events.

The scheduler calculates the previous month's usage totals and prints billing reports.

The current implementation does not generate real Stripe invoices.

## 7. Automated Test Results

Command:
python -m pytest tests/ -q

Result:
30 passed in 0.99s

Status: PASSED

All 30 automated tests completed successfully.

**Final test result:** To be added after the complete test suite is run.

## 8. Verification Status

The capstone includes local development and testing functionality.

Production payment processing, persistent invoices, and deployment have not been verified.

## 9. Additional Evidence

Add the following before final submission:

- Final automated test results
- API response examples
- Database migration verification
- GitHub repository URL
