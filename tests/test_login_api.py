import requests

BASE_URL = "https://parabank.parasoft.com/parabank/services/bank"
headers = {
        "Accept": "application/json"}

def test_login_success(new_user):
    response = requests.get(f"{BASE_URL}/login/{new_user['username']}/{new_user['password']}", headers=headers, timeout=10)
    response_json = response.json()
    assert response.status_code == 200, f"Login failed: {response.status_code} {response.text}"
    assert response_json["id"] == new_user["customer_id"], f"Expected customer ID {new_user['customer_id']}, got {response_json['id']}"