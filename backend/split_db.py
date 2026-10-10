# split_db.py
import os
import sqlite3

def migrate():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    source_db = os.path.join(backend_dir, "jobs.db")
    
    if not os.path.exists(source_db):
        print("No legacy jobs.db found. No split migration needed.")
        return
        
    print("Found legacy jobs.db. Splitting data into candidate-specific databases...")
    
    # Connect to legacy db
    conn = sqlite3.connect(source_db)
    cursor = conn.cursor()
    
    # Read table info
    cursor.execute("PRAGMA table_info(jobs)")
    columns_info = cursor.fetchall()
    column_names = [col[1] for col in columns_info]
    
    # Read all rows from jobs
    cursor.execute("SELECT * FROM jobs")
    all_jobs = cursor.fetchall()
    
    # Read all rows from sent_history
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sent_history'")
    has_sent_history = cursor.fetchone()
    
    sent_history_rows = []
    if has_sent_history:
        cursor.execute("SELECT * FROM sent_history")
        sent_history_rows = cursor.fetchall()
        
    conn.close()
    
    # Get index of 'client' column
    client_idx = column_names.index("client") if "client" in column_names else -1
    
    # For each candidate, build/update a new DB
    candidates = ["rushi", "anoushika"]
    
    for candidate in candidates:
        dest_db = os.path.join(backend_dir, f"jobs_{candidate}.db")
        print(f"Creating/updating {dest_db}...")
        
        dest_conn = sqlite3.connect(dest_db)
        dest_cursor = dest_conn.cursor()
        
        # Create jobs table in destination
        dest_cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                email TEXT,
                url TEXT,
                job_description TEXT,
                sent INTEGER,
                client TEXT,
                search_keyword TEXT
            )
        """)
        
        # Create sent_history table in destination
        dest_cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_history (
                email TEXT PRIMARY KEY,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Filter jobs for this candidate
        candidate_jobs = []
        for job in all_jobs:
            job_client = job[client_idx] if client_idx != -1 else None
            if not job_client:
                job_client = "rushi" # default
                
            if job_client == candidate:
                candidate_jobs.append(job)
                
        # Insert jobs
        for job in candidate_jobs:
            dest_cursor.execute("""
                INSERT OR IGNORE INTO jobs (id, title, company, email, url, job_description, sent, client, search_keyword)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job[0], # id
                job[1] if len(job) > 1 else None,
                job[2] if len(job) > 2 else None,
                job[3] if len(job) > 3 else None,
                job[4] if len(job) > 4 else None,
                job[5] if len(job) > 5 else None,
                job[6] if len(job) > 6 else None,
                job[7] if len(job) > 7 else None,
                job[8] if len(job) > 8 else None
            ))
            
        # Filter and insert sent_history
        sent_emails = {job[3].strip().lower() for job in candidate_jobs if len(job) > 6 and job[6] == 1 and job[3]}
        
        for sh in sent_history_rows:
            sh_email = sh[0].strip().lower()
            if sh_email in sent_emails or any(job[3] and job[3].strip().lower() == sh_email for job in candidate_jobs):
                dest_cursor.execute("INSERT OR IGNORE INTO sent_history (email, sent_at) VALUES (?, ?)", (sh[0], sh[1]))
                
        dest_conn.commit()
        dest_conn.close()
        print(f"Database {os.path.basename(dest_db)} created/updated with {len(candidate_jobs)} records.")
        
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
