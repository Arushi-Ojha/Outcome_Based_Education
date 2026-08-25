from database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            print("Wiping existing student data to avoid FK conflicts...")
            conn.execute(text("DELETE FROM IA_Marks;"))
            conn.execute(text("DELETE FROM Student_Enrollments;"))
            conn.execute(text("DELETE FROM Student_Details;"))
            
            print("Altering Student_Details schema...")
            # Drop email
            conn.execute(text("ALTER TABLE Student_Details DROP COLUMN email;"))
            # Drop batch_year
            conn.execute(text("ALTER TABLE Student_Details DROP COLUMN batch_year;"))
            # Add semester
            conn.execute(text("ALTER TABLE Student_Details ADD COLUMN semester INT NOT NULL DEFAULT 1;"))
            
            conn.commit()
            print("Successfully executed student schema migration!")
        except Exception as e:
            print(f"Failed during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    run_migration()
