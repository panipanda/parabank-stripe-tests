from decimal import Decimal

import pytest
import requests
from conftest import BASE_URL, TIMEOUT
from helpers import (
    HEADERS,
    get_balance,
    get_transactions,
    new_transactions,
)


def post(path, **params):
    return requests.post(f"{BASE_URL}{path}", params=params, headers=HEADERS, timeout=TIMEOUT)


def test_transfer_above_balance_keeps_total(account_pair):
    # TC-11: transfer 0.01 above the balance of A; the overdraft rule is unknown,
    # so only check that both sides and the history stay consistent
    a, b = account_pair["a"], account_pair["b"]
    balance_a = get_balance(a)
    balance_b = get_balance(b)
    amount = balance_a + Decimal("0.01")

    response = post("/transfer", fromAccountId=a, toAccountId=b, amount=str(amount))

    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}: {response.text}"
    )
    assert get_balance(a) == balance_a - amount, (
        f"Expected balance A {balance_a - amount}, got {get_balance(a)}"
    )
    assert get_balance(b) == balance_b + amount, (
        f"Expected balance B {balance_b + amount}, got {get_balance(b)}"
    )


@pytest.mark.xfail(strict=True, reason="TC-12: service accepts a negative transfer amount")
def test_transfer_negative_amount_is_rejected(account_pair):
    # TC-12: transfer -5 is expected to be rejected without changing balances and history
    a, b = account_pair["a"], account_pair["b"]
    balance_a = get_balance(a)
    balance_b = get_balance(b)
    history_a = get_transactions(a)
    history_b = get_transactions(b)

    response = post("/transfer", fromAccountId=a, toAccountId=b, amount="-5")

    assert response.status_code >= 400, (
        f"Expected an error status for amount -5, got {response.status_code}: {response.text}"
    )
    assert get_balance(a) == balance_a, f"Expected balance A {balance_a}, got {get_balance(a)}"
    assert get_balance(b) == balance_b, f"Expected balance B {balance_b}, got {get_balance(b)}"
    assert not new_transactions(history_a, get_transactions(a)), "Expected no new transactions on A"
    assert not new_transactions(history_b, get_transactions(b)), "Expected no new transactions on B"


def test_transfer_zero_keeps_balances(account_pair):
    # TC-13: transfer 0 must not change balances
    a, b = account_pair["a"], account_pair["b"]
    balance_a = get_balance(a)
    balance_b = get_balance(b)

    post("/transfer", fromAccountId=a, toAccountId=b, amount="0")

    assert get_balance(a) == balance_a, f"Expected balance A {balance_a}, got {get_balance(a)}"
    assert get_balance(b) == balance_b, f"Expected balance B {balance_b}, got {get_balance(b)}"


def test_transfer_to_same_account_keeps_balance(account_pair):
    # TC-15: transfer A -> A must not change the balance of A
    a = account_pair["a"]
    balance_a = get_balance(a)

    post("/transfer", fromAccountId=a, toAccountId=a, amount="10.00")

    assert get_balance(a) == balance_a, f"Expected balance A {balance_a}, got {get_balance(a)}"


def test_transfer_non_numeric_amount_changes_nothing(account_pair):
    # TC-16: transfer amount=abc must not change balances and history
    a, b = account_pair["a"], account_pair["b"]
    balance_a = get_balance(a)
    balance_b = get_balance(b)
    history_a = get_transactions(a)
    history_b = get_transactions(b)

    response = post("/transfer", fromAccountId=a, toAccountId=b, amount="abc")

    assert response.status_code >= 400, (
        f"Expected an error status for amount 'abc', got {response.status_code}: {response.text}"
    )
    assert get_balance(a) == balance_a, f"Expected balance A {balance_a}, got {get_balance(a)}"
    assert get_balance(b) == balance_b, f"Expected balance B {balance_b}, got {get_balance(b)}"
    assert not new_transactions(history_a, get_transactions(a)), "Expected no new transactions on A"
    assert not new_transactions(history_b, get_transactions(b)), "Expected no new transactions on B"


@pytest.mark.xfail(strict=True, reason="TC-19: service accepts a negative deposit amount")
def test_deposit_negative_amount_is_rejected(account_pair):
    # TC-19: deposit -50 is expected to be rejected without changing balance and history
    a = account_pair["a"]
    balance_a = get_balance(a)
    history_a = get_transactions(a)

    response = post("/deposit", accountId=a, amount="-50")

    assert response.status_code >= 400, (
        f"Expected an error status for amount -50, got {response.status_code}: {response.text}"
    )
    assert get_balance(a) == balance_a, f"Expected balance A {balance_a}, got {get_balance(a)}"
    assert not new_transactions(history_a, get_transactions(a)), "Expected no new transactions on A"
