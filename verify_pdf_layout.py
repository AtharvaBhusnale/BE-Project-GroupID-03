from fpdf import FPDF
import os
from PIL import Image

# Create dummy images for testing
if not os.path.exists("test_orig.png"):
    img = Image.new('RGB', (200, 200), color = 'red')
    img.save('test_orig.png')
if not os.path.exists("test_enh.png"):
    img = Image.new('RGB', (800, 800), color = 'blue')
    img.save('test_enh.png')

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Medical Enhancement Report', 1, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_test_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Patient & Doctor Info
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Patient Name: John Doe", ln=True)
    pdf.cell(0, 8, f"Patient ID: 12345", ln=True)
    pdf.cell(0, 8, f"Doctor: Dr. Smith", ln=True)
    pdf.cell(0, 8, f"Date: 2023-10-27", ln=True)
    pdf.cell(0, 8, f"Enhancement Type: Real-ESRGAN 4x Upscale", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "MRI Scan Comparison", ln=True)
    pdf.ln(5)
    
    # Side-by-side Layout
    # Page width is usually 210mm. Margins default 10mm.
    # Printable width ~190mm.
    # We want 2 images. Let's give them 90mm each.
    
    y_start = pdf.get_y()
    
    # Left Image (Original)
    pdf.set_xy(10, y_start)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Original (Low-Res)", align='C')
    pdf.image("test_orig.png", x=15, y=y_start+10, w=80)
    
    # Right Image (Enhanced)
    pdf.set_xy(110, y_start)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(90, 10, "Enhanced (AI 4x)", align='C')
    pdf.image("test_enh.png", x=115, y=y_start+10, w=80)
    
    pdf.output("layout_test.pdf")
    print("PDF generated: layout_test.pdf")

if __name__ == "__main__":
    generate_test_pdf()
