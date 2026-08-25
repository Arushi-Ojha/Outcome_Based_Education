from database import engine
from sqlalchemy import text

def run_migration():
    with engine.connect() as conn:
        try:
            print("Adding KSA columns to POs...")
            conn.execute(text("ALTER TABLE POs ADD COLUMN ksa_domain VARCHAR(20) NULL;"))
            conn.execute(text("ALTER TABLE POs ADD COLUMN ksa_level VARCHAR(10) NULL;"))
            
            print("Adding KSA columns to COs...")
            conn.execute(text("ALTER TABLE COs ADD COLUMN ksa_domain VARCHAR(20) NULL;"))
            conn.execute(text("ALTER TABLE COs ADD COLUMN ksa_level VARCHAR(10) NULL;"))
            
            print("Dropping redundant ksa_tag_id from COs...")
            # We must first drop the foreign key constraint
            # Let's dynamically find and drop the FK constraint for ksa_tag_id in COs
            fk_query = """
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = 'COs' AND COLUMN_NAME = 'ksa_tag_id' AND TABLE_SCHEMA = DATABASE();
            """
            result = conn.execute(text(fk_query)).fetchone()
            if result:
                constraint_name = result[0]
                conn.execute(text(f"ALTER TABLE COs DROP FOREIGN KEY {constraint_name};"))
            
            conn.execute(text("ALTER TABLE COs DROP COLUMN ksa_tag_id;"))
            
            conn.commit()
            print("Migration completed successfully!")
        except Exception as e:
            print(f"Migration failed or already applied: {e}")

if __name__ == "__main__":
    run_migration()
