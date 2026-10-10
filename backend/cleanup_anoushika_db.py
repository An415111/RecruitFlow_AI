# cleanup_anoushika_db.py
import os
import sqlite3

def cleanup():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(backend_dir, "jobs_anoushika.db")
    
    if not os.path.exists(db_path):
        print("jobs_anoushika.db does not exist.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Whitelist delete: delete anything that does not contain core cyber terms in title
    # Whitelist delete: delete anything that does not contain core cyber terms in title,
    # or contains senior/manager/architect/offensive security terms
    query = """
    DELETE FROM jobs 
    WHERE NOT (
        LOWER(title) LIKE '%security%'
        OR LOWER(title) LIKE '%cyber%'
        OR LOWER(title) LIKE '%soc%'
        OR LOWER(title) LIKE '%siem%'
        OR LOWER(title) LIKE '%incident%'
        OR LOWER(title) LIKE '%threat%'
        OR LOWER(title) LIKE '%iam%'
        OR LOWER(title) LIKE '%access%'
        OR LOWER(title) LIKE '%blue%team%'
        OR LOWER(title) LIKE '%splunk%'
        OR LOWER(title) LIKE '%vulnerability%'
        OR LOWER(title) LIKE '%grc%'
    ) OR (
        LOWER(title) LIKE '%senior%'
        OR LOWER(title) LIKE '%sr.%'
        OR LOWER(title) LIKE '%lead%'
        OR LOWER(title) LIKE '%principal%'
        OR LOWER(title) LIKE '%staff%'
        OR LOWER(title) LIKE '%director%'
        OR LOWER(title) LIKE '%manager%'
        OR LOWER(title) LIKE '%architect%'
        OR LOWER(title) LIKE '%head%'
        OR LOWER(title) LIKE '%chief%'
        OR LOWER(title) LIKE '%vp%'
        OR LOWER(title) LIKE '%penetration%'
        OR LOWER(title) LIKE '%pentester%'
        OR LOWER(title) LIKE '%pen tester%'
        OR LOWER(title) LIKE '%ethical hacker%'
        OR LOWER(title) LIKE '%red team%'
        OR LOWER(title) LIKE '%devsecops%'
    )
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        print(f"Successfully cleaned database: deleted {cursor.rowcount} mismatching/senior/offensive jobs from jobs_anoushika.db.")
    except Exception as e:
        print(f"Error cleaning up jobs_anoushika.db: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup()
