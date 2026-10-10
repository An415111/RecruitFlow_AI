import google.generativeai as genai

genai.configure(api_key="YOUR_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_email(jd, candidate_name):

    prompt = f"""
    Job Description:

    {jd}

    Candidate Name:

    {candidate_name}

    Write a professional recruiter outreach email.
    Keep it short and professional.
    """

    response = model.generate_content(prompt)

    return response.text