from ai.resume_optimizer import optimize_resume

jd = """
Java Developer

Requirements:
- Java
- SQL
- Spring Boot
- REST APIs
- Problem Solving
- OOP
- Git
"""

resume = """
B.Sc Computer Science
CGPA: 9.63

Skills:
Python, Java, JavaScript, SQL, MongoDB,
Node.js, Express.js, HTML, CSS

Projects:
Musico Music Streaming Application
Assistify Telegram Bot
Color Game
"""

result = optimize_resume(
    jd,
    resume
)

print(result)