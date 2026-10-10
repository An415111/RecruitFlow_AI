from emailer.gmail_sender import send_email
from emailer.templates import generate_email

candidate_details = """
Candidate Name: Ankit Gupta
Email: ankitgupta37937@gmail.com
Phone: 9833250407
Location: Mumbai, India
Work Authorization: Indian Citizen
Availability: Immediate
Experience: Fresher
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

body = generate_email(
    candidate_name="Ankit Gupta",
    recruiter_name="Ankit Gupta",
    role="Java Developer",
    linkedin_post_url="https://www.linkedin.com/posts/sample-post",
    candidate_details=candidate_details,
    job_description=job_description
)

send_email(
    "ankitgupta37937@gmail.com",   # your email
    "Submission for Java Developer - Ankit Gupta",
    body
)

print("Email Sent Successfully")