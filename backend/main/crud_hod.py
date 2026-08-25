from sqlalchemy.orm import Session
from datetime import datetime
from main import models, schemas, schemas_hod

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
# CURRICULUM BLUEPRINTING
# ==========================================
def create_academic_course(db: Session, course: schemas_hod.AcademicCourseCreate, department_id: int):
    db_course = models.AcademicCourse(**course.model_dump(), department_id=department_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_academic_course(db: Session, course_id: int, course_data: schemas_hod.AcademicCourseUpdate, department_id: int):
    db_course = db.query(models.AcademicCourse).filter(
        models.AcademicCourse.id == course_id,
        models.AcademicCourse.department_id == department_id
    ).first()
    if db_course:
        for key, value in course_data.model_dump(exclude_unset=True).items():
            setattr(db_course, key, value)
        db.commit()
        db.refresh(db_course)
    return db_course

def create_subject(db: Session, subject: schemas_hod.SubjectCreate, department_id: int):
    db_subject = models.Subject(**subject.model_dump(), department_id=department_id)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

def bulk_insert_curriculum(db: Session, mappings: schemas_hod.CurriculumMappingBulkCreate):
    db_mappings = [models.CourseCurriculum(**m.model_dump()) for m in mappings.mappings]
    db.add_all(db_mappings)
    db.commit()
    return len(db_mappings)

def create_elective_basket(db: Session, basket: schemas_hod.ElectiveBasketCreate, academic_course_id: int, sem_number: int):
    db_basket = models.ElectiveBasket(**basket.model_dump(), academic_course_id=academic_course_id, semester_number=sem_number)
    db.add(db_basket)
    db.commit()
    db.refresh(db_basket)
    return db_basket

def add_subjects_to_basket(db: Session, basket_id: int, academic_course_id: int, subject_ids: list[int]):
    basket = db.query(models.ElectiveBasket).filter(models.ElectiveBasket.id == basket_id).first()
    if not basket:
        return False
    
    mappings = [
        models.CourseCurriculum(
            academic_course_id=academic_course_id,
            subject_id=sid,
            semester_number=basket.semester_number,
            subject_category=models.SubjectCategory.MAJOR, # Electives
            is_mandatory=False,
            elective_basket_id=basket_id
        ) for sid in subject_ids
    ]
    db.add_all(mappings)
    db.commit()
    return True

def get_semester_structure(db: Session, academic_course_id: int, semester_number: int):
    # Fetch mandatory subjects
    mandatory = db.query(models.CourseCurriculum).filter(
        models.CourseCurriculum.academic_course_id == academic_course_id,
        models.CourseCurriculum.semester_number == semester_number,
        models.CourseCurriculum.is_mandatory == True,
        models.CourseCurriculum.elective_basket_id == None
    ).all()
    
    # Fetch baskets
    baskets = db.query(models.ElectiveBasket).filter(
        models.ElectiveBasket.academic_course_id == academic_course_id,
        models.ElectiveBasket.semester_number == semester_number
    ).all()
    
    basket_data = []
    for b in baskets:
        # Fetch subjects for this basket
        subjects = db.query(models.CourseCurriculum).filter(
            models.CourseCurriculum.elective_basket_id == b.id
        ).all()
        basket_data.append({
            "basket_id": b.id,
            "name": b.name,
            "required_selection_count": b.required_selection_count,
            "subjects": [c.subject_id for c in subjects]
        })
        
    return {
        "mandatory_subjects": [m.subject_id for m in mandatory],
        "elective_baskets": basket_data
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

def get_cos_for_subject(db: Session, subject_id: int):
    return db.query(models.CO).filter(models.CO.subject_id == subject_id).all()

def clone_cos(db: Session, source_subject_id: int, target_subject_id: int):
    source_cos = db.query(models.CO).filter(models.CO.subject_id == source_subject_id).all()
    if not source_cos:
        return 0
    
    cloned_cos = [
        models.CO(
            statement=co.statement,
            subject_id=target_subject_id,
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

def get_co_po_mappings(db: Session, subject_id: int):
    return db.query(models.COPOMapping).join(models.CO).filter(models.CO.subject_id == subject_id).all()

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

def assign_faculty_to_subject(db: Session, faculty_id: int, subject_id: int, academic_year: str, semester: int):
    # Check if already assigned
    existing = db.query(models.SubjectCoordinator).filter(
        models.SubjectCoordinator.faculty_id == faculty_id,
        models.SubjectCoordinator.subject_id == subject_id,
        models.SubjectCoordinator.academic_year == academic_year,
        models.SubjectCoordinator.semester == semester
    ).first()
    
    if existing:
        return existing
        
    assignment = models.SubjectCoordinator(
        faculty_id=faculty_id,
        subject_id=subject_id,
        academic_year=academic_year,
        semester=semester
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment
