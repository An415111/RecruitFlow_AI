import os
import sqlite3
import sys

# Reconfigure terminal output to support UTF-8 (prevents crashes from emojis in job posts)
sys.stdout.reconfigure(encoding='utf-8')

print("\n==================================================")
print("RECRUITFLOW-AI: CHECK DATABASE")
print("==================================================")
print("1. Sai Rushi Kasyap (rushi)")
print("2. Santosh Anoushika Komala (anoushika)")

while True:
    try:
        choice = input("\nSelect a candidate database to check (1-2): ").strip()
        if choice == "1":
            db_name = "jobs_rushi.db"
            candidate_name = "Sai Rushi Kasyap"
            break
        elif choice == "2":
            db_name = "jobs_anoushika.db"
            candidate_name = "Santosh Anoushika Komala"
            break
        else:
            print("Please select 1 or 2.")
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

# Connect to the selected database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, db_name)

if not os.path.exists(db_path):
    # Check if we should fall back to legacy jobs.db
    legacy_path = os.path.join(BASE_DIR, "jobs.db")
    if db_name == "jobs_rushi.db" and os.path.exists(legacy_path):
        print(f"\nNote: jobs_rushi.db not found, falling back to legacy jobs.db")
        db_path = legacy_path
    else:
        print(f"\nDatabase file {db_path} does not exist yet. Please run the scraper first.")
        sys.exit(0)

print(f"\nChecking database: {os.path.basename(db_path)} for {candidate_name}...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Execute SQL query to select all records in the jobs table
cursor.execute("""
SELECT 
    title, 
    email, 
    url, 
    substr(job_description, 1, 200) 
FROM jobs
""")

# Fetch all matching records using fetchall()
rows = cursor.fetchall()

# Print every record stored in the jobs table
for row in rows:
    print("\n--------------------")
    print("TITLE:", row[0])
    print("EMAIL:", row[1])
    print("URL:", row[2])
    print("JD:", row[3])

# Print total number of records found
print("\n====================")
print(f"TOTAL RECORDS FOUND: {len(rows)}")

# Close the database connection
conn.close()