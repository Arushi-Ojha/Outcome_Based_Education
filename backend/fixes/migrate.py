import os
from sqlalchemy import text
from database import engine

def apply_migrations():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE Users_Info ADD COLUMN status ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL DEFAULT 'PENDING';"))
            print("Successfully added 'status' column to Users_Info table.")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    apply_migrations()
