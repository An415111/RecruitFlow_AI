import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "jobs.db"))
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30.0}
)

def ensure_unique_email_constraint(db_file_path):
    import sqlite3
    if not os.path.exists(db_file_path):
        return
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    try:
        # Check if jobs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
        if not cursor.fetchone():
            conn.close()
            return
            
        # Check table SQL to see if UNIQUE(email) is present
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='jobs'")
        create_sql = cursor.fetchone()[0] or ""
        
        if "UNIQUE" not in create_sql.upper():
            print(f"Migrating {os.path.basename(db_file_path)} to add UNIQUE constraint on email...")
            
            # 1. Create a temporary table with unique constraint
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs_new (
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
            """)
            
            # 2. Copy data, grouping by email to discard duplicates
            cursor.execute("""
                INSERT OR IGNORE INTO jobs_new (id, title, company, email, url, job_description, sent, client, search_keyword)
                SELECT id, title, company, email, url, job_description, MAX(IFNULL(sent, 0)), client, search_keyword
                FROM jobs
                GROUP BY LOWER(TRIM(email))
            """)
            
            # 3. Drop old table and rename new one
            cursor.execute("DROP TABLE jobs")
            cursor.execute("ALTER TABLE jobs_new RENAME TO jobs")
            conn.commit()
            print(f"Successfully migrated {os.path.basename(db_file_path)} to new schema.")
    except Exception as e:
        print(f"Error migrating {os.path.basename(db_file_path)}: {e}")
        conn.rollback()
    finally:
        conn.close()

# Run migrations at import time
ensure_unique_email_constraint(os.path.join(BASE_DIR, "jobs_rushi.db"))
ensure_unique_email_constraint(os.path.join(BASE_DIR, "jobs_anoushika.db"))
ensure_unique_email_constraint(os.path.join(BASE_DIR, "jobs.db"))

# Enable WAL mode and ensure tables exist for default database
with engine.connect() as conn:
    try:
        conn.execute(text("PRAGMA journal_mode=WAL;"))
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
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS hotlist_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recruiter_email TEXT,
                    campaign_name TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
                """
            )
        )
        conn.commit()
    except Exception:
        pass

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()