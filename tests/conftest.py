import uuid

import pytest
import requests

from config import BASE_URL, SITE_URL, TIMEOUT


@pytest.fixture
def new_user():
    """Register a new ParaBank customer and return their data."""
    username = f"qa_{uuid.uuid4().hex[:12]}"
    password = "Passw0rd"

    form = {
        "customer.firstName": "Test",
        "customer.lastName": "User",
        "customer.address.street": "1 Test Street",
        "customer.address.city": "Testville",
        "customer.address.state": "TS",
        "customer.address.zipCode": "12345",
        "customer.phoneNumber": "5550100",
        "customer.ssn": "123-45-6789",
        "customer.username": username,
        "customer.password": password,
        "repeatedPassword": password,
    }

    with requests.Session() as session:
        # GET first so the server issues session cookies before the form is sent
        session.get(f"{SITE_URL}/register.htm", timeout=TIMEOUT)
        response = session.post(f"{SITE_URL}/register.htm", data=form, timeout=TIMEOUT)
        assert response.status_code == 200, f"Registration failed: {response.status_code}"
        assert "Your account was created successfully" in response.text, (
            f"No success message after registering {username}"
        )

    # Get the customer ID via REST login; tests compare against this value
    login = requests.get(
        f"{BASE_URL}/login/{username}/{password}",
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert login.status_code == 200, f"Login after registration: {login.status_code} {login.text}"

    return {"username": username, "password": password, "customer_id": login.json()["id"]}


@pytest.fixture
def account_pair(new_user):
    """Return two different accounts (A checking, B savings) of a new customer."""
    customer_id = new_user["customer_id"]
    headers = {"Accept": "application/json"}

    accounts = requests.get(
        f"{BASE_URL}/customers/{customer_id}/accounts", headers=headers, timeout=TIMEOUT
    )
    assert accounts.status_code == 200, f"Accounts request failed: {accounts.status_code}"
    account_a = accounts.json()[0]["id"]

    created = requests.post(
        f"{BASE_URL}/createAccount",
        params={"customerId": customer_id, "newAccountType": 1, "fromAccountId": account_a},
        headers=headers,
        timeout=TIMEOUT,
    )
    assert created.status_code == 200, f"Account creation failed: {created.status_code}"
    account_b = created.json()["id"]

    assert account_a != account_b, f"Expected two different accounts, got {account_a} twice"
    return {"customer_id": customer_id, "a": account_a, "b": account_b}
