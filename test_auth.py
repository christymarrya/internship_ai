import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_auth_flow():
    # Unique email for testing
    ts = int(time.time())
    email = f"test_{ts}@example.com"
    password = "testpassword123"
    name = "Test User"

    print(f"--- Testing Signup with {email} ---")
    signup_payload = {
        "name": name,
        "email": email,
        "password": password
    }
    r1 = requests.post(f"{BASE_URL}/signup", json=signup_payload)
    if r1.status_code == 201:
        print("SUCCESS: User registered.")
    else:
        print(f"FAILED: {r1.status_code} - {r1.text}")
        return

    print("\n--- Testing Login ---")
    login_payload = {
        "email": email,
        "password": password
    }
    r2 = requests.post(f"{BASE_URL}/login", json=login_payload)
    if r2.status_code == 200:
        token_data = r2.json()
        token = token_data["access_token"]
        print("SUCCESS: Token received.")
        # print(f"Token: {token[:20]}...")
    else:
        print(f"FAILED: {r2.status_code} - {r2.text}")
        return

    print("\n--- Testing Signup with Duplicate Email ---")
    r3 = requests.post(f"{BASE_URL}/signup", json=signup_payload)
    if r3.status_code == 400:
        print("SUCCESS: Duplicate email blocked.")
    else:
        print(f"FAILED: Expected 400, got {r3.status_code}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_auth_flow()
