from fpdf import FPDF
import markdown_it
from app.core.logger import get_logger
import io

logger = get_logger(__name__)

class PDFGenerator(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('helvetica', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        # self.cell(30, 10, 'Tailored Resume', 1, 0, 'C')
        # Line break
        self.ln(10)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('helvetica', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def sanitize_text(text: str) -> str:
    """
    Replaces common Unicode characters that are not supported by standard PDF fonts
    with their ASCII equivalents.
    """
    replacements = {
        "\u2013": "-", # en-dash
        "\u2014": "--", # em-dash
        "\u2018": "'", # left single quote
        "\u2019": "'", # right single quote
        "\u201c": '"', # left double quote
        "\u201d": '"', # right double quote
        "\u2022": "*", # bullet
        "\u2026": "...", # ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Also handle some common latin-1 characters that might still cause issues if not encoded
    return text.encode("latin-1", "replace").decode("latin-1")

def generate_resume_pdf(markdown_text: str) -> bytes:
    """
    Converts markdown resume text into a professional PDF using fpdf2.
    Handles basic markdown formatting: headers, bold, italics, bullets.
    """
    # Sanitize the entire text first
    markdown_text = sanitize_text(markdown_text)
    
    pdf = PDFGenerator()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    # Simple markdown parsing (can be replaced with a more robust library if needed)
    lines = markdown_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        # Headers
        if line.startswith('###'):
            pdf.set_font("helvetica", 'B', 14)
            pdf.cell(0, 10, line.replace('###', '').strip(), ln=True)
            pdf.set_font("helvetica", size=11)
        elif line.startswith('##') or (line.startswith('**') and line.endswith('**')):
            pdf.set_font("helvetica", 'B', 16)
            pdf.cell(0, 10, line.replace('##', '').replace('**', '').strip(), ln=True)
            pdf.set_font("helvetica", size=11)
        elif line.startswith('#'):
            pdf.set_font("helvetica", 'B', 20)
            pdf.cell(0, 12, line.replace('#', '').strip(), ln=True, align='C')
            pdf.set_font("helvetica", size=11)
        elif line.startswith('---') or line.startswith('==='):
            pdf.line(pdf.get_x(), pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        elif (line.startswith('*') or line.startswith('-')) and len(line) > 1 and line[1] in (' ', '\t'):
            pdf.set_font("helvetica", size=11)
            pdf.set_x(15 + 5) # Margin + indentation
            clean_line = line[1:].strip().replace('**', '')
            # Truncate very long words to prevent multi_cell horizontal space error
            safe_words = [w if len(w) < 60 else w[:57] + "..." for w in clean_line.split()]
            pdf.multi_cell(0, 7, "- " + " ".join(safe_words))
        else:
            # Handle inline bolding (rough version)
            # This can be improved with a real markdown parser traversal
            pdf.set_font("helvetica", size=11)
            clean_line = line.replace('**', '')
            safe_words = [w if len(w) < 60 else w[:57] + "..." for w in clean_line.split()]
            pdf.multi_cell(0, 7, " ".join(safe_words))
            
    # Return PDF bytes
    return bytes(pdf.output())
