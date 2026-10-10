import os
from sqlalchemy import create_engine, text

# Get absolute path to backend/jobs.db
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
db_path = os.path.join(BACKEND_DIR, "jobs.db")

engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"timeout": 30.0}
)


def save_email(
    email,
    title,
    job_description,
    url,
    client=None,
    search_keyword=None
):
    email = email.strip().lower()




    # Dynamically select database file based on client
    client_suffix = f"_{client}" if client else ""
    db_name = f"jobs{client_suffix}.db"
    db_file_path = os.path.join(BACKEND_DIR, db_name)

    engine = create_engine(
        f"sqlite:///{db_file_path}",
        connect_args={"timeout": 30.0}
    )

    with engine.connect() as conn:

        # Ensure jobs table exists with UNIQUE constraint on email
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

        # Ensure sent_history table exists
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

        # Backward compatibility alterations
        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN client TEXT;"))
            conn.commit()
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE jobs ADD COLUMN search_keyword TEXT;"))
            conn.commit()
        except Exception:
            pass

        conn.execute(
            text(
                """
                INSERT OR IGNORE INTO sent_history (email)
                SELECT DISTINCT LOWER(TRIM(email)) FROM jobs WHERE sent = 1 AND email IS NOT NULL AND TRIM(email) != ''
                """
            )
        )
        conn.commit()

        # Check if the email already exists in either sent_history or jobs table
        existing = conn.execute(
            text("""
            SELECT email FROM jobs WHERE LOWER(TRIM(email)) = :email
            UNION
            SELECT email FROM sent_history WHERE LOWER(TRIM(email)) = :email
            """),
            {
                "email": email
            }
        ).fetchone()

        if existing:
            print(f"Already Exists: {email}")
            return

        try:
            conn.execute(
                text("""
                INSERT INTO jobs
                (
                    title,
                    company,
                    email,
                    url,
                    job_description,
                    client,
                    search_keyword,
                    sent
                )
                VALUES
                (
                    :title,
                    :company,
                    :email,
                    :url,
                    :job_description,
                    :client,
                    :search_keyword,
                    0
                )
                """),
                {
                    "title": title,
                    "company": "LinkedIn Recruiter",
                    "email": email,
                    "url": url,
                    "job_description": job_description,
                    "client": client,
                    "search_keyword": search_keyword
                }
            )
            conn.commit()
            print(f"Saved: {email}")
        except Exception as e:
            if "UNIQUE" in str(e):
                print(f"Already Exists: {email}")
            else:
                print(f"Error saving {email}: {e}")