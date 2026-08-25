from sqlalchemy import text
from database import engine

def apply_migrations():
    try:
        with engine.begin() as conn:
            # We add the column to Program_Curriculum
            conn.execute(text("ALTER TABLE Program_Curriculum ADD COLUMN elective_basket_id INT NULL;"))
            
            # Since the Elective_Baskets table was created by create_all, we can now add the foreign key
            conn.execute(text("ALTER TABLE Program_Curriculum ADD CONSTRAINT fk_elective_basket FOREIGN KEY (elective_basket_id) REFERENCES Elective_Baskets(id) ON DELETE SET NULL;"))
            
            print("Successfully updated Program_Curriculum table with elective_basket_id!")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    apply_migrations()
