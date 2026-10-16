from decimal import InvalidOperation, Decimal
import requests
import pytest

BASE_URL = "https://parabank.parasoft.com/parabank/services/bank"
headers = {"Accept": "application/json"}


def test_accounts_list(new_user):
    # TC-06: a new customer has a non-empty list of own accounts

    response = requests.get(
        f"{BASE_URL}/customers/{new_user['customer_id']}/accounts",
        headers=headers,
        timeout=10,
    )

    assert response.status_code == 200, (
        f"Expected status 200 for accounts request, got {response.status_code}"
    )
    accounts = response.json(parse_float=Decimal)
    assert isinstance(accounts, list), (
        f"Expected accounts to be a list, got {type(accounts).__name__}"
    )
    assert accounts, (
        f"Expected at least one account for customer {new_user['customer_id']}"
    )
    account_ids = [account["id"] for account in accounts]
    assert len(account_ids) == len(set(account_ids)), (
        f"Expected unique account IDs, got {account_ids}"
    )
    for account in accounts:
        assert account["customerId"] == new_user["customer_id"], (
            f"Account {account['id']}: expected customerId {new_user['customer_id']}, "
            f"got {account['customerId']}"
        )
        try:
            Decimal(account["balance"])
        except (InvalidOperation, TypeError):
            pytest.fail(
                f"Account {account['id']}: balance is not a valid amount, "
                f"got {account['balance']!r}"
            )
