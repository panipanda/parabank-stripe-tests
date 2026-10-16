import uuid

import pytest
import requests

SITE_URL = "https://parabank.parasoft.com/parabank"
BASE_URL = f"{SITE_URL}/services/bank"
TIMEOUT = 10


@pytest.fixture
def new_user():
    """Регистрирует нового клиента ParaBank и возвращает его данные."""
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
        # GET нужен, чтобы сервер выдал сессионные cookies до отправки формы
        session.get(f"{SITE_URL}/register.htm", timeout=TIMEOUT)
        response = session.post(f"{SITE_URL}/register.htm", data=form, timeout=TIMEOUT)
        assert response.status_code == 200, f"Регистрация не удалась: {response.status_code}"
        assert "Your account was created successfully" in response.text, (
            f"Нет сообщения об успешной регистрации для {username}"
        )

    # ID клиента узнаём через REST-логин, сравнивать будем именно его
    login = requests.get(
        f"{BASE_URL}/login/{username}/{password}",
        headers={"Accept": "application/json"},
        timeout=TIMEOUT,
    )
    assert login.status_code == 200, f"Логин после регистрации: {login.status_code} {login.text}"

    return {"username": username, "password": password, "customer_id": login.json()["id"]}
