from emailer.templates import generate_email

candidate_details = """
Candidate Name: Sai Rushi Kasyap
Email: rushimukkamala5@gmail.com
Phone: +1 (346)-646-8149
Location: Monroe, Michigan
LinkedIn: https://www.linkedin.com/in/rushi-mukkamala
Open to Relocate: yes
Work Authorization: STEM OPT
Availability: immediate
Total Experience: not mentioned
Employer: Quinn@jpitstaffing.com
Employer Number: +1 5716265445
"""

job_description = """
Java Developer

Required Skills:
Java
Spring Boot
SQL
REST API
Git
AWS
Microservices
"""

email = generate_email(
    candidate_name="Sai Rushi Kasyap",
    recruiter_name="Sai Ambati",
    role="Java Developer",
    linkedin_post_url="https://www.linkedin.com/posts/sample-post",
    candidate_details=candidate_details,
    job_description=job_description
)

import sys
def safe_print(text_to_print):
    try:
        print(text_to_print)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        print(text_to_print.encode(encoding, errors='replace').decode(encoding))

safe_print(email)

with open("generated_email_test.txt", "w", encoding="utf-8") as f:
    f.write(email)
print("\nGenerated email saved to generated_email_test.txt")
