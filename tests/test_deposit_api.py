from decimal import Decimal

import requests

BASE_URL = "https://parabank.parasoft.com/parabank/services/bank"
headers = {"Accept": "application/json"}


def test_deposit(new_user):
    # TC-18: deposit 50.00 -> balance grows by exactly 50.00,
    # exactly one new Credit transaction with the right amount and accountId
    amount = Decimal("50.00")

    response = requests.get(
        f"{BASE_URL}/customers/{new_user['customer_id']}/accounts",
        headers=headers,
        timeout=10,
    )
    assert response.status_code == 200, (
        f"Expected status 200 for accounts request, got {response.status_code}"
    )
    accounts = response.json()
    assert accounts, f"Expected at least one account for customer {new_user['customer_id']}"
    account_id = accounts[0]["id"]

    account_response = requests.get(
        f"{BASE_URL}/accounts/{account_id}",
        headers=headers,
        timeout=10,
    )
    assert account_response.status_code == 200, (
        f"Expected status 200 for account request, got {account_response.status_code}"
    )
    balance_before = account_response.json(parse_float=Decimal)["balance"]

    transactions_response = requests.get(
        f"{BASE_URL}/accounts/{account_id}/transactions",
        headers=headers,
        timeout=10,
    )
    assert transactions_response.status_code == 200, (
        f"Expected status 200 for transactions request, got {transactions_response.status_code}"
    )
    transactions_before = transactions_response.json(parse_float=Decimal)

    deposit_response = requests.post(
        f"{BASE_URL}/deposit",
        params={"accountId": account_id, "amount": str(amount)},
        headers=headers,
        timeout=10,
    )
    assert deposit_response.status_code == 200, (
        f"Expected status 200 for deposit request, got {deposit_response.status_code}"
    )

    account_response = requests.get(
        f"{BASE_URL}/accounts/{account_id}",
        headers=headers,
        timeout=10,
    )
    assert account_response.status_code == 200, (
        f"Expected status 200 for account request, got {account_response.status_code}"
    )
    balance_after = account_response.json(parse_float=Decimal)["balance"]

    transactions_response = requests.get(
        f"{BASE_URL}/accounts/{account_id}/transactions",
        headers=headers,
        timeout=10,
    )
    assert transactions_response.status_code == 200, (
        f"Expected status 200 for transactions request, got {transactions_response.status_code}"
    )
    transactions_after = transactions_response.json(parse_float=Decimal)

    expected_balance = balance_before + amount
    assert balance_after == expected_balance, (
        f"Expected balance_after={expected_balance}, got balance_after={balance_after} "
        f"(balance_before={balance_before}, amount={amount})"
    )
    assert len(transactions_after) == len(transactions_before) + 1, (
        f"Expected transaction count {len(transactions_before) + 1}, "
        f"got {len(transactions_after)} (before={len(transactions_before)})"
    )
    transaction_ids_before = {transaction["id"] for transaction in transactions_before}
    new_transactions = [
        transaction
        for transaction in transactions_after
        if transaction["id"] not in transaction_ids_before
    ]
    assert len(new_transactions) == 1, (
        f"Expected exactly one transaction with a new id, got {len(new_transactions)}"
    )
    new_transaction = new_transactions[0]
    assert new_transaction["type"] == "Credit", (
        f"Expected transaction type='Credit', got type={new_transaction['type']!r}"
    )
    assert new_transaction["amount"] == amount, (
        f"Expected transaction amount={amount}, got amount={new_transaction['amount']!r}"
    )
    assert new_transaction["accountId"] == account_id, (
        f"Expected transaction accountId={account_id}, "
        f"got accountId={new_transaction['accountId']!r}"
    )
