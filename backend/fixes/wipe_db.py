from database import engine
from sqlalchemy import text
import models

def brute_force_wipe():
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        tables = conn.execute(text("SHOW TABLES;")).fetchall()
        for table in tables:
            table_name = table[0]
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`;"))
                print(f"Dropped {table_name}")
            except Exception as e:
                print(f"Failed to drop {table_name}: {e}")
        
        # Second pass for stubborn circular dependencies
        tables = conn.execute(text("SHOW TABLES;")).fetchall()
        for table in tables:
            table_name = table[0]
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`;"))
                print(f"Dropped {table_name} on second pass")
            except Exception as e:
                print(f"Failed to drop {table_name} on second pass: {e}")
                
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()
            
    print("Recreating tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Database wiped and updated successfully!")

if __name__ == "__main__":
    brute_force_wipe()
