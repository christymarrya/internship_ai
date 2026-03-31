import asyncio
import httpx
from fpdf import FPDF
import os

def create_sample_pdf(filename, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

async def test_matching_pipeline():
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
    pdf_filename = "match_test.pdf"
    create_sample_pdf(pdf_filename, resume_text)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Upload
        print(f"Uploading {pdf_filename}...")
        with open(pdf_filename, "rb") as f:
            files = {"file": (pdf_filename, f, "application/pdf")}
            r1 = await client.post("http://localhost:8000/api/v1/resume/upload", files=files)
            if r1.status_code != 201:
                print(f"FAILED UPLOAD: {r1.status_code} - {r1.text}")
                return
            
            resume_id = r1.json()["resume_id"]
            print(f"SUCCESS: Resume Parsed. ID: {resume_id}")

        # Step 2: Match
        print("Testing Semantic Match Engine...")
        payload = {
            "resume_id": resume_id,
            "job_description": "Wanted: Senior field operative with expertise in combat, negotiation, and international espionage. Must be comfortable with high-stakes environments."
        }
        r2 = await client.post("http://localhost:8000/api/v1/match/", json=payload, timeout=180.0)
        
        if r2.status_code != 200:
            print(f"FAILED MATCH: {r2.status_code} - {r2.text}")
        else:
            match_data = r2.json()
            print("\n================ SEMANTIC MATCH RESULT ================\n")
            print(f"Score: {match_data['match_score']}% ({match_data['match_label']})")
            print(f"Recommendation: {match_data['recommendation']}")
            print(f"Matched Skills: {', '.join(match_data['matched_skills'])}")
            print(f"Missing Skills: {', '.join(match_data['missing_skills'])}")
            print("\n========================================================\n")

    # Cleanup
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

if __name__ == "__main__":
    asyncio.run(test_matching_pipeline())
