import hashlib
import hmac
import json
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

secret = os.getenv("STRIPE_WEBHOOK_SECRET")

if not secret:
    raise RuntimeError("STRIPE_WEBHOOK_SECRET is missing")

event = {
    "id": "evt_local_cancel_001",
    "object": "event",
    "type": "customer.subscription.deleted",
    "data": {
        "object": {
            "id": "sub_local_pro_001",
            "object": "subscription",
            "status": "canceled",
            "metadata": {
                "tenant_id": "1"
            }
        }
    }
}
payload = json.dumps(event, separators=(",", ":"))
timestamp = int(time.time())

signature = hmac.new(
    secret.encode(),
    f"{timestamp}.{payload}".encode(),
    hashlib.sha256
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "Stripe-Signature": f"t={timestamp},v1={signature}"
}

response = requests.post(
    "http://127.0.0.1:8000/webhooks/stripe",
    data=payload,
    headers=headers,
    timeout=10
)

print("Status code:", response.status_code)
print("Response:", response.text)