from ai.resume_optimizer import optimize_resume

with open("test_resume.txt", "r", encoding="utf-8") as f:
    resume = f.read()

jd = """
Java Developer

Required Skills:
Java
Spring Boot
Microservices
SQL
AWS
REST API
Git
"""

optimized = optimize_resume(
    jd,
    resume
)

with open(
    "optimized_resume.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write(optimized)

print("Resume Saved")