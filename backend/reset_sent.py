# reset_sent.py
import os
import sys
from sqlalchemy import create_engine, text

print("\nSelect database to reset sent status:")
print("1. Sai Rushi Kasyap (rushi)")
print("2. Santosh Anoushika Komala (anoushika)")
choice = input("Choice (1-2): ").strip()
db_name = "jobs_rushi.db" if choice == "1" else "jobs_anoushika.db"

engine = create_engine(
    f"sqlite:///{db_name}"
)

with engine.connect() as conn:

    conn.execute(
        text("""
        UPDATE jobs
        SET sent = 0
        WHERE id = 1
        """)
    )

    conn.commit()

print("Recruiter Reset")