import uuid

import pytest
import requests

SITE_URL = "https://parabank.parasoft.com/parabank"
BASE_URL = f"{SITE_URL}/services/bank"
TIMEOUT = 10


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
