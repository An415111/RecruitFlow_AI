import os
import sys
import subprocess
import json
from emailer.gmail_sender import send_email
from emailer.templates import generate_email
from ai.resume_optimizer import optimize_resume

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def test_outreach():
    print("\n==================================================")
    print("RECRUITFLOW-AI: RUNNING OUTREACH TEST FOR RUSHI")
    print("==================================================")

    # 1. Load candidate profile
    profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
            client_profile = profiles["rushi"]
    except Exception as e:
        print(f"Error loading candidate_profiles.json: {e}")
        return

    # 2. Define a sample finance/accounting job description
    job_title = "Assistant Controller"
    recruiter_name = "Sarah Connor"
    recruiter_url = "https://www.linkedin.com/posts/sarah-connor-sample-finance-job"
    
    job_description = """
    Position: Assistant Controller
    Location: San Dimas, CA
    Type: Full-time
    
    Responsibilities:
    - Lead month-end and year-end close processes.
    - Prepare and review journal entries, reconciliations, and financial statements.
    - Oversee restricted fund and grant accounting compliance.
    - Work with external auditors and support audit readiness.
    
    Requirements:
    - Bachelor's or Master's in Accounting or Finance.
    - 5+ years of progressive accounting experience.
    - Proficiency in Sage Intacct, Sage 100, and advanced Excel.
    - Strong understanding of GAAP and internal controls.
    """

    print(f"\nTarget Job Role: {job_title}")
    print(f"Recruiter Name: {recruiter_name}")

    # 3. Format candidate details
    edu_list = client_profile.get("education", [])
    edu_str = ""
    for edu in edu_list:
        edu_str += f"\n- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('duration', '')})"
        if edu.get('cgpa'):
            edu_str += f" | GPA: {edu.get('cgpa', '')}"
    skills_str = ", ".join(client_profile.get("keywords", []))

    candidate_details = f"""Candidate Name: {client_profile.get('name', '')}
Email: {client_profile.get('email', '')}
Phone: {client_profile.get('phone', '')}
Location: {client_profile.get('location', '')}
LinkedIn: {client_profile.get('linkedin', '')}
Open to Relocate: {client_profile.get('open_to_relocate', 'yes')}
Work Authorization: {client_profile.get('work_auth', 'not mentioned')}
Availability: {client_profile.get('availability', 'immediate')}
Employer: {client_profile.get('employer', 'quinn@jpitstaffing.com')}
Employer Number: {client_profile.get('employer_number', '+1 5716265445')}
Education: {edu_str}
Key Skills/Keywords: {skills_str}"""

    # 4. Load base resume
    base_resume_file = client_profile.get("base_resume_file", "test_resume_rushi.txt")
    base_resume_path = os.path.join(BASE_DIR, base_resume_file)

    with open(base_resume_path, "r", encoding="utf-8") as f:
        base_resume = f.read()

    # 5. Optimize resume using LLM
    print("\nParsing Resume...")
    optimized_resume = optimize_resume(
        job_description,
        base_resume,
        candidate_profile=client_profile
    )

    with open(os.path.join(BASE_DIR, "optimized_resume.txt"), "w", encoding="utf-8") as f:
        f.write(optimized_resume)
    print("Parsed Resume saved to optimized_resume.txt")

    # 6. Generate DOCX and PDF resume files
    print("\nGenerating fresh DOCX resume...")
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "create_docx.py")], cwd=BASE_DIR, check=True)

    print("Generating fresh PDF resume...")
    subprocess.run([sys.executable, os.path.join(BASE_DIR, "convert_to_pdf.py")], cwd=BASE_DIR, check=True)
    print("Resume PDF generated at resumes/Resumes.pdf")

    # 7. Generate email body
    print("\nGenerating outreach email...")
    actual_job_title = job_title
    try:
        resume_data = json.loads(optimized_resume)
        actual_job_title = resume_data.get("target_role", job_title)
    except Exception:
        pass

    body = generate_email(
        candidate_name=client_profile.get("name", "Sai Rushi Kasyap"),
        recruiter_name=recruiter_name,
        role=actual_job_title,
        linkedin_post_url=recruiter_url,
        candidate_details=candidate_details,
        job_description=job_description
    )
    import emailer.templates as templates
    subject = templates.LAST_GENERATED_SUBJECT

    print("\n===== GENERATED TEST EMAIL BODY =====")
    def safe_print(text_to_print):
        try:
            print(text_to_print)
        except UnicodeEncodeError:
            encoding = sys.stdout.encoding or 'utf-8'
            print(text_to_print.encode(encoding, errors='replace').decode(encoding))
    safe_print(body)
    print("=====================================\n")

    # 8. Send test email to USER's email address
    test_receiver = "ankitgupta37937@gmail.com"
    print(f"\nSending test email to: {test_receiver}...")
    
    import random
    rand_val = random.randint(100, 999)
    attachment_name = f"rushi{rand_val}.pdf"

    send_email(
        receiver=test_receiver,
        subject=f"[TEST] {subject}",
        body=body,
        resume_path=os.path.join(BASE_DIR, "resumes", "Resumes.pdf"),
        cc=[],
        bcc=[],
        attachment_filename=attachment_name
    )

    print("\n==================================================")
    print("SUCCESS: Test email sent successfully to " + test_receiver)
    print("==================================================")

if __name__ == "__main__":
    test_outreach()
