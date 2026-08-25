from database import engine
from sqlalchemy.orm import Session
from sqlalchemy import text
import models

def create_default_term():
    with Session(engine) as db:
        try:
            # Check if any term exists
            term = db.query(models.AcademicTerm).first()
            if not term:
                print("No AcademicTerm found. Creating a default one with ID 1...")
                # We can execute a raw SQL to ensure ID=1, or just let autoincrement do it (if empty, it will be 1).
                # But to be safe if autoincrement is weird, we can specify ID.
                db.execute(text("INSERT INTO Academic_Terms (id, term_name, start_date, end_date) VALUES (1, 'Fall 2024', '2024-08-01', '2024-12-31')"))
                db.commit()
                print("Default AcademicTerm created successfully!")
            else:
                print(f"An AcademicTerm already exists with ID: {term.id}. Please use this ID in your payload instead of 1.")
        except Exception as e:
            print(f"Error creating AcademicTerm: {e}")

if __name__ == "__main__":
    create_default_term()
