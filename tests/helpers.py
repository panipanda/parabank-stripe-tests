import random
from decimal import Decimal

import requests

from conftest import BASE_URL, TIMEOUT

HEADERS = {"Accept": "application/json"}


def get_json(path):
    """GET a REST path, check for status 200 and return parsed JSON with exact Decimal amounts."""
    response = requests.get(f"{BASE_URL}{path}", headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, (
        f"Expected status 200 for GET {path}, got {response.status_code}: {response.text}"
    )
    return response.json(parse_float=Decimal)


def post_money(path, **params):
    """POST a money operation (query parameters), check for status 200 and return the text reply."""
    response = requests.post(f"{BASE_URL}{path}", params=params, headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 200, (
        f"Expected status 200 for POST {path}, got {response.status_code}: {response.text}"
    )
    return response.text


def get_balance(account_id):
    return get_json(f"/accounts/{account_id}")["balance"]


def get_transactions(account_id):
    return get_json(f"/accounts/{account_id}/transactions")


def new_transactions(before, after):
    """Return transactions from `after` whose id is not present in `before`."""
    ids_before = {transaction["id"] for transaction in before}
    return [transaction for transaction in after if transaction["id"] not in ids_before]


def find_missing_account_id():
    """Pick an account id that the service confirms does not exist (GET returns 400)."""
    for _ in range(10):
        candidate = random.randint(900_000_000, 999_999_999)
        response = requests.get(
            f"{BASE_URL}/accounts/{candidate}", headers=HEADERS, timeout=TIMEOUT
        )
        if response.status_code == 400:
            return candidate
    raise AssertionError("Could not find an account id confirmed as missing in 10 attempts")
