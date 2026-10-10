import os
import sys
import sqlite3

# Add backend directory to Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from linkedin.save_emails import save_email

def run_tests():
    client_name = "test_filter"
    db_name = f"jobs_{client_name}.db"
    db_path = os.path.join(CURRENT_DIR, db_name)

    # Make sure we start with a clean test database
    if os.path.exists(db_path):
        os.remove(db_path)

    print("Running save_email tests...")

    # Test Case 1: Email contains "staffing"
    print("Testing Case 1: Email containing 'staffing'...")
    save_email(
        email="recruiter@staffingagency.com",
        title="Python Developer",
        job_description="Looking for Python Developer with Django experience.",
        url="http://example.com/job1",
        client=client_name
    )

    # Test Case 2: Job description contains "staffing"
    print("Testing Case 2: Job description containing 'staffing'...")
    save_email(
        email="hr@normalcompany.com",
        title="Java Developer",
        job_description="This position is open through a staffing agency.",
        url="http://example.com/job2",
        client=client_name
    )

    # Test Case 3: Normal job and email (no 'staffing')
    print("Testing Case 3: Normal job and email...")
    save_email(
        email="jobs@techcorp.com",
        title="React Developer",
        job_description="We are hiring a React developer directly. No agency.",
        url="http://example.com/job3",
        client=client_name
    )

    # Verify database contents
    if not os.path.exists(db_path):
        print(f"Error: Database {db_name} was not created!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT email, title, job_description FROM jobs")
    rows = cursor.fetchall()
    conn.close()

    print(f"\nSaved jobs count: {len(rows)}")
    for row in rows:
        print(f" - Email: {row[0]}, Title: {row[1]}")

    # Assertions
    assert len(rows) == 3, f"Expected 3 saved jobs, but got {len(rows)}"
    emails_saved = [row[0] for row in rows]
    assert "recruiter@staffingagency.com" in emails_saved
    assert "hr@normalcompany.com" in emails_saved
    assert "jobs@techcorp.com" in emails_saved
    print("\nSUCCESS: All save_email filter tests passed!")

    # Cleanup
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Test database cleaned up.")
    except PermissionError:
        print("Note: Could not delete test database because the file was locked by SQLAlchemy connection pool. This is expected on Windows.")

if __name__ == "__main__":
    run_tests()
