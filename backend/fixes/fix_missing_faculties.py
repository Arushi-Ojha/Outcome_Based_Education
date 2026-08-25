from database import engine
from sqlalchemy.orm import Session
import models
from datetime import datetime

def fix_missing_faculties():
    with Session(engine) as db:
        # Find all approved FACULTY and COORDINATORS
        approved_staff = db.query(models.UserInfo).filter(
            models.UserInfo.status == models.UserStatus.APPROVED,
            models.UserInfo.role.in_([models.Role.FACULTY, models.Role.COORDINATOR])
        ).all()
        
        count = 0
        for staff in approved_staff:
            existing = db.query(models.Faculty).filter(models.Faculty.user_id == staff.id).first()
            if not existing:
                new_faculty = models.Faculty(
                    user_id=staff.id,
                    department_id=staff.department_id,
                    joining_date=datetime.utcnow().date()
                )
                db.add(new_faculty)
                count += 1
                
        db.commit()
        print(f"Fixed! Auto-generated {count} missing Faculty profiles for previously approved staff.")

if __name__ == "__main__":
    fix_missing_faculties()
