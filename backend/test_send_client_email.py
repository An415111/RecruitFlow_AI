import os
import sys

# Add backend directory to Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from emailer.gmail_sender import send_email
from emailer.templates import generate_email

def test_send_client():
    # Rushi details formatted matching templates expectations
    candidate_details = """Candidate Name: Sai Rushi Kasyap
Email: rushimukkamala5@gmail.com
Phone: +1 (346)-646-8149
Location: Monroe, Michigan (Relocating)
LinkedIn: https://www.linkedin.com/in/rushi-mukkamala
Open to Relocate: yes
Work Authorization: STEM OPT
Availability: immediate
Total Experience: not mentioned
"""

    job_description = """
Financial Analyst / Assistant Controller

We are seeking a Financial Analyst/Assistant Controller. The ideal candidate will have experience in general ledger accounting, financial statement preparation, and GAAP compliance. Proficiency in Excel (VBA) and Sage Intacct is highly desired.
"""

    print("Generating outreach email for Sai Rushi Kasyap...")
    body = generate_email(
        candidate_name="Sai Rushi Kasyap",
        recruiter_name="Recruiter", # Resolves to "Tech Recruiter" in templates.py
        role="Assistant Controller",
        linkedin_post_url="https://www.linkedin.com/jobs/view/987654",
        candidate_details=candidate_details,
        job_description=job_description
    )

    import emailer.templates as templates
    print("\n========== GENERATED OUTREACH EMAIL ==========")
    print(f"Subject: {templates.LAST_GENERATED_SUBJECT}")
    print(body)
    print("==============================================\n")

    test_receiver = "ankitgupta37937@gmail.com"
    subject = "Submission for Assistant Controller - Sai Rushi Kasyap"

    resume_pdf_path = os.path.join(CURRENT_DIR, "resumes", "Resumes.pdf")
    if not os.path.exists(resume_pdf_path):
        resume_pdf_path = os.path.join(CURRENT_DIR, "Ankit_Gupta_Resume.pdf")
        if not os.path.exists(resume_pdf_path):
            resume_pdf_path = None

    print(f"Sending test email to: {test_receiver}...")
    send_email(
        receiver=test_receiver,
        subject=subject,
        body=body,
        resume_path=resume_pdf_path
    )
    print("Test email sent successfully!")

if __name__ == "__main__":
    test_send_client()
