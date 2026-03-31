import requests
from bs4 import BeautifulSoup

url = "https://internshala.com/internships/software-development-internships/"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

internships = []
# Internshala typically wraps job cards in a div with class 'internship_meta' or 'container-fluid'
job_cards = soup.find_all("div", class_="container-fluid")

for card in job_cards[:5]:
    try:
        title_elem = card.find("h3", class_="job-internship-name")
        company_elem = card.find("p", class_="company-name")
        location_elem = card.find("div", class_="row-1-item locations")
        
        if title_elem and company_elem:
            title = title_elem.text.strip()
            company = company_elem.text.strip()
            print(f"Found: {title} at {company}")
    except Exception as e:
        print("Error parsing a card:", e)

if not job_cards:
    print("No job cards found. The class names might be different.")
