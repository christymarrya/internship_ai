import requests
import json
import time

url = "http://localhost:8000/api/v1/cover-letter/generate-cover-letter"
payload = {
    "resume_id": "1c1259c7-eec8-4281-88c9-d0e6aaa2cc07",
    "job_description": "We are seeking a high-stakes intelligence operative for international missions.",
    "tone": "professional"
}

print("Sending request to AI Cover Letter Generator...")
start_time = time.time()
try:
    response = requests.post(url, json=payload, timeout=300)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    if response.status_code == 200:
        data = response.json()
        print("\nSUCCESS! COVER LETTER GENERATED:\n")
        print("-------------")
        print(data["cover_letter"])
        print("-------------")
    else:
        print(f"FAILED: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"ERROR: {e}")
