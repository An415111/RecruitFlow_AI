from emailer.templates import generate_email

jd = """
Business Analyst

Skills:
Requirements Gathering
Agile
JIRA
SQL
Stakeholder Management
"""

candidate_details = """
Candidate Name: Ankit Gupta
Email: ankitgupta37937@gmail.com
"""

print(
    generate_email(
        "Ankit Gupta",
        "Recruiter",
        "Business Analyst",
        "https://linkedin.com/test3",
        candidate_details,
        jd
    )
)