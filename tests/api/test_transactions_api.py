from decimal import Decimal

from helpers import get_json, get_transactions, new_transactions, post_money


def test_search_transactions_by_amount(new_user):
    # TC-20: search by amount returns every known transaction of that amount
    # and none of another amount
    account_id = get_json(f"/customers/{new_user['customer_id']}/accounts")[0]["id"]
    target_amount = Decimal("100.00")
    other_amount = Decimal("50.00")

    history_before = get_transactions(account_id)
    post_money("/deposit", accountId=account_id, amount=str(target_amount))
    history_after_target = get_transactions(account_id)
    post_money("/deposit", accountId=account_id, amount=str(other_amount))
    history_after_other = get_transactions(account_id)

    target_new = new_transactions(history_before, history_after_target)
    other_new = new_transactions(history_after_target, history_after_other)
    assert len(target_new) == 1, f"Expected one new {target_amount} transaction, got {len(target_new)}"
    assert len(other_new) == 1, f"Expected one new {other_amount} transaction, got {len(other_new)}"
    target_ids = {transaction["id"] for transaction in target_new}
    other_id = other_new[0]["id"]

    found = get_json(f"/accounts/{account_id}/transactions/amount/{target_amount}")

    assert found, f"Expected a non-empty result for amount {target_amount}"
    found_ids = {transaction["id"] for transaction in found}
    assert target_ids <= found_ids, (
        f"Expected result to contain {target_ids}, got ids {found_ids}"
    )
    assert other_id not in found_ids, (
        f"Expected transaction {other_id} ({other_amount}) to be absent, got ids {found_ids}"
    )
    wrong_amounts = [t["amount"] for t in found if t["amount"] != target_amount]
    assert not wrong_amounts, f"Expected all amounts to be {target_amount}, got {wrong_amounts}"
