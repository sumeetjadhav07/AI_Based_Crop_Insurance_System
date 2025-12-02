# app/services/payment_stub.py
import uuid
from datetime import datetime

# This is a simple mock payment processor.
# Later you can replace this with Razorpay, Stripe, or UPI integration.

def process_payment(amount: float, user_id: str, policy_name: str):
    """
    Simulates a payment transaction.
    Always returns a 'success' result with a fake transaction ID.
    """
    transaction_id = f"txn_{uuid.uuid4().hex[:10]}"

    return {
        "status": "success",
        "transaction_id": transaction_id,
        "amount": amount,
        "user_id": user_id,
        "policy_name": policy_name,
        "timestamp": datetime.utcnow().isoformat()
    }
