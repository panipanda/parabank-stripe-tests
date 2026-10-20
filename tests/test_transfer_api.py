from decimal import Decimal

import requests

from conftest import BASE_URL, TIMEOUT
from helpers import (
    HEADERS,
    find_missing_account_id,
    get_balance,
    get_transactions,
    new_transactions,
    post_money,
)


def test_transfer_between_own_accounts(account_pair):
    # TC-09: transfer 100.00 A -> B changes balances by exactly 100.00,
    # keeps the total, and adds one Debit (A) and one Credit (B) to the history
    account_a, account_b = account_pair["a"], account_pair["b"]
    amount = Decimal("100.00")

    balance_a_before = get_balance(account_a)
    balance_b_before = get_balance(account_b)
    history_a_before = get_transactions(account_a)
    history_b_before = get_transactions(account_b)

    post_money("/transfer", fromAccountId=account_a, toAccountId=account_b, amount=str(amount))

    balance_a_after = get_balance(account_a)
    balance_b_after = get_balance(account_b)
    new_a = new_transactions(history_a_before, get_transactions(account_a))
    new_b = new_transactions(history_b_before, get_transactions(account_b))

    assert balance_a_after == balance_a_before - amount, (
        f"Expected balance A {balance_a_before - amount}, got {balance_a_after} "
        f"(before={balance_a_before}, amount={amount})"
    )
    assert balance_b_after == balance_b_before + amount, (
        f"Expected balance B {balance_b_before + amount}, got {balance_b_after} "
        f"(before={balance_b_before}, amount={amount})"
    )
    assert balance_a_after + balance_b_after == balance_a_before + balance_b_before, (
        f"Expected total {balance_a_before + balance_b_before} to be preserved, "
        f"got {balance_a_after + balance_b_after}"
    )

    assert len(new_a) == 1, f"Expected exactly one new transaction on A, got {len(new_a)}"
    assert new_a[0]["type"] == "Debit", f"Expected type='Debit' on A, got {new_a[0]['type']!r}"
    assert new_a[0]["amount"] == amount, f"Expected amount={amount} on A, got {new_a[0]['amount']!r}"
    assert new_a[0]["accountId"] == account_a, (
        f"Expected accountId={account_a} on A, got {new_a[0]['accountId']!r}"
    )

    assert len(new_b) == 1, f"Expected exactly one new transaction on B, got {len(new_b)}"
    assert new_b[0]["type"] == "Credit", f"Expected type='Credit' on B, got {new_b[0]['type']!r}"
    assert new_b[0]["amount"] == amount, f"Expected amount={amount} on B, got {new_b[0]['amount']!r}"
    assert new_b[0]["accountId"] == account_b, (
        f"Expected accountId={account_b} on B, got {new_b[0]['accountId']!r}"
    )


def test_transfer_to_missing_account_is_rejected(account_pair):
    # TC-14: transfer to a confirmed missing account -> 400,
    # balance and transaction ids of A stay unchanged
    account_a = account_pair["a"]
    missing_id = find_missing_account_id()

    balance_before = get_balance(account_a)
    history_before = get_transactions(account_a)

    response = requests.post(
        f"{BASE_URL}/transfer",
        params={"fromAccountId": account_a, "toAccountId": missing_id, "amount": "10.00"},
        headers=HEADERS,
        timeout=TIMEOUT,
    )

    assert response.status_code == 400, (
        f"Expected status 400 for transfer to missing account {missing_id}, "
        f"got {response.status_code}: {response.text}"
    )
    balance_after = get_balance(account_a)
    assert balance_after == balance_before, (
        f"Expected balance A unchanged at {balance_before}, got {balance_after}"
    )
    history_after = get_transactions(account_a)
    assert not new_transactions(history_before, history_after), (
        f"Expected no new transactions on A, got {new_transactions(history_before, history_after)}"
    )
