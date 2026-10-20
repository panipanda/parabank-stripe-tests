# QA bank and payments tests

Demo project for test automation with Python, pytest and Playwright.

The system under test is [ParaBank](https://parabank.parasoft.com/parabank), a public demo bank. Payments are covered with the [Stripe](https://docs.stripe.com/api) API in test mode.

## Status

Work in progress. Currently implemented:

- `new_user` fixture: registers a fresh customer for every test
- `account_pair` fixture: two different accounts (checking and savings) of a new customer
- API tests (`tests/`):
  - TC-02, TC-03: login with valid and wrong credentials
  - TC-06, TC-07, TC-08: account list, savings account creation, missing account
  - TC-09, TC-14: transfer between own accounts, transfer to a missing account
  - TC-18: deposit updates balance and history
  - TC-20: search transactions by amount
  - TC-11, TC-12, TC-13, TC-15, TC-16, TC-19: amount rules for transfers and deposits (TC-12 and TC-19 are marked xfail)
- Stripe API tests (`tests/test_stripe_api.py`, test mode only):
  - card payment is created and confirmed
  - the same idempotency key does not create a second payment
  - partial refund is recorded on the charge
- UI tests (`tests/ui/`, Playwright):
  - TC-01: registration and opening Accounts Overview
  - TC-17: transfer in the UI, balances checked in the UI and in the API

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

The tests call a shared public demo service, so network or service outages can cause failures that are not test bugs. Every test creates its own user and does not touch other people's data.

## Stripe key

Copy `.env.example` to `.env` and set `STRIPE_SECRET_KEY` to a test key (`sk_test_...`). Without it the Stripe tests are skipped; live keys (`sk_live_...`) are never used. `.env` is git-ignored.
