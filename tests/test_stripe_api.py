import os
import uuid
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

STRIPE_URL = "https://api.stripe.com/v1"
TIMEOUT = 10
AMOUNT = 2000


@pytest.fixture
def stripe_auth():
    key = os.getenv("STRIPE_SECRET_KEY", "")
    if not key.startswith("sk_test_"):
        pytest.skip("STRIPE_SECRET_KEY with a test key (sk_test_...) is not set in .env")
    return (key, "")


def create_payment(auth, idempotency_key):
    """Create and confirm a test card payment of AMOUNT cents."""
    return requests.post(
        f"{STRIPE_URL}/payment_intents",
        auth=auth,
        headers={"Idempotency-Key": idempotency_key},
        data={
            "amount": AMOUNT,
            "currency": "usd",
            "payment_method": "pm_card_visa",
            "confirm": "true",
            "automatic_payment_methods[enabled]": "true",
            "automatic_payment_methods[allow_redirects]": "never",
        },
        timeout=TIMEOUT,
    )


def test_payment_is_confirmed(stripe_auth):
    # Stripe 1: a test card payment is created and confirmed in one request
    response = create_payment(stripe_auth, str(uuid.uuid4()))

    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}: {response.text}"
    )
    payment = response.json()
    assert payment["status"] == "succeeded", f"Expected status 'succeeded', got {payment['status']!r}"
    assert payment["amount"] == AMOUNT, f"Expected amount {AMOUNT}, got {payment['amount']}"
    assert payment["amount_received"] == AMOUNT, (
        f"Expected amount_received {AMOUNT}, got {payment['amount_received']}"
    )
    assert payment["currency"] == "usd", f"Expected currency 'usd', got {payment['currency']!r}"


def test_same_idempotency_key_does_not_create_second_payment(stripe_auth):
    # Stripe 2: a repeated request with the same Idempotency-Key returns the same payment
    key = str(uuid.uuid4())

    first = create_payment(stripe_auth, key)
    second = create_payment(stripe_auth, key)

    assert first.status_code == 200, f"First request: got {first.status_code}: {first.text}"
    assert second.status_code == 200, f"Second request: got {second.status_code}: {second.text}"
    assert second.json()["id"] == first.json()["id"], (
        f"Expected the same payment id, got {first.json()['id']} and {second.json()['id']}"
    )
    assert second.headers.get("Idempotent-Replayed") == "true", (
        f"Expected the second reply to be a replay, got header "
        f"{second.headers.get('Idempotent-Replayed')!r}"
    )


def test_partial_refund(stripe_auth):
    # Stripe 3: a partial refund is recorded on the charge and the payment stays succeeded
    refund_amount = 500
    payment = create_payment(stripe_auth, str(uuid.uuid4())).json()
    assert payment["status"] == "succeeded", f"Payment not ready: status {payment['status']!r}"

    refund = requests.post(
        f"{STRIPE_URL}/refunds",
        auth=stripe_auth,
        data={"payment_intent": payment["id"], "amount": refund_amount},
        timeout=TIMEOUT,
    )

    assert refund.status_code == 200, f"Expected status 200, got {refund.status_code}: {refund.text}"
    assert refund.json()["amount"] == refund_amount, (
        f"Expected refund amount {refund_amount}, got {refund.json()['amount']}"
    )
    after = requests.get(
        f"{STRIPE_URL}/payment_intents/{payment['id']}",
        auth=stripe_auth,
        params={"expand[]": "latest_charge"},
        timeout=TIMEOUT,
    ).json()
    charge = after["latest_charge"]
    assert charge["amount_refunded"] == refund_amount, (
        f"Expected amount_refunded {refund_amount}, got {charge['amount_refunded']}"
    )
    assert charge["refunded"] is False, "Expected the charge to be refunded only partially"
    assert after["status"] == "succeeded", f"Expected status 'succeeded', got {after['status']!r}"
