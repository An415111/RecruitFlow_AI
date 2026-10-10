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

result = optimize_resume(
    jd,
    resume
)

print(result)