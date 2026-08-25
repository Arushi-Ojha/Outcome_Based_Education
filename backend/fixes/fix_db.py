from database import engine
import models
from sqlalchemy import text

def check_and_fix_db():
    with engine.connect() as conn:
        try:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            conn.execute(text("DROP TABLE IF EXISTS Course_Curriculum;"))
            conn.execute(text("DROP TABLE IF EXISTS Elective_Baskets;"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            print("Successfully dropped stale tables.")
            conn.commit()
        except Exception as e:
            print(f"Error dropping: {e}")
            
    print("Recreating tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Done!")

if __name__ == "__main__":
    check_and_fix_db()
