from sqlalchemy.orm import Session
from datetime import datetime
from main import models, schemas, schemas_hod
from main.auth import get_password_hash
import secrets
from main.email_utils import send_credentials_email

# ==========================================
# DEPARTMENT SETUP
# ==========================================
def create_department(db: Session, dept: schemas.DepartmentCreate, user_id: int):
    # 1. Create the Department
    db_dept = models.Department(**dept.model_dump())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    
    # 2. Assign the HOD to this department in UserInfo
    user = db.query(models.UserInfo).filter(models.UserInfo.id == user_id).first()
    user.department_id = db_dept.id
    
    # 3. Create the formal HOD role record
    db_hod = models.HOD(user_id=user_id, department_id=db_dept.id, start_date=datetime.utcnow().date())
    db.add(db_hod)
    db.commit()
    
    return db_dept

# ==========================================
# STAFF APPROVALS
# ==========================================
def get_pending_staff(db: Session, department_id: int):
    return db.query(models.UserInfo).filter(
        models.UserInfo.department_id == department_id,
        models.UserInfo.status == models.UserStatus.PENDING,
        models.UserInfo.role.in_([models.Role.FACULTY, models.Role.COORDINATOR])
    ).all()

def approve_staff_member(db: Session, user_id: int, department_id: int):
    user = db.query(models.UserInfo).filter(
        models.UserInfo.id == user_id,
        models.UserInfo.department_id == department_id
    ).first()
    if user:
        user.status = models.UserStatus.APPROVED
        
        # Auto-create Faculty profile for FACULTY and COORDINATOR roles
        if user.role in [models.Role.FACULTY, models.Role.COORDINATOR]:
            existing_faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user.id).first()
            if not existing_faculty:
                new_faculty = models.Faculty(
                    user_id=user.id,
                    department_id=department_id,
                    joining_date=datetime.utcnow().date()
                )
                db.add(new_faculty)
                
        db.commit()
        return user
    return None

# ==========================================
# STAFF CREATION (BY HOD)
# ==========================================
def create_staff_user(db: Session, user_data: schemas_hod.UserCreate, department_id: int, role: models.Role):
    # Check if email exists
    if db.query(models.UserInfo).filter(models.UserInfo.email == user_data.email).first():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User with this email already exists")

    raw_password = secrets.token_urlsafe(8)
    new_user = models.UserInfo(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(raw_password),
        role=role,
        status=models.UserStatus.APPROVED,
        department_id=department_id
    )
    db.add(new_user)
    db.flush()

    if role in [models.Role.FACULTY, models.Role.COORDINATOR]:
        new_faculty = models.Faculty(
            user_id=new_user.id,
            department_id=department_id,
            joining_date=datetime.utcnow().date()
        )
        db.add(new_faculty)

    db.commit()
    db.refresh(new_user)

    send_credentials_email(user_data.email, role.value, raw_password)

    return schemas_hod.UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role.value,
        password=raw_password
    )

def reset_user_password(db: Session, email: str, department_id: int):
    user = db.query(models.UserInfo).filter(
        models.UserInfo.email == email,
        models.UserInfo.department_id == department_id
    ).first()
    
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found in your department")
        
    raw_password = secrets.token_urlsafe(8)
    user.password_hash = get_password_hash(raw_password)
    db.commit()
    
    send_credentials_email(user.email, user.role.value, raw_password)
    return {"msg": f"Password reset successfully. New credentials sent to {email}"}

# ==========================================
# CURRICULUM BLUEPRINTING
# ==========================================
def create_program(db: Session, course: schemas_hod.ProgramCreate, department_id: int):
    db_course = models.Program(**course.model_dump(), department_id=department_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_program(db: Session, course_id: int, course_data: schemas_hod.ProgramUpdate, department_id: int):
    db_course = db.query(models.Program).filter(
        models.Program.id == course_id,
        models.Program.department_id == department_id
    ).first()
    if db_course:
        for key, value in course_data.model_dump(exclude_unset=True).items():
            setattr(db_course, key, value)
        db.commit()
        db.refresh(db_course)
    return db_course

def create_course(db: Session, course: schemas_hod.CourseCreate, department_id: int):
    db_course = models.Course(**course.model_dump(), department_id=department_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def bulk_insert_curriculum(db: Session, mappings: schemas_hod.CurriculumMappingBulkCreate):
    db_mappings = [models.CourseCurriculum(**m.model_dump()) for m in mappings.mappings]
    db.add_all(db_mappings)
    db.commit()
    return len(db_mappings)

def create_elective_combination(db: Session, combination: schemas_hod.ElectiveCombinationCreate, program_id: int, sem_number: int):
    db_combination = models.ElectiveCombination(**combination.model_dump(), program_id=program_id, semester_number=sem_number)
    db.add(db_combination)
    db.commit()
    db.refresh(db_combination)
    return db_combination

def add_courses_to_combination(db: Session, combination_id: int, program_id: int, course_ids: list[int]):
    combination = db.query(models.ElectiveCombination).filter(models.ElectiveCombination.id == combination_id).first()
    if not combination:
        return False
    
    mappings = [
        models.CourseCurriculum(
            program_id=program_id,
            course_id=sid,
            semester_number=combination.semester_number,
            course_category=models.CourseCategory.MAJOR, # Electives
            is_mandatory=False,
            elective_combination_id=combination_id
        ) for sid in course_ids
    ]
    db.add_all(mappings)
    db.commit()
    return True

def get_semester_structure(db: Session, program_id: int, semester_number: int):
    # Fetch mandatory subjects
    mandatory = db.query(models.CourseCurriculum).filter(
        models.CourseCurriculum.program_id == program_id,
        models.CourseCurriculum.semester_number == semester_number,
        models.CourseCurriculum.is_mandatory == True,
        models.CourseCurriculum.elective_combination_id == None
    ).all()
    
    # Fetch combinations
    combinations = db.query(models.ElectiveCombination).filter(
        models.ElectiveCombination.program_id == program_id,
        models.ElectiveCombination.semester_number == semester_number
    ).all()
    
    combination_data = []
    for c in combinations:
        # Fetch subjects for this combination
        subjects = db.query(models.CourseCurriculum).filter(
            models.CourseCurriculum.elective_combination_id == c.id
        ).all()
        combination_data.append({
            "combination_id": c.id,
            "name": c.name,
            "required_selection_count": c.required_selection_count,
            "subjects": [s.course_id for s in subjects]
        })
        
    return {
        "mandatory_subjects": [m.course_id for m in mandatory],
        "elective_combinations": combination_data
    }

# ==========================================
# OBE FRAMEWORK CRUD (Generic logic)
# ==========================================
def get_model_by_id(db: Session, model_class, record_id: int):
    return db.query(model_class).filter(model_class.id == record_id).first()

def get_all_models(db: Session, model_class, **filters):
    return db.query(model_class).filter_by(**filters).all()

def create_model(db: Session, model_class, data: dict):
    new_record = model_class(**data)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def update_model(db: Session, record, update_data: dict):
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record

def delete_model(db: Session, record):
    db.delete(record)
    db.commit()

# ==========================================
# COURSE OUTCOMES & CO-PO MAPPING
# ==========================================
def create_co(db: Session, co_data: schemas_hod.COCreate):
    db_co = models.CO(**co_data.model_dump())
    db.add(db_co)
    db.commit()
    db.refresh(db_co)
    return db_co

def get_cos_for_subject(db: Session, course_id: int):
    return db.query(models.CO).filter(models.CO.course_id == course_id).all()

def clone_cos(db: Session, source_course_id: int, target_course_id: int):
    source_cos = db.query(models.CO).filter(models.CO.course_id == source_course_id).all()
    if not source_cos:
        return 0
    
    cloned_cos = [
        models.CO(
            statement=co.statement,
            course_id=target_course_id,
            ksa_tag_id=co.ksa_tag_id
        ) for co in source_cos
    ]
    db.add_all(cloned_cos)
    db.commit()
    return len(cloned_cos)

def bulk_map_co_po(db: Session, mapping_data: schemas_hod.COPOMappingBulkCreate):
    mappings = [models.COPOMapping(**m.model_dump()) for m in mapping_data.mappings]
    db.add_all(mappings)
    db.commit()
    return len(mappings)

def get_co_po_mappings(db: Session, course_id: int):
    return db.query(models.COPOMapping).join(models.CO).filter(models.CO.course_id == course_id).all()

def bulk_map_peo_ga(db: Session, mapping_data: schemas_hod.PEOGAMappingBulkCreate):
    mappings = [models.PEOGAMapping(**m.model_dump()) for m in mapping_data.mappings]
    db.add_all(mappings)
    db.commit()
    return len(mappings)

def bulk_map_po_peo(db: Session, mapping_data: schemas_hod.POPEOMappingBulkCreate):
    mappings = [models.POPEOMapping(**m.model_dump()) for m in mapping_data.mappings]
    db.add_all(mappings)
    db.commit()
    return len(mappings)

def bulk_map_assessment_co(db: Session, mapping_data: schemas_hod.AssessmentCOMappingBulkCreate):
    mappings = [models.AssessmentCOMapping(**m.model_dump()) for m in mapping_data.mappings]
    db.add_all(mappings)
    db.commit()
    return len(mappings)

def create_ksa_tag(db: Session, ksa: schemas_hod.KSATagCreate):
    db_ksa = models.KSATag(**ksa.model_dump())
    db.add(db_ksa)
    db.commit()
    db.refresh(db_ksa)
    return db_ksa

def get_ksa_tags(db: Session):
    return db.query(models.KSATag).all()

def assign_faculty_to_subject(db: Session, faculty_id: int, course_id: int, academic_year: str, semester: int):
    # Check if already assigned
    existing = db.query(models.CourseCoordinator).filter(
        models.CourseCoordinator.faculty_id == faculty_id,
        models.CourseCoordinator.course_id == course_id,
        models.CourseCoordinator.academic_year == academic_year,
        models.CourseCoordinator.semester == semester
    ).first()
    
    if existing:
        return existing
        
    assignment = models.CourseCoordinator(
        faculty_id=faculty_id,
        course_id=course_id,
        academic_year=academic_year,
        semester=semester
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment
