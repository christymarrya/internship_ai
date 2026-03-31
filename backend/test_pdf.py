import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from app.utils.pdf_generator import generate_resume_pdf

test_md = """
# Test Resume
## Experience
**Bold Job** - 2025
* Bullet 1
* Bullet 2
"""

try:
    pdf_bytes = generate_resume_pdf(test_md)
    with open("test.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF generated successfully!")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
