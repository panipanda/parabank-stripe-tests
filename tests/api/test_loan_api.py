import json
from decimal import Decimal

from helpers.api import get_balance, get_json, post_money

# TC-22: the loan rule below was recorded from the public demo on 2026-11-09, it is not a
# published contract. A new customer has a CHECKING account with a balance of about 515.50.
#   - 1000.00 loan with a 100.00 down payment is approved: a new LOAN account holds 1000.00
#     and the down payment is taken from the funding account
#   - a down payment above the funding balance is denied
#     (message error.insufficient.funds.for.down.payment)
#   - a 100000.00 loan is denied (message error.insufficient.funds)
LOAN_AMOUNT = Decimal("1000.00")
DOWN_PAYMENT = Decimal("100.00")


def request_loan(customer_id, funding_account_id, amount, down_payment):
    """Send requestLoan and return the parsed decision."""
    reply = post_money(
        "/requestLoan",
        customerId=customer_id,
        amount=str(amount),
        downPayment=str(down_payment),
        fromAccountId=funding_account_id,
    )
    return json.loads(reply)


def get_accounts(customer_id):
    return get_json(f"/customers/{customer_id}/accounts")


def test_loan_is_approved_and_creates_loan_account(new_user):
    # TC-22: an approved loan creates the customer's own LOAN account with the loan amount
    # and takes exactly the down payment from the funding account
    customer_id = new_user["customer_id"]
    funding_id = get_accounts(customer_id)[0]["id"]
    balance_before = get_balance(funding_id)

    decision = request_loan(customer_id, funding_id, LOAN_AMOUNT, DOWN_PAYMENT)

    assert decision["approved"] is True, f"Expected the loan to be approved, got {decision}"
    loan_id = decision["accountId"]
    assert loan_id is not None, f"Expected an account id in the decision, got {decision}"

    loan_accounts = [a for a in get_accounts(customer_id) if a["id"] == loan_id]
    assert len(loan_accounts) == 1, f"Expected account {loan_id} once in the list"
    loan_account = loan_accounts[0]
    assert loan_account["type"] == "LOAN", f"Expected type='LOAN', got {loan_account['type']!r}"
    assert loan_account["customerId"] == customer_id, (
        f"Expected customerId={customer_id}, got {loan_account['customerId']!r}"
    )
    assert loan_account["balance"] == LOAN_AMOUNT, (
        f"Expected loan balance {LOAN_AMOUNT}, got {loan_account['balance']}"
    )
    balance_after = get_balance(funding_id)
    assert balance_after == balance_before - DOWN_PAYMENT, (
        f"Expected funding balance {balance_before - DOWN_PAYMENT}, got {balance_after} "
        f"(before={balance_before}, down payment={DOWN_PAYMENT})"
    )


def check_loan_is_denied(customer_id, funding_id, amount, down_payment, expected_message):
    """Request a loan and check the denial and that nothing changed."""
    accounts_before = get_accounts(customer_id)
    balance_before = get_balance(funding_id)

    decision = request_loan(customer_id, funding_id, amount, down_payment)

    assert decision["approved"] is False, f"Expected the loan to be denied, got {decision}"
    assert decision["message"] == expected_message, (
        f"Expected message {expected_message!r}, got {decision['message']!r}"
    )
    assert decision["accountId"] is None, f"Expected no account id, got {decision['accountId']}"
    ids_before = [account["id"] for account in accounts_before]
    ids_after = [account["id"] for account in get_accounts(customer_id)]
    assert ids_after == ids_before, f"Expected accounts {ids_before}, got {ids_after}"
    balance_after = get_balance(funding_id)
    assert balance_after == balance_before, (
        f"Expected funding balance unchanged at {balance_before}, got {balance_after}"
    )


def test_loan_is_denied_when_down_payment_exceeds_balance(new_user):
    # TC-22: a down payment above the funding balance is denied, no account, no money moved
    customer_id = new_user["customer_id"]
    funding_id = get_accounts(customer_id)[0]["id"]
    too_much = get_balance(funding_id) + Decimal("100.00")

    check_loan_is_denied(
        customer_id,
        funding_id,
        LOAN_AMOUNT,
        too_much,
        "error.insufficient.funds.for.down.payment",
    )


def test_loan_is_denied_when_amount_is_too_large(new_user):
    # TC-22: a loan far above the customer's funds is denied, no account, no money moved
    customer_id = new_user["customer_id"]
    funding_id = get_accounts(customer_id)[0]["id"]

    check_loan_is_denied(
        customer_id,
        funding_id,
        Decimal("100000.00"),
        DOWN_PAYMENT,
        "error.insufficient.funds",
    )
