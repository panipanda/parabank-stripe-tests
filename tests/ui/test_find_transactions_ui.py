from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from playwright.sync_api import Page, expect

from helpers.api import get_json, get_transactions, post_money
from helpers.ui import log_in

DESCRIPTION = "Deposit via Web Service"
DEPOSITS = [Decimal("100.00"), Decimal("50.00"), Decimal("100.00")]


@pytest.fixture
def account_with_deposits(new_user):
    """Make known deposits on the customer's account and return its id and full history."""
    account_id = get_json(f"/customers/{new_user['customer_id']}/accounts")[0]["id"]
    for amount in DEPOSITS:
        post_money("/deposit", accountId=account_id, amount=str(amount))
    return {"account_id": account_id, "history": get_transactions(account_id)}


def transaction_day(transaction):
    """Return the calendar day of a transaction.

    ParaBank stores the date as midnight UTC, so the day is read in UTC, not in local time.
    """
    return datetime.fromtimestamp(transaction["date"] / 1000, tz=UTC).date()


def day_text(day):
    """Format a day the way the Find Transactions page expects and shows it (MM-DD-YYYY)."""
    return day.strftime("%m-%d-%Y")


def open_find_transactions(page: Page, account_id):
    """Open the Find Transactions page of a logged-in user and select the account.

    Opening the page again before every search hides the previous result, so a result on
    screen always belongs to the search that was just made.
    """
    page.get_by_role("link", name="Find Transactions").click()
    page.locator("#accountId").select_option(str(account_id))


def test_find_transactions_by_amount_in_ui(page: Page, new_user, account_with_deposits):
    # TC-21: searching by amount 100.00 shows exactly the 100.00 deposits of the account
    # (counted from the API history) and none of the 50.00 deposit
    account_id = account_with_deposits["account_id"]
    searched = Decimal("100.00")
    expected = [t for t in account_with_deposits["history"] if t["amount"] == searched]
    assert len(expected) == 2, f"Expected two {searched} transactions in the history: {expected}"

    log_in(page, new_user["username"], new_user["password"])
    open_find_transactions(page, account_id)
    page.locator("#amount").fill(str(searched))
    page.locator("#findByAmount").click()

    rows = page.locator("#transactionBody tr")
    expect(rows).to_have_count(len(expected))
    for row in rows.all():
        expect(row).to_contain_text(DESCRIPTION)
        expect(row).to_contain_text(f"${searched}")
    expect(rows.filter(has_text="$50.00")).to_have_count(0)


def test_find_transactions_by_date_in_ui(page: Page, new_user, account_with_deposits):
    # TC-21: searching by the date taken from the created transactions shows all of them,
    # searching by the previous day shows none of them
    account_id = account_with_deposits["account_id"]
    history = account_with_deposits["history"]
    day = transaction_day(history[0])
    expected = [t for t in history if transaction_day(t) == day]
    assert len(expected) == len(DEPOSITS), f"Expected all deposits on {day}, got {expected}"

    log_in(page, new_user["username"], new_user["password"])
    open_find_transactions(page, account_id)
    page.locator("#transactionDate").fill(day_text(day))
    page.locator("#findByDate").click()

    rows = page.locator("#transactionBody tr")
    expect(rows).to_have_count(len(expected))
    expect(rows.filter(has_text=day_text(day))).to_have_count(len(expected))
    expect(rows.filter(has_text="$100.00")).to_have_count(2)
    expect(rows.filter(has_text="$50.00")).to_have_count(1)

    open_find_transactions(page, account_id)
    page.locator("#transactionDate").fill(day_text(day - timedelta(days=1)))
    page.locator("#findByDate").click()

    # With no match the page still shows a result table, so wait for it to appear
    # and then check that none of the real deposits is listed
    expect(page.locator("#resultContainer")).to_be_visible()
    expect(rows.filter(has_text=DESCRIPTION)).to_have_count(0)
