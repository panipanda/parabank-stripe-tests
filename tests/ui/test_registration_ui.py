import re
import uuid

from playwright.sync_api import Page, expect

from config import SITE_URL


def test_register_and_open_accounts_overview(page: Page):
    # TC-01: registering with unique data shows the welcome page for this user
    # and the new session can open Accounts Overview with at least one account
    username = f"qa_{uuid.uuid4().hex[:12]}"
    fields = {
        "customer.firstName": "Test",
        "customer.lastName": "User",
        "customer.address.street": "1 Test Street",
        "customer.address.city": "Testville",
        "customer.address.state": "TS",
        "customer.address.zipCode": "12345",
        "customer.phoneNumber": "5550100",
        "customer.ssn": "123-45-6789",
        "customer.username": username,
        "customer.password": "Passw0rd",
        "repeatedPassword": "Passw0rd",
    }

    page.goto(f"{SITE_URL}/register.htm")
    for field_id, value in fields.items():
        # ids contain dots, so an attribute selector is used instead of "#id"
        page.locator(f'[id="{field_id}"]').fill(value)
    page.get_by_role("button", name="Register").click()

    right_panel = page.locator("#rightPanel")
    expect(right_panel).to_contain_text(f"Welcome {username}")
    expect(right_panel).to_contain_text("Your account was created successfully")

    page.get_by_role("link", name="Accounts Overview").click()

    expect(page).to_have_url(re.compile(r"/overview\.htm"))
    expect(right_panel.get_by_role("heading", name="Accounts Overview")).to_be_visible()
    account_links = right_panel.locator("#accountTable tbody tr a")
    expect(account_links.first).to_be_visible()
