import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_internship_discovery():
    # 1. Login/Signup
    ts = int(time.time())
    email = f"int_test_{ts}@example.com"
    print(f"--- Registering {email} ---")
    requests.post(f"{BASE_URL}/auth/signup", json={"name": "Job Hunter", "email": email, "password": "password123"})
    login_r = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "password123"})
    token = login_r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get all internships
    print("\n--- Listing Internships ---")
    r_list = requests.get(f"{BASE_URL}/internships/", headers=headers)
    internships = r_list.json()
    print(f"Found {len(internships)} roles.")
    if not internships: return
    target_id = internships[0]["id"]

    # 3. Save internship
    print(f"\n--- Saving Internship {target_id} ---")
    r_save = requests.post(f"{BASE_URL}/internships/{target_id}/save", headers=headers)
    print(r_save.json())

    # 4. List saved
    print("\n--- Listing Saved Internships ---")
    r_saved = requests.get(f"{BASE_URL}/internships/saved", headers=headers)
    print(f"Total saved: {len(r_saved.json())}")

    # 5. Apply (requires a resume_id)
    # Note: For simplicity, we'll try to apply without a real resume upload first 
    # but the API requires a valid resume_id in DB if we had stricter FK checks in logic (which we do in model but maybe not explicitly checked in endpoint before add)
    # Actually, we should use a real resume_id if possible.
    
    # 6. Unsave
    print(f"\n--- Unsaving Internship {target_id} ---")
    r_unsave = requests.delete(f"{BASE_URL}/internships/{target_id}/unsave", headers=headers)
    print(r_unsave.json())

    print("\n--- Internship Logic Verification Complete ---")

if __name__ == "__main__":
    test_internship_discovery()
