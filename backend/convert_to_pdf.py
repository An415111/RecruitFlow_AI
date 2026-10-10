import json
import os
import html
from pypdf import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab_resume_maker import generate_resume_pdf

def build_pdf():
    optimized_path = "optimized_resume.txt"
    output_pdf = "resumes/Resumes.pdf"
    
    with open(optimized_path, "r", encoding="utf-8") as f:
        resume_data = json.load(f)
        
    name = resume_data.get("name", "").lower()
    
    # Identify the base PDF
    base_pdf_path = None
    if "anoushika" in name:
        base_pdf_path = "resumes/anoushika_base.pdf"
    elif "rushi" in name:
        base_pdf_path = "resumes/rushi_base.pdf"
        
    if base_pdf_path and os.path.exists(base_pdf_path):
        print(f"Using default base PDF resume directly: {base_pdf_path}")
        
        # Read the job description
        jd_text = ""
        if os.path.exists("job_description.txt"):
            with open("job_description.txt", "r", encoding="utf-8") as f:
                jd_text = f.read().strip()
                
        if jd_text:
            # Generate a temporary PDF with just the job description in 6pt white font
            temp_jd_pdf = "temp_jd.pdf"
            doc = SimpleDocTemplate(
                temp_jd_pdf,
                rightMargin=25,
                leftMargin=25,
                topMargin=20,
                bottomMargin=20
            )
            styles = getSampleStyleSheet()
            jd_style = ParagraphStyle(
                "JDStyle",
                parent=styles["Normal"],
                fontSize=6,
                leading=7,
                textColor=colors.HexColor("#FFFFFF"),
                spaceBefore=0,
                spaceAfter=0
            )
            # Escape HTML/XML entities and replace newlines with <br/>
            jd_html = html.escape(jd_text).replace("\n", "<br/>")
            content = [Paragraph(jd_html, jd_style)]
            doc.build(content)
            
            # Merge the base PDF and the temporary JD PDF
            writer = PdfWriter()
            
            # Add pages from base PDF
            reader_base = PdfReader(base_pdf_path)
            for page in reader_base.pages:
                writer.add_page(page)
                
            # Add the JD page(s)
            reader_jd = PdfReader(temp_jd_pdf)
            for page in reader_jd.pages:
                writer.add_page(page)
            
            # Save the merged PDF
            os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
            with open(output_pdf, "wb") as out_f:
                writer.write(out_f)
                
            # Clean up temp file
            if os.path.exists(temp_jd_pdf):
                try:
                    os.remove(temp_jd_pdf)
                except Exception:
                    pass
                
            print("Successfully merged default resume with job description and saved to resumes/Resumes.pdf")
        else:
            # Just copy the base PDF if no JD is found
            print("No job description found. Copying base PDF directly.")
            import shutil
            os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
            shutil.copy2(base_pdf_path, output_pdf)
    else:
        # Fallback to standard PDF generator if no base PDF matches or exists
        print("No matching default base PDF found. Generating using reportlab_resume_maker...")
        generate_resume_pdf(resume_data, output_pdf)
        
    print("PDF Created Successfully")

if __name__ == "__main__":
    build_pdf()