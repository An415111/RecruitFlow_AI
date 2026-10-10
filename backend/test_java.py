from emailer.templates import generate_email

jd = """
Java Developer

Skills:
Java
Spring Boot
Microservices
AWS
"""

candidate_details = """
Candidate Name: Ankit Gupta
Email: ankitgupta37937@gmail.com
"""

print(
    generate_email(
        "Ankit Gupta",
        "Recruiter",
        "Java Developer",
        "https://linkedin.com/test1",
        candidate_details,
        jd
    )
)