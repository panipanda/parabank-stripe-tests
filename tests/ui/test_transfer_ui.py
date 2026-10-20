from decimal import Decimal

from playwright.sync_api import Page, expect

from config import SITE_URL
from helpers.api import get_balance


def money(value):
    """Format an amount the way ParaBank shows it, for example $365.50."""
    return f"${value:,.2f}"


def test_transfer_funds_in_ui(page: Page, new_user, account_pair):
    # TC-17: a 50.00 transfer made in the UI is shown in the UI and in the API,
    # A decreases by 50.00, B increases by 50.00, the total is preserved
    account_a, account_b = account_pair["a"], account_pair["b"]
    amount = Decimal("50.00")
    balance_a_before = get_balance(account_a)
    balance_b_before = get_balance(account_b)

    page.goto(f"{SITE_URL}/index.htm")
    page.locator('input[name="username"]').fill(new_user["username"])
    page.locator('input[name="password"]').fill(new_user["password"])
    page.get_by_role("button", name="Log In").click()
    page.get_by_role("link", name="Transfer Funds").click()

    page.locator("#amount").fill(str(amount))
    page.locator("#fromAccountId").select_option(str(account_a))
    page.locator("#toAccountId").select_option(str(account_b))
    page.get_by_role("button", name="Transfer").click()

    result = page.locator("#showResult")
    expect(result).to_contain_text("Transfer Complete!")
    expect(result).to_contain_text(
        f"{money(amount)} has been transferred from account #{account_a} to account #{account_b}"
    )

    page.get_by_role("link", name="Accounts Overview").click()
    row_a = page.locator("#accountTable tbody tr", has_text=str(account_a))
    row_b = page.locator("#accountTable tbody tr", has_text=str(account_b))
    expect(row_a).to_contain_text(money(balance_a_before - amount))
    expect(row_b).to_contain_text(money(balance_b_before + amount))

    balance_a_after = get_balance(account_a)
    balance_b_after = get_balance(account_b)
    assert balance_a_after == balance_a_before - amount, (
        f"Expected balance A {balance_a_before - amount}, got {balance_a_after}"
    )
    assert balance_b_after == balance_b_before + amount, (
        f"Expected balance B {balance_b_before + amount}, got {balance_b_after}"
    )
    assert balance_a_after + balance_b_after == balance_a_before + balance_b_before, (
        f"Expected total {balance_a_before + balance_b_before} to be preserved, "
        f"got {balance_a_after + balance_b_after}"
    )
