from database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            print("Restoring ksa_domain to POs...")
            conn.execute(text("ALTER TABLE POs ADD COLUMN ksa_domain VARCHAR(20) NULL;"))
            conn.commit()
            print("Successfully restored ksa_domain to POs.")
        except Exception as e:
            print(f"Failed to restore ksa_domain to POs: {e}")

if __name__ == "__main__":
    run_migration()
