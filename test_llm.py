import asyncio
import httpx
from fpdf import FPDF
import os
import time

def create_sample_pdf(filename, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

async def test_llm_pipeline():
    # 1. Create a real PDF file
    resume_text = """
James Bond
Secret Agent | MI6
London, UK | +44 20 7946 0958 | 007@mi6.gov.uk

EXPERIENCE:
MI6, London (2006 - Present)
- Operative 007: Completed numerous high-stakes international missions.
- Specialized in intelligence gathering, infiltration, and combat.
- Managed complex assignments independently under extreme pressure.

SKILLS:
Espionage, Marksmanship, Driving, Hand-to-hand combat, Multilingual, Negotiation.
"""
    pdf_filename = "sample_resume.pdf"
    create_sample_pdf(pdf_filename, resume_text)
    
    async with httpx.AsyncClient() as client:
        # Step 0: Auth
        ts = int(time.time())
        email = f"ai_test_{ts}@example.com"
        print(f"Registering test user: {email}...")
        signup_payload = {"name": "AI Tester", "email": email, "password": "password123"}
        await client.post("http://localhost:8000/api/v1/auth/signup", json=signup_payload)
        
        print("Logging in...")
        login_r = await client.post("http://localhost:8000/api/v1/auth/login", json={"email": email, "password": "password123"})
        token = login_r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Upload PDF
        print(f"Uploading {pdf_filename}...")
        with open(pdf_filename, "rb") as f:
            files = {"file": (pdf_filename, f, "application/pdf")}
            r1 = await client.post("http://localhost:8000/api/v1/resume/upload", files=files, headers=headers)
            if r1.status_code != 201:
                print(f"FAILED UPLOAD: {r1.status_code} - {r1.text}")
                return
            
            resume_id = r1.json()["resume_id"]
            print(f"SUCCESS: Resume Parsed. ID: {resume_id}")

        # Step 2: Generate Cover Letter
        print("Requesting AI Cover Letter...")
        payload = {
            "resume_id": resume_id,
            "job_description": "We are seeking a software engineer with experience in Python and AI.",
            "company_name": "Tech Corp",
            "job_title": "Senior Field Operative",
            "tone": "professional"
        }
        r2 = await client.post("http://localhost:8000/api/v1/cover-letter/generate-cover-letter", json=payload, timeout=300.0, headers=headers)
        
        if r2.status_code != 200:
            print(f"FAILED COVER LETTER: {r2.status_code} - {r2.text}")
        else:
            cl_data = r2.json()
            print("\n================ AI GENERATED COVER LETTER ================\n")
            print(cl_data["cover_letter"])
            print("\n===========================================================\n")

    # Cleanup
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

if __name__ == "__main__":
    asyncio.run(test_llm_pipeline())
