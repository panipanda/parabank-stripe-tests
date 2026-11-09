from playwright.sync_api import Page

from config import SITE_URL


def submit_registration(page: Page, form):
    """Open the registration page, fill every field of `form` and press Register."""
    page.goto(f"{SITE_URL}/register.htm")
    for field_name, value in form.items():
        # names contain dots, so an attribute selector is used instead of "#id"
        page.locator(f'[id="{field_name}"]').fill(value)
    page.get_by_role("button", name="Register").click()


def log_in(page: Page, username, password):
    """Log in through the home page form."""
    page.goto(f"{SITE_URL}/index.htm")
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    page.get_by_role("button", name="Log In").click()
