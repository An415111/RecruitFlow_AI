import json
from reportlab_resume_maker import generate_resume_pdf

# Read response from file
with open("optimized_resume.txt", "r", encoding="utf-8") as f:
    resume_data = json.load(f)

# Check parsed data
print(resume_data["name"])

# print(resume_data.keys())

# Generate PDF
generate_resume_pdf(resume_data, "Ankit_Gupta_Resume.pdf")