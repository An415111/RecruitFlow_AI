import os
import sys
from sqlalchemy import create_engine, text

print("\nSelect database to check sent status:")
print("1. Sai Rushi Kasyap (rushi)")
print("2. Santosh Anoushika Komala (anoushika)")
choice = input("Choice (1-2): ").strip()
db_name = "jobs_rushi.db" if choice == "1" else "jobs_anoushika.db"

engine = create_engine(f"sqlite:///{db_name}")

with engine.connect() as conn:

    result = conn.execute(
        text(
            """
            SELECT id, email, sent
            FROM jobs
            """
        )
    )

    for row in result:
        print(row)