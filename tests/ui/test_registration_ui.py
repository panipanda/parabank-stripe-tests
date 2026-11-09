import re

from playwright.sync_api import Page, expect

from helpers.data import new_username, registration_form
from helpers.ui import submit_registration


def test_register_and_open_accounts_overview(page: Page):
    # TC-01: registering with unique data shows the welcome page for this user
    # and the new session can open Accounts Overview with at least one account
    username = new_username()

    submit_registration(page, registration_form(username))

    right_panel = page.locator("#rightPanel")
    expect(right_panel).to_contain_text(f"Welcome {username}")
    expect(right_panel).to_contain_text("Your account was created successfully")

    page.get_by_role("link", name="Accounts Overview").click()

    expect(page).to_have_url(re.compile(r"/overview\.htm"))
    expect(right_panel.get_by_role("heading", name="Accounts Overview")).to_be_visible()
    account_links = right_panel.locator("#accountTable tbody tr a")
    expect(account_links.first).to_be_visible()
