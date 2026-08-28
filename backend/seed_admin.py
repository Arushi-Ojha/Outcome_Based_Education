import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main.database import SessionLocal
from main.models import UserInfo, Role, UserStatus
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

db = SessionLocal()
existing_admin = db.query(UserInfo).filter(UserInfo.name == 'OBE_BOSS').first()
if existing_admin:
    print("Admin user already exists!")
else:
    admin = UserInfo(
        name='OBE_BOSS',
        email='admin@obe.com',
        password_hash=get_password_hash('OBE2026'),
        role=Role.ADMIN,
        status=UserStatus.APPROVED
    )
    db.add(admin)
    db.commit()
    print("Admin user OBE_BOSS with password OBE2026 created successfully.")
