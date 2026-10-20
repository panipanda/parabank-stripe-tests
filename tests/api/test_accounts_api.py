from decimal import Decimal, InvalidOperation

import pytest
import requests

from config import BASE_URL
from helpers.api import find_missing_account_id, get_json

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
    assert accounts, f"Expected at least one account for customer {new_user['customer_id']}"
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


def test_create_savings_account(new_user):
    # TC-07: a created SAVINGS account is consistent in the creation reply,
    # in GET /accounts/{id} and in the customer's account list.
    # The balance is not checked: the initial funding rule is not documented.
    customer_id = new_user["customer_id"]
    accounts = get_json(f"/customers/{customer_id}/accounts")
    funding_account_id = accounts[0]["id"]

    response = requests.post(
        f"{BASE_URL}/createAccount",
        params={
            "customerId": customer_id,
            "newAccountType": 1,
            "fromAccountId": funding_account_id,
        },
        headers=headers,
        timeout=10,
    )
    assert response.status_code == 200, (
        f"Expected status 200 for account creation, got {response.status_code}: {response.text}"
    )
    created = response.json()
    new_id = created["id"]
    assert new_id != funding_account_id, (
        f"Expected a new account id, got the funding account id {new_id}"
    )
    assert created["type"] == "SAVINGS", f"Expected type='SAVINGS', got {created['type']!r}"
    assert created["customerId"] == customer_id, (
        f"Expected customerId={customer_id}, got {created['customerId']!r}"
    )

    fetched = get_json(f"/accounts/{new_id}")
    assert fetched["type"] == "SAVINGS", f"GET: expected type='SAVINGS', got {fetched['type']!r}"
    assert fetched["customerId"] == customer_id, (
        f"GET: expected customerId={customer_id}, got {fetched['customerId']!r}"
    )

    listed = [a for a in get_json(f"/customers/{customer_id}/accounts") if a["id"] == new_id]
    assert len(listed) == 1, f"Expected account {new_id} once in the list, got {len(listed)}"
    assert listed[0]["type"] == "SAVINGS", (
        f"List: expected type='SAVINGS', got {listed[0]['type']!r}"
    )
    assert listed[0]["customerId"] == customer_id, (
        f"List: expected customerId={customer_id}, got {listed[0]['customerId']!r}"
    )


def test_get_missing_account():
    # TC-08: GET of a confirmed missing account -> 400 with a "could not find" message
    # and no customer data in the body
    missing_id = find_missing_account_id()

    response = requests.get(f"{BASE_URL}/accounts/{missing_id}", headers=headers, timeout=10)

    assert response.status_code == 400, (
        f"Expected status 400 for missing account {missing_id}, got {response.status_code}"
    )
    assert "Could not find account" in response.text, (
        f"Expected a 'could not find' message, got {response.text!r}"
    )
    assert "customerId" not in response.text, (
        f"Expected no account data in the error body, got {response.text!r}"
    )
