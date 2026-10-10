from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(override=True)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None


def get_recruiter_first_name(full_name):
    if not full_name or full_name.lower().strip() == "recruiter":
        return "Recruiter"
    parts = full_name.strip().split()
    if parts:
        first = parts[0]
        if first.lower() in ["mr.", "ms.", "mrs.", "dr.", "mr", "ms", "mrs", "dr"] and len(parts) > 1:
            return parts[1]
        return first
    return "Recruiter"


def clean_job_description(jd_text):
    import re
    if not jd_text:
        return ""

    lines = jd_text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue

        # Skip common LinkedIn action buttons and footer clutter
        if stripped in ["Like", "Comment", "Share", "Send", "Feed post", "Follow", "Report this post", "Promoted", "… more", "more"]:
            continue

        # Skip solitary numbers or like/comment counter lines (e.g. '1', '12', '5 likes', '2 comments')
        if re.match(r'^\d+$', stripped):
            continue
        if re.match(r'^\d+\s*(?:likes?|comments?|reposts?|shares?|reactions?)$', stripped, re.IGNORECASE):
            continue

        # Skip hashtag lines or lines consisting entirely of hashtags
        words = stripped.split()
        if words and all(w.startswith("#") for w in words):
            continue

        # Remove hashtags within lines or clean lines that are mostly hashtags
        line_no_hashtags = re.sub(r'#\w+', '', stripped).strip()
        if not line_no_hashtags:
            continue

        # Skip recruiter contact lines (e.g. Email: ..., Mail: ..., Number: ..., Phone: ..., Contact: ..., etc.)
        lower_line = line_no_hashtags.lower()
        if re.match(r'^(?:📧|✉️|📱|📞|☎️|▶️|👉|\*|-)?\s*(?:email|mail|e-mail|number|phone|mobile|contact|call|reach|whatsapp|send resume|drop cv|share resume)\s*[:\-]\s*', lower_line):
            continue
        if re.match(r'^(?:send|drop|share|forward)\s+(?:your\s+)?(?:resume|cv|profile)\s+(?:to|at)\s*[:\-]?\s*', lower_line):
            continue

        cleaned_lines.append(line_no_hashtags)

    # Collapse multi-blank lines
    result = "\n".join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result).strip()
    return result


def load_candidate_profile(candidate_name, candidate_details_str=None):
    import json
    import os
    
    profile = {
        "name": candidate_name,
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "open_to_relocate": "no",
        "work_auth": "",
        "availability": "immediate",
        "experience": "not mentioned",
        "education": [],
        "keywords": []
    }
    
    if candidate_details_str:
        lines = candidate_details_str.strip().split("\n")
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                k = key.strip().lower()
                v = val.strip()
                if "name" in k:
                    profile["name"] = v
                elif "email" in k:
                    profile["email"] = v
                elif "phone" in k:
                    profile["phone"] = v
                elif "location" in k:
                    profile["location"] = v
                elif "linkedin" in k:
                    profile["linkedin"] = v
                elif "open to relocate" in k or "relocating" in k:
                    profile["open_to_relocate"] = v
                elif "work authorization" in k or "work auth" in k:
                    profile["work_auth"] = v
                elif "availability" in k:
                    profile["availability"] = v
                elif "experience" in k:
                    profile["experience"] = v
                    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        profiles_path = os.path.join(backend_dir, "candidate_profiles.json")
        if os.path.exists(profiles_path):
            with open(profiles_path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            for key, p in profiles.items():
                if p.get("name", "").lower().strip() == candidate_name.lower().strip():
                    for pk, pv in p.items():
                        profile[pk] = pv
                    break
    except Exception as e:
        print(f"Error loading candidate_profiles.json: {e}")
        
    return profile


LAST_GENERATED_SUBJECT = ""

def clean_tech_skills_for_subject(tech_skills_str):
    import re
    if not tech_skills_str:
        return ""
    # Replace " and " or " & " with ", "
    cleaned = re.sub(r'\b(and|&)\b', ',', tech_skills_str, flags=re.IGNORECASE)
    # Replace multiple spaces/commas with a single comma
    cleaned = re.sub(r'[\s,]+', ', ', cleaned)
    # Strip leading/trailing spaces and commas
    cleaned = cleaned.strip(', ')
    return cleaned


def generate_email(
    candidate_name,
    recruiter_name,
    role,
    linkedin_post_url,
    candidate_details,
    job_description
):
    global LAST_GENERATED_SUBJECT
    profile = load_candidate_profile(candidate_name, candidate_details)
    
    prompt = f"""
You are an expert AI Recruitment Assistant. Your task is to extract highly relevant details and generate a concise summary.

Target Recruiter Name: {recruiter_name}
Target Job Role: {role}
Job Description:
{job_description}

Candidate Profile Details:
- Name: {profile.get('name')}
- Location: {profile.get('location')}
- Work Authorization: {profile.get('work_auth')}
- Experience: {profile.get('experience')}
- Candidate Keywords/Skills: {", ".join(profile.get('keywords', []))}

Your task is to analyze the candidate's keywords and the job description to generate:
1. `tech_skills_intro`: Extract 2-3 key technologies from the Candidate Keywords/Skills that are highly relevant to the Job Description (e.g. "Python, Java, and AWS" or "SIEM, IAM, and Incident Response").
2. `core_skills_bullet`: A single concise bullet point summarizing the candidate's core technical skills, certifications, or competencies matching the target job description (e.g. "Strong command of SIEM tools, incident triage, and access management" or "Proficient in general ledger accounting, financial reporting, and Excel"). Include experience level if mentioned (e.g., "4+ Years of hands-on Data Engineer experience delivering production-grade solutions"). Do NOT invent experience years if not mentioned in candidate details.

Return ONLY a valid JSON object matching the schema below. Do NOT include markdown code block styling like ```json or any other text before/after the JSON.

JSON Schema:
{{
  "tech_skills_intro": "Python, Java, and AWS",
  "core_skills_bullet": "4+ Years of hands-on Data Engineer experience delivering production-grade solutions"
}}
"""

    import time
    import json
    import re
    from ai.llm_client import call_llm
    
    last_error = None
    response = ""
    for attempt in range(3):
        try:
            response = call_llm(prompt, temperature=0.2, max_tokens=1800)
            break
        except Exception as e:
            last_error = e
            sleep_time = 6 + (attempt * 3)
            print(f"\n[Rate Limit / Error] Email Generation hit error: {e}. Retrying in {sleep_time} seconds... (Attempt {attempt+1}/3)")
            time.sleep(sleep_time)
            
    if not response and last_error:
        raise last_error

    try:
        clean_res = response.strip()
        if clean_res.startswith("```"):
            lines = clean_res.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_res = "\n".join(lines).strip()
            
        res_data = json.loads(clean_res)
    except Exception as e:
        print(f"JSON parsing failed for LLM response: {e}. Attempting regex fallback.")
        res_data = {}
        
        tech_match = re.search(r'"tech_skills_intro"\s*:\s*"([^"]+)"', response)
        res_data["tech_skills_intro"] = tech_match.group(1) if tech_match else ", ".join(profile.get("keywords", [])[:3])
        
        core_match = re.search(r'"core_skills_bullet"\s*:\s*"([^"]+)"', response)
        res_data["core_skills_bullet"] = core_match.group(1) if core_match else f"Strong background in {', '.join(profile.get('keywords', [])[:4])}"

    tech_skills_intro = res_data.get("tech_skills_intro", ", ".join(profile.get("keywords", [])[:3]))
    core_skills_bullet = res_data.get("core_skills_bullet", f"Strong background in {', '.join(profile.get('keywords', [])[:4])}")
    
    tech_skills_clean = clean_tech_skills_for_subject(tech_skills_intro)
    LAST_GENERATED_SUBJECT = f"Submission for {role} - {profile.get('name')}"
    
    location_clean = profile.get("location", "").replace(" (Relocating)", "")
    if profile.get("open_to_relocate", "").lower() == "yes":
        loc_bullet = "Open to relocation"
    else:
        loc_bullet = f"Located in {location_clean}"
        
    availability = profile.get("availability", "")
    if availability.lower() == "immediate":
        avail_bullet = "Immediate, and available to interview at short notice"
    else:
        avail_bullet = f"Available: {availability}"
        
    phone = profile.get("phone", "")
    email_addr = profile.get("email", "")
    contact_str = f"{phone} | {email_addr}" if phone and email_addr else (phone or email_addr or "")
    relocate_pref = "open to relocation" if profile.get("open_to_relocate", "").lower() == "yes" else "no"
    experience_val = profile.get("experience", "not mentioned")
    
    relocate_str = "Open for relocation" if profile.get("open_to_relocate", "").lower() == "yes" else "No"
    rate_str = profile.get("rate", "Negotiable")
    
    salutation_name = recruiter_name
    if recruiter_name.lower().strip() == "recruiter":
        salutation_name = "Tech Recruiter"

    exp_val = profile.get('experience', '')
    exp_line = f"\n• Total Experience: {exp_val}" if exp_val and exp_val.lower() != "not mentioned" else ""

    jd_raw = clean_job_description(job_description) if job_description else ""
    jd_section = f"\n\n--- JOB DESCRIPTION ---\n{jd_raw}" if jd_raw else ""

    ref_section = ""
    if linkedin_post_url and linkedin_post_url.strip():
        ref_section = f"\n\nRole reference:\n- LinkedIn Post URL: {linkedin_post_url.strip()}"

    email_body = f"""Dear {salutation_name},

I came across your posting for a {role} position. My hands-on experience with {tech_skills_intro} maps directly to what you are looking for, and I would welcome the opportunity to be considered.

Please find my submission details below for your review:

--- SUBMISSION DETAILS ---
• Candidate Name: {profile.get('name')}
• Applied Role: {role}{exp_line}
• Phone / Contact: {profile.get('phone', '')}
• Email Address: {profile.get('email', '')}
• Current Location: {profile.get('location', '')}
• Relocation: {relocate_str}
• Work Authorization: {profile.get('work_auth', '')}
• Availability: {profile.get('availability', '')}
• Rate / Compensation: {rate_str}
• LinkedIn Profile: {profile.get('linkedin', '')}{jd_section}

I have attached my updated resume for your review. Are you available for a brief call sometime this week to discuss this position? Thank you for your time and consideration; I look forward to hearing from you.

Best regards,
{profile.get('name')}{ref_section}"""

    return email_body