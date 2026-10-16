import requests

BASE_URL = "https://parabank.parasoft.com/parabank/services/bank"
headers = {
        "Accept": "application/json"}

def test_login_success(new_user):
    response = requests.get(f"{BASE_URL}/login/{new_user['username']}/{new_user['password']}", headers=headers, timeout=10)
    response_json = response.json()
    assert response.status_code == 200, f"Login failed: {response.status_code} {response.text}"
    assert response_json["id"] == new_user["customer_id"], f"Expected customer ID {new_user['customer_id']}, got {response_json['id']}"

def test_login_wrong_password(new_user):
    response = requests.get(f"{BASE_URL}/login/{new_user['username']}/wrongpassword", headers=headers, timeout=10)
    assert response.status_code == 400, f"Expected 400 Invalid username and/or password, got {response.status_code} {response.text}"
    assert "Invalid username and/or password" in response.text, f"Expected error message not found in response: {response.text}"
    assert new_user["password"] not in response.text, f"Password should not be in the error message: {response.text}"
    assert str(new_user["customer_id"]) not in response.text, f"Customer ID {new_user['customer_id']} should not be in the error message: {response.text}"