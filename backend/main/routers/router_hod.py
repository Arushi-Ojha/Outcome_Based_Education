from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from main.database import get_db
from main import models, schemas, schemas_hod, crud_hod, auth

router = APIRouter(prefix="/hod", tags=["HOD Domain"])

# ==========================================
# 1. DEPARTMENT SETUP
# ==========================================
@router.post("/departments", response_model=schemas.DepartmentResponse)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    if current_hod.department_id:
        raise HTTPException(status_code=400, detail="You are already assigned to a department")
    return crud_hod.create_department(db, dept, current_hod.id)

# ==========================================
# 2. STAFF APPROVALS
# ==========================================
@router.get("/staff/pending", response_model=List[schemas.UserResponse])
def get_pending_staff(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_pending_staff(db, current_hod.department_id)

@router.patch("/staff/{user_id}/approve")
def approve_staff(user_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    user = crud_hod.approve_staff_member(db, user_id, current_hod.department_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or not in your department")
    return {"msg": f"User {user.name} approved successfully"}

# ==========================================
# 2. CURRICULUM BLUEPRINTING
# ==========================================
@router.post("/academic-courses", response_model=schemas_hod.AcademicCourseResponse)
def create_academic_course(course: schemas_hod.AcademicCourseCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_academic_course(db, course, current_hod.department_id)

@router.put("/academic-courses/{course_id}", response_model=schemas_hod.AcademicCourseResponse)
def update_academic_course(course_id: int, course: schemas_hod.AcademicCourseUpdate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    updated_course = crud_hod.update_academic_course(db, course_id, course, current_hod.department_id)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Academic Course not found in your department")
    return updated_course

from sqlalchemy.exc import IntegrityError

@router.post("/subjects", response_model=schemas_hod.SubjectResponse)
def create_subject(subject: schemas_hod.SubjectCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    try:
        return crud_hod.create_subject(db, subject, current_hod.department_id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Subject with code '{subject.code}' already exists in the database!")

@router.post("/academic-courses/mapping")
def bulk_mapping(mappings: schemas_hod.CurriculumMappingBulkCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    count = crud_hod.bulk_insert_curriculum(db, mappings)
    return {"msg": f"Curriculum mapped successfully. Inserted {count} records."}

@router.post("/academic-courses/{academic_course_id}/semester/{sem_number}/baskets", response_model=schemas_hod.ElectiveBasketResponse)
def create_basket(academic_course_id: int, sem_number: int, basket: schemas_hod.ElectiveBasketCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_elective_basket(db, basket, academic_course_id, sem_number)

@router.post("/academic-courses/baskets/{basket_id}/subjects")
def add_subjects_to_basket(basket_id: int, payload: schemas_hod.BasketCourseAdd, academic_course_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    success = crud_hod.add_subjects_to_basket(db, basket_id, academic_course_id, payload.subject_ids)
    if not success:
        raise HTTPException(status_code=404, detail="Elective Basket not found")
    return {"msg": f"Added {len(payload.subject_ids)} subjects to basket"}

@router.get("/academic-courses/{academic_course_id}/semester/{sem_number}/structure")
def get_semester_structure(academic_course_id: int, sem_number: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_semester_structure(db, academic_course_id, sem_number)

# ==========================================
# 3. OBE FRAMEWORK CRUD
# ==========================================
# GAs
@router.post("/obe/gas", response_model=schemas_hod.GAResponse)
def create_ga(ga: schemas_hod.GACreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_model(db, models.GA, ga.model_dump())

@router.get("/obe/gas", response_model=List[schemas_hod.GAResponse])
def get_gas(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.GA)

@router.delete("/obe/gas/{ga_id}")
def delete_ga(ga_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    ga = crud_hod.get_model_by_id(db, models.GA, ga_id)
    if not ga: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, ga)
    return {"msg": "Deleted successfully"}

# PEOs
@router.post("/obe/peos", response_model=schemas_hod.PEOResponse)
def create_peo(peo: schemas_hod.PEOCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    data = peo.model_dump()
    data["department_id"] = current_hod.department_id
    return crud_hod.create_model(db, models.PEO, data)

@router.get("/obe/peos", response_model=List[schemas_hod.PEOResponse])
def get_peos(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.PEO, department_id=current_hod.department_id)

@router.delete("/obe/peos/{peo_id}")
def delete_peo(peo_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    peo = crud_hod.get_model_by_id(db, models.PEO, peo_id)
    if not peo or peo.department_id != current_hod.department_id: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, peo)
    return {"msg": "Deleted successfully"}

# POs
@router.post("/obe/pos", response_model=schemas_hod.POResponse)
def create_po(po: schemas_hod.POCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    data = po.model_dump()
    data["department_id"] = current_hod.department_id
    return crud_hod.create_model(db, models.PO, data)

@router.get("/obe/pos", response_model=List[schemas_hod.POResponse])
def get_pos(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.PO, department_id=current_hod.department_id)

@router.delete("/obe/pos/{po_id}")
def delete_po(po_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    po = crud_hod.get_model_by_id(db, models.PO, po_id)
    if not po or po.department_id != current_hod.department_id: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, po)
    return {"msg": "Deleted successfully"}

# KSA Tags
@router.post("/obe/ksas", response_model=schemas_hod.KSATagResponse)
def create_ksa(ksa: schemas_hod.KSATagCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_model(db, models.KSATag, ksa.model_dump())

@router.get("/obe/ksas", response_model=List[schemas_hod.KSATagResponse])
def get_ksas(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.KSATag)

@router.delete("/obe/ksas/{ksa_id}")
def delete_ksa(ksa_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    ksa = crud_hod.get_model_by_id(db, models.KSATag, ksa_id)
    if not ksa: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, ksa)
    return {"msg": "Deleted successfully"}



@router.post("/obe/mapping/peo-ga")
def map_peo_ga(payload: schemas_hod.PEOGAMappingBulkCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    count = crud_hod.bulk_map_peo_ga(db, payload)
    return {"msg": f"Successfully created {count} PEO-GA mappings"}

@router.post("/obe/mapping/po-peo")
def map_po_peo(payload: schemas_hod.POPEOMappingBulkCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    count = crud_hod.bulk_map_po_peo(db, payload)
    return {"msg": f"Successfully created {count} PO-PEO mappings"}



@router.post("/obe/ksas", response_model=schemas_hod.KSATagResponse)
def create_ksa_tag(ksa: schemas_hod.KSATagCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_ksa_tag(db, ksa)

@router.get("/obe/ksas", response_model=List[schemas_hod.KSATagResponse])
def get_ksa_tags(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_ksa_tags(db)
