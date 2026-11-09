# QA bank and payments tests

Demo project for test automation with Python, pytest and Playwright.

The system under test is [ParaBank](https://parabank.parasoft.com/parabank), a public demo bank. Payments are covered with the [Stripe](https://docs.stripe.com/api) API in test mode.

## Status

31 tests: 29 pass and 2 are marked `xfail` on purpose (see below).

- `new_user` fixture: registers a fresh customer for every test
- `account_pair` fixture: two different accounts (checking and savings) of a new customer
- API tests (`tests/api/`):
  - TC-02, TC-03: login with valid and wrong credentials
  - TC-06, TC-07, TC-08: account list, savings account creation, missing account
  - TC-09, TC-10, TC-14: transfer between own accounts, transfer in the history of both accounts, transfer to a missing account
  - TC-18: deposit updates balance and history
  - TC-20: search transactions by amount
  - TC-22: loan is approved (new LOAN account, down payment taken) or denied (two denial cases)
  - TC-23: the same account as JSON and as XML has equal content
  - TC-11, TC-12, TC-13, TC-15, TC-16, TC-19: amount rules for transfers and deposits (TC-12 and TC-19 are marked xfail)
- Stripe API tests (`tests/api/test_stripe_api.py`, test mode only):
  - card payment is created and confirmed
  - the same idempotency key does not create a second payment
  - partial refund is recorded on the charge
  - declined card gives a card error
  - refund above the paid amount is rejected
- UI tests (`tests/ui/`, Playwright):
  - TC-01, TC-04, TC-05: registration, different passwords, taken username
  - TC-17: transfer in the UI, balances checked in the UI and in the API
  - TC-21: find transactions by amount and by date

### Notes on the results

- TC-12 and TC-19 are `xfail(strict=True)`: the service accepts a negative transfer or deposit amount. The rule "amount must be positive" is an expectation, not a published requirement.
- TC-22 uses a loan rule that was recorded from the public demo on 2026-11-09. It is not a published contract, so the test can fail if the demo settings change.
- Searching transactions in the UI with no match shows one broken row (`NaN-NaN-NaN undefined`). TC-21 only checks that no real transaction is listed in that case.

## Project layout

```
tests/api/    API tests (ParaBank REST, Stripe)
tests/ui/     UI tests (Playwright)
tests/conftest.py   shared fixtures: new_user, account_pair
helpers/      api.py (REST helpers), data.py (test data), ui.py (UI steps)
config.py     base URLs and timeout
.github/workflows/tests.yml   manual run in GitHub Actions
```

## Setup

Python 3.12. On Windows, from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

## Run

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

The tests call a shared public demo service, so network or service outages can cause failures that are not test bugs. Every test creates its own user and does not touch other people's data. ParaBank rate-limits (HTTP 429) when the whole suite is run many times in a few minutes: wait and run again.

## Stripe key

Copy `.env.example` to `.env` and set `STRIPE_SECRET_KEY` to a test key (`sk_test_...`). Without it the Stripe tests are skipped; live keys (`sk_live_...`) are never used. `.env` is git-ignored.

## GitHub Actions

The workflow `Tests` has two jobs:

- `lint` runs on every push and pull request: `ruff check`, `ruff format --check` and test collection (no network calls).
- `tests` runs the whole suite on Python 3.12 with Chromium, only when started by hand (Actions tab, Run workflow).

The full run is manual on purpose: ParaBank sits behind Cloudflare, which rate-limits fast clients, and runs from GitHub runners failed with HTTP 429 after about ten registrations (the same suite passes on a local machine). To run the Stripe tests there, add a test key as the repository secret `STRIPE_SECRET_KEY`; without it they are skipped.
