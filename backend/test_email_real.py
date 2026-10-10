from emailer.templates import generate_email

jd = """
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

candidate_details = """
Candidate Name: Ankit Gupta
Email: ankitgupta37937@gmail.com
Phone: 9833250407
Location: Mumbai, India
Work Authorization: Indian Citizen
Availability: Immediate
Experience: Fresher
LinkedIn: https://www.linkedin.com/in/ankit-gupta018/
GitHub: https://github.com/An415111
"""

email = generate_email(
    candidate_name="Ankit Gupta",
    recruiter_name="Recruiter",
    role="Java Developer",
    linkedin_post_url="https://www.linkedin.com/in/sample-recruiter/",
    candidate_details=candidate_details,
    job_description=jd
)

print(email)