from sqlalchemy import text
from database import engine

def fix_otp_table():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE OTP_Verifications MODIFY COLUMN expires_at DATETIME NOT NULL;"))
            print("Successfully changed expires_at to DATETIME.")
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    fix_otp_table()
