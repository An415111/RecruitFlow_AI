from ai.resume_optimizer import optimize_resume

jd = """
Java Developer
Python
FastAPI
SQL
AWS
"""

resume = """
BSc Computer Science
Python
HTML
CSS
JavaScript
"""

print(
    optimize_resume(
        jd,
        resume
    )
)