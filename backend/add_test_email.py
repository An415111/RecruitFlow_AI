import os
import sys
from sqlalchemy import create_engine, text

print("\nSelect database to add test email:")
print("1. Sai Rushi Kasyap (rushi)")
print("2. Santosh Anoushika Komala (anoushika)")
choice = input("Choice (1-2): ").strip()
db_name = "jobs_rushi.db" if choice == "1" else "jobs_anoushika.db"

engine = create_engine(f"sqlite:///{db_name}")

with engine.connect() as conn:

    conn.execute(
        text("""
        INSERT INTO jobs
        (
            title,
            company,
            email,
            url,
            job_description,
            sent
        )
        VALUES
        (
            :title,
            :company,
            :email,
            :url,
            :job_description,
            :sent
        )
        """),
        {
            "title": "Python Developer",
            "company": "Test Company",
            "email": "ankitssgupta0786@gmail.com",
            "url": "test",
            "job_description": "Python FastAPI SQL",
            "sent": 0
        }
    )

    conn.commit()

print("Test Email Added")