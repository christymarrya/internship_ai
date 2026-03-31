import requests
import json

base_url = "http://localhost:8000/api/v1/auth"
email = "test2@example.com"
password = "password"

# 1. Signup
print("--- SIGNUP ---")
res = requests.post(f"{base_url}/signup", json={"name": "Test User", "email": email, "password": password})
print(res.status_code, res.text)

# 2. Login
print("--- LOGIN ---")
res = requests.post(f"{base_url}/login", json={"email": email, "password": password})
print(res.status_code, res.text)
