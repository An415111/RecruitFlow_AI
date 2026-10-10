from sqlalchemy import create_engine, text
import os
import subprocess
import sys

from emailer.gmail_sender import send_email
from emailer.templates import generate_email
from ai.resume_optimizer import optimize_resume

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "jobs.db")
engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"check_same_thread": False, "timeout": 30.0}
)


def safe_print(text_to_print):
    try:
        print(text_to_print)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or 'utf-8'
        print(text_to_print.encode(encoding, errors='replace').decode(encoding))


def extract_recruiter_name(job_description):
    try:
        import json
        from ai.llm_client import call_llm
        prompt = f"""
You are an expert data extraction assistant.
Analyze the following LinkedIn post/job description and extract the recruiter's name.

Job Description:
{job_description}

Rules:
1. Look for the author of the post (usually immediately after 'Feed post', but if it's a group post, look for the person posting inside the group, e.g. "Rahul N" after the group name).
2. Look for the name in the email signature at the bottom (e.g., "Best Regards, Sam R", "Thanks & Regards, Balamurali").
3. Look at the email address prefix (e.g., "rahul@vysystems.com") and see if a corresponding name "Rahul" or "Rahul N" is mentioned in the post body.
4. If a full name (first and last name/initial) is available, you MUST return the full name (e.g., "Gogulakrishnan Veeramuthu", "Aruna Yadav", "Nigesh Thangam", "Rahul N"). Only return the first name if no last name is mentioned.
5. If no recruiter name is available or if you are unsure, return "Recruiter". Never invent a name.

Output Format:
Return ONLY a valid JSON object with the key "recruiter_name". Do not include any other keys, explanations, or code blocks.
Example:
{{"recruiter_name": "Harshita Sharma"}}
"""
        raw = call_llm(prompt, temperature=0.0, max_tokens=50)
        start_json = raw.find('{')
        end_json = raw.rfind('}')
        if start_json != -1 and end_json != -1:
            raw = raw[start_json:end_json+1]
            
        data = json.loads(raw)
        name = data.get("recruiter_name", "Recruiter").strip()
        if len(name) > 40 or "\n" in name:
            return "Recruiter"
        return name
    except Exception:
        return "Recruiter"


def select_client():
    import json
    
    profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
    except Exception as e:
        print(f"Error loading candidate_profiles.json: {e}")
        sys.exit(1)

    print("\n==================================================")
    print("RECRUITFLOW-AI: OUTREACH CANDIDATE SELECTION")
    print("==================================================")
    client_keys = list(profiles.keys())
    for idx, key in enumerate(client_keys, 1):
        name = profiles[key].get("name", key)
        print(f"{idx}. {name} ({key})")
    
    while True:
        try:
            choice = input(f"\nSelect a candidate (1-{len(client_keys)}): ").strip()
            if not choice:
                continue
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(client_keys):
                selected_key = client_keys[choice_idx]
                return selected_key, profiles[selected_key]
            else:
                print(f"Please select a number between 1 and {len(client_keys)}.")
        except ValueError:
            print("Please enter a valid number.")


def send_all(limit=None, client_id=None):
    if not client_id:
        client_id, client_profile = select_client()
    else:
        import json
        profiles_path = os.path.join(BASE_DIR, "candidate_profiles.json")
        with open(profiles_path, "r", encoding="utf-8") as f:
            profiles = json.load(f)
        client_profile = profiles.get(client_id)
        if not client_profile:
            raise ValueError(f"Candidate profile '{client_id}' not found.")

    client_suffix = f"_{client_id}" if client_id else ""
    db_name = f"jobs{client_suffix}.db"
    engine = create_engine(
        f"sqlite:///{os.path.join(BASE_DIR, db_name)}",
        connect_args={"check_same_thread": False, "timeout": 30.0}
    )

    with engine.connect() as conn:
        try:
            conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.commit()
        except Exception:
            pass

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    company TEXT,
                    email TEXT UNIQUE,
                    url TEXT,
                    job_description TEXT,
                    sent INTEGER DEFAULT 0,
                    client TEXT,
                    search_keyword TEXT
                )
                """
            )
        )
        conn.commit()

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS sent_history (
                    email TEXT PRIMARY KEY,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )
        conn.commit()
        conn.execute(
            text(
                """
                INSERT OR IGNORE INTO sent_history (email)
                SELECT DISTINCT LOWER(TRIM(email)) FROM jobs WHERE sent = 1 AND email IS NOT NULL AND TRIM(email) != ''
                """
            )
        )
        conn.commit()

        # Backward compatibility for legacy jobs (treat client IS NULL as 'rushi')
        if client_id == "rushi":
            query = """
                SELECT id, email, title, job_description, url
                FROM jobs
                WHERE (sent IS NULL OR sent = 0)
                  AND email IS NOT NULL AND TRIM(email) != ''
                  AND (client = :client_id OR client IS NULL)
                  AND LOWER(TRIM(email)) NOT IN (SELECT DISTINCT LOWER(TRIM(email)) FROM jobs WHERE sent = 1)
                  AND LOWER(TRIM(email)) NOT IN (SELECT DISTINCT LOWER(TRIM(email)) FROM sent_history)
                GROUP BY LOWER(TRIM(email))
                ORDER BY id ASC
            """
        else:
            query = """
                SELECT id, email, title, job_description, url
                FROM jobs
                WHERE (sent IS NULL OR sent = 0)
                  AND email IS NOT NULL AND TRIM(email) != ''
                  AND client = :client_id
                  AND LOWER(TRIM(email)) NOT IN (SELECT DISTINCT LOWER(TRIM(email)) FROM jobs WHERE sent = 1)
                  AND LOWER(TRIM(email)) NOT IN (SELECT DISTINCT LOWER(TRIM(email)) FROM sent_history)
                GROUP BY LOWER(TRIM(email))
                ORDER BY id ASC
            """

        result = conn.execute(text(query), {"client_id": client_id})

        recruiters = result.fetchall()
        if limit is not None:
            recruiters = recruiters[:limit]

    print(f"\nRecruiters Found: {len(recruiters)}\n")

    if len(recruiters) == 0:

        print(f"No unsent recruiters found for candidate: {client_profile['name']}")
        return

    sent_emails_in_run = set()
    for row in recruiters:

        job_id = row[0]
        recruiter_email = row[1]
        job_title = row[2]
        job_description = row[3]
        recruiter_url = row[4]

        # Local process double check
        normalized_email = recruiter_email.strip().lower()
        if normalized_email in sent_emails_in_run:
            print(f"Skipping -> {recruiter_email} (already processed/sent in this execution run)")
            continue

        # Double check database and sent_history to prevent race conditions or duplicate sends
        with engine.connect() as conn:
            check = conn.execute(
                text(
                    """
                    SELECT sent FROM jobs WHERE LOWER(TRIM(email)) = LOWER(TRIM(:email)) AND sent = 1
                    UNION
                    SELECT 1 FROM sent_history WHERE LOWER(TRIM(email)) = LOWER(TRIM(:email))
                    """
                ),
                {"email": recruiter_email}
            ).fetchall()
            if check:
                print(f"Skipping -> {recruiter_email} (already sent in another thread/process or history)")
                # Add to local set since we know it's already sent
                sent_emails_in_run.add(normalized_email)
                continue

        try:

            print(f"\nProcessing Job: {job_title}")

            print("\n========== JOB DESCRIPTION ==========\n")
            safe_print(job_description)
            print("\n=====================================\n")

            
# CANDIDATE PROFILE
# ====================================

            candidate_name = client_profile.get("name", "Sai Rushi Kasyap")

            # Format education and skills for inclusion in email generator candidate_details
            edu_list = client_profile.get("education", [])
            edu_str = ""
            for edu in edu_list:
                edu_str += f"\n- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('duration', '')})"
                if edu.get('cgpa'):
                    edu_str += f" | GPA: {edu.get('cgpa', '')}"
            skills_str = ", ".join(client_profile.get("keywords", []))

            candidate_details = f"""Candidate Name: {client_profile.get('name', '')}
Email: {client_profile.get('email', '')}
Phone: {client_profile.get('phone', '')}
Location: {client_profile.get('location', '')}
LinkedIn: {client_profile.get('linkedin', '')}
Open to Relocate: {client_profile.get('open_to_relocate', 'yes')}
Work Authorization: {client_profile.get('work_auth', 'not mentioned')}
Availability: {client_profile.get('availability', 'immediate')}
Employer: {client_profile.get('employer', 'quinn@jpitstaffing.com')}
Employer Number: {client_profile.get('employer_number', '+1 5716265445')}
Education: {edu_str}
Key Skills/Keywords: {skills_str}"""

            # ====================================
            # LOAD BASE RESUME
            # ====================================
            base_resume_file = client_profile.get("base_resume_file", "test_resume.txt")
            base_resume_path = os.path.join(BASE_DIR, base_resume_file)

            with open(
                base_resume_path,
                "r",
                encoding="utf-8"
            ) as f:

                base_resume = f.read()

            # ====================================
            # OPTIMIZE RESUME
            # ====================================

            optimized_resume = optimize_resume(
                job_description,
                base_resume,
                candidate_profile=client_profile
            )

            print("\n===== OPTIMIZED RESUME =====\n")
            safe_print(optimized_resume[:1000])

            with open(
                "optimized_resume.txt",
                "w",
                encoding="utf-8"
            ) as f:

                f.write(optimized_resume)

            print("\nOptimized Resume Saved")

            # Save job description for DOCX and PDF generators to append in white/6pt font
            with open("job_description.txt", "w", encoding="utf-8") as f:
                f.write(job_description)

            # Create fresh DOCX
            subprocess.run(
                [sys.executable, "create_docx.py"],
                cwd=BASE_DIR,
                check=True
            )

            # Create fresh PDF
            subprocess.run(
                [sys.executable, "convert_to_pdf.py"],
                cwd=BASE_DIR,
                check=True
            )

            print("\nFresh PDF Generated")

            # ====================================
            # EXTRACT RECRUITER NAME
            # ====================================

            recruiter_name = extract_recruiter_name(job_description)
            print(f"Extracted Recruiter Name: {recruiter_name}")

            # ====================================
            # GENERATE EMAIL
            # ====================================

            actual_job_title = job_title
            try:
                import json
                resume_data = json.loads(optimized_resume)
                actual_job_title = resume_data.get("target_role", job_title)
            except Exception:
                pass

            body = generate_email(
                candidate_name=candidate_name,
                recruiter_name=recruiter_name,
                role=actual_job_title,
                linkedin_post_url=recruiter_url,
                candidate_details=candidate_details,
                job_description=job_description
            )
            import emailer.templates as templates
            subject = templates.LAST_GENERATED_SUBJECT

            print("\n===== GENERATED EMAIL =====\n")
            safe_print(body[:1000])

            print(f"\nSending -> {recruiter_email}")

            # Generate a random 3-digit number for the filename override
            import random
            rand_val = random.randint(100, 999)
            attachment_name = f"{client_id}{rand_val}.pdf"

            send_email(
                recruiter_email,
                subject,
                body,
                "resumes/Resumes.pdf",
                cc=client_profile.get("cc", []),
                bcc=client_profile.get("bcc", []),
                attachment_filename=attachment_name
            )
            sent_emails_in_run.add(normalized_email)

            # ====================================
            # MARK AS SENT
            # ====================================

            with engine.connect() as conn:

                conn.execute(
                    text(
                        """
                        UPDATE jobs
                        SET sent = 1
                        WHERE LOWER(TRIM(email)) = LOWER(TRIM(:email))
                        """
                    ),
                    {
                        "email": recruiter_email
                    }
                )

                conn.execute(
                    text(
                        """
                        INSERT OR IGNORE INTO sent_history (email)
                        VALUES (:email)
                        """
                    ),
                    {
                        "email": recruiter_email.strip().lower()
                    }
                )

                conn.commit()

            print(
                f"\nEmail Sent Successfully -> {recruiter_email}"
            )

        except Exception as e:

            print(
                f"\nFailed -> {recruiter_email}"
            )

            print(e)


if __name__ == "__main__":
    import sys
    limit = 50
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    send_all(limit=limit)