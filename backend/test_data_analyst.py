from emailer.templates import generate_email

jd = """
Data Analyst

Skills:
SQL
Power BI
Excel
Tableau
Python
"""

candidate_details = """
Candidate Name: Ankit Gupta
Email: ankitgupta37937@gmail.com
"""

print(
    generate_email(
        "Ankit Gupta",
        "Recruiter",
        "Data Analyst",
        "https://linkedin.com/test2",
        candidate_details,
        jd
    )
)