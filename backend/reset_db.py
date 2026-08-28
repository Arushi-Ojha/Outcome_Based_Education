import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main.database import SessionLocal, engine
from main.models import Base, UserInfo, Role, UserStatus
from passlib.context import CryptContext
from sqlalchemy import text

# Drop all tables
print("Dropping all database tables...")
with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    Base.metadata.drop_all(bind=conn)
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

# Recreate all tables
print("Recreating all database tables...")
Base.metadata.create_all(bind=engine)

# Re-seed Admin
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

db = SessionLocal()
print("Seeding admin credentials...")
admin = UserInfo(
    name='OBE_BOSS',
    email='admin@obe.com',
    password_hash=get_password_hash('OBE2026'),
    role=Role.ADMIN,
    status=UserStatus.APPROVED
)
db.add(admin)
db.commit()
print("Database reset successful! Admin user OBE_BOSS with password OBE2026 recreated.")
