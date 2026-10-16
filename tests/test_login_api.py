import requests
import json

BASE_URL = "https://parabank.parasoft.com/parabank/services/bank"

# login + password: parapanda Passw0rd

userLogin = "parapanda"
userPassword = "Passw0rd"

headers = {
    "Accept": "application/json"}
response = requests.get(f"{BASE_URL}/login/{userLogin}/{userPassword}", headers=headers, timeout=10)
response_json = response.json()
print(response.status_code)
print(json.dumps(response_json))