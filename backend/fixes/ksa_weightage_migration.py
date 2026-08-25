from database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            print("Cleaning up POs...")
            conn.execute(text("ALTER TABLE POs DROP COLUMN ksa_domain;"))
            conn.execute(text("ALTER TABLE POs DROP COLUMN ksa_level;"))
        except Exception as e:
            print(f"Skipping PO drop (already dropped or missing): {e}")

        try:
            print("Cleaning up COs...")
            conn.execute(text("ALTER TABLE COs DROP COLUMN ksa_domain;"))
            conn.execute(text("ALTER TABLE COs DROP COLUMN ksa_level;"))
        except Exception as e:
            print(f"Skipping CO drop (already dropped or missing): {e}")

        try:
            print("Restoring ksa_tag_id to COs...")
            conn.execute(text("ALTER TABLE COs ADD COLUMN ksa_tag_id INT NULL;"))
            conn.execute(text("ALTER TABLE COs ADD CONSTRAINT fk_co_ksatag FOREIGN KEY (ksa_tag_id) REFERENCES KSA_Tags(id) ON DELETE SET NULL;"))
        except Exception as e:
            print(f"Skipping ksa_tag_id addition to COs: {e}")

        try:
            print("Upgrading KSA_Tags with weightages...")
            conn.execute(text("ALTER TABLE KSA_Tags ADD COLUMN knowledge_weight FLOAT NOT NULL DEFAULT 0.0;"))
            conn.execute(text("ALTER TABLE KSA_Tags ADD COLUMN skill_weight FLOAT NOT NULL DEFAULT 0.0;"))
            conn.execute(text("ALTER TABLE KSA_Tags ADD COLUMN attitude_weight FLOAT NOT NULL DEFAULT 0.0;"))
        except Exception as e:
            print(f"Skipping KSA_Tags upgrade (already added): {e}")

        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
