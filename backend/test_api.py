from apify_client import ApifyClient

# Uses the same key as config.py
API_KEY = "your-apify-api-key"

client = ApifyClient(API_KEY)

# Quick connectivity test — list your available actors
print("Testing Apify connection...")
try:
    user_client = client.user("me")
    user_data = user_client.get()
    if user_data:
        print(f"Connected! Username: {user_data.get('username', 'N/A')}")
    else:
        print("Error: Could not fetch user info. Check your API key.")
except Exception as e:
    print(f"Error: {e}")