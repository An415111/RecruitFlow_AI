from ai.resume_optimizer import optimize_resume

with open("test_resume.txt", "r", encoding="utf-8") as f:
    resume = f.read()

jd = """
Assistant Controller

Required Skills:
- GAAP compliance
- Nonprofit fund accounting
- SAGE 100 or Sage Intacct
- OMB Uniform Guidance (2 CFR Part 200)
- Financial statement preparation and review
- External audit liaison
- Excel (VBA/macros)
- Financial reporting
"""

optimized_resume = optimize_resume(
    jd,
    resume
)

with open(
    "optimized_resume.txt",
    "w",
    encoding="utf-8"
) as f:
    f.write(optimized_resume)

print("Optimized Resume Saved")