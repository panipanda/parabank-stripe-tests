import re

from playwright.sync_api import Page, expect

from helpers.api import rest_login
from helpers.data import PASSWORD, new_username, registration_form
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


def test_registration_rejects_different_passwords(page: Page):
    # TC-04: different Password and Confirm -> validation error on the form,
    # no success message and no customer is created (login with either password fails)
    username = new_username()
    different_password = "Different1"

    submit_registration(page, registration_form(username, repeated_password=different_password))

    expect(page.locator('[id="repeatedPassword.errors"]')).to_have_text("Passwords did not match.")
    expect(page).to_have_url(re.compile(r"/register\.htm"))
    expect(page.locator("#rightPanel")).not_to_contain_text("Your account was created")

    for password in (PASSWORD, different_password):
        response = rest_login(username, password)
        assert response.status_code == 400, (
            f"Expected login of the rejected user {username} to fail with 400, "
            f"got {response.status_code}"
        )


def test_registration_rejects_taken_username(page: Page, new_user):
    # TC-05: registering an existing username with other data is rejected,
    # the original customer and credentials stay unchanged
    other_password = "Other1234"

    submit_registration(page, registration_form(new_user["username"], other_password))

    expect(page.locator('[id="customer.username.errors"]')).to_have_text(
        "This username already exists."
    )
    expect(page).to_have_url(re.compile(r"/register\.htm"))
    expect(page.locator("#rightPanel")).not_to_contain_text("Your account was created")

    original = rest_login(new_user["username"], new_user["password"])
    assert original.status_code == 200, (
        f"Expected the original credentials to still work, got {original.status_code}"
    )
    assert original.json()["id"] == new_user["customer_id"], (
        f"Expected customer id {new_user['customer_id']}, got {original.json()['id']}"
    )
    replaced = rest_login(new_user["username"], other_password)
    assert replaced.status_code == 400, (
        f"Expected the new password to be rejected with 400, got {replaced.status_code}"
    )
