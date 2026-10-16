# QA bank and payments tests

A small demo project for practising test automation with Python, pytest and Playwright.

The system under test is [ParaBank](https://parabank.parasoft.com/parabank), a public demo bank. Stripe (test mode) is planned as a later step.

## Status

Work in progress. Currently implemented:

- `new_user` fixture: registers a fresh customer for every test
- TC-02: API login test (status 200 and exact customer ID)

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
