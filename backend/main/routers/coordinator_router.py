from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from main.database import get_db
from main import models, schemas, auth

router = APIRouter(prefix="/coordinator", tags=["Coordinator Domain"])

from typing import List
from main import schemas_hod
from main import crud_faculty, crud_hod
from main import schemas_faculty

@router.post("/courses/{course_id}/faculty-upload")
def upload_faculty_for_course(course_id: int, payload: schemas_faculty.FacultyUploadRequest, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    # Coordinator manages their own department
    return crud_faculty.upload_and_assign_faculty(db, course_id, payload, current_coordinator.department_id)

@router.get("/courses/{course_id}/assigned-faculty", response_model=List[schemas_faculty.FacultyCourseResponse])
def get_assigned_faculty(course_id: int, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    return crud_faculty.get_assigned_faculty(db, course_id)

@router.get("/departments/my-department/faculty-dropdown", response_model=List[schemas_faculty.FacultyDropdownResponse])
def get_faculty_dropdown(db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    return crud_faculty.get_faculty_dropdown(db, current_coordinator.department_id)


@router.post("/course-outcomes", response_model=schemas_hod.COResponse)
def create_course_outcome(co: schemas_hod.COCreate, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    return crud_hod.create_co(db, co)

@router.get("/course-outcomes/{course_id}", response_model=List[schemas_hod.COResponse])
def get_cos(course_id: int, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    return crud_hod.get_cos_for_subject(db, course_id)

@router.post("/course-outcomes/clone")
def clone_cos(payload: schemas_hod.CloneCORequest, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    count = crud_hod.clone_cos(db, payload.source_course_id, payload.target_course_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="No COs found in the source subject")
    return {"msg": f"Successfully cloned {count} COs to the target subject"}

@router.post("/courses/mappings/co-po")
def map_co_po(payload: schemas_hod.COPOMappingBulkCreate, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    count = crud_hod.bulk_map_co_po(db, payload)
    return {"msg": f"Successfully created {count} CO-PO mappings"}

@router.get("/courses/{course_id}/mappings/co-po", response_model=List[schemas_hod.COPOMappingResponse])
def get_co_po_mapping(course_id: int, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    return crud_hod.get_co_po_mappings(db, course_id)

@router.post("/assessments")
def create_assessment(assessment: schemas.AssessmentCreate, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    new_assessment = models.Assessment(**assessment.model_dump())
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return {"msg": "Assessment created successfully", "id": new_assessment.id}

@router.post("/assessments/mappings/co")
def map_assessment_co(payload: schemas_hod.AssessmentCOMappingBulkCreate, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    count = crud_hod.bulk_map_assessment_co(db, payload)
    return {"msg": f"Successfully created {count} Assessment-CO mappings"}

from main import schemas_faculty

@router.post("/courses/{course_id}/assign-faculty/{user_id}")
def assign_faculty_to_subject(course_id: int, user_id: int, payload: schemas_faculty.FacultyAssignmentRequest, db: Session = Depends(get_db), current_coordinator: models.UserInfo = Depends(auth.get_current_coordinator)):
    # Look up the Faculty record using the User ID
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty record not found for this User ID. Make sure the user is registered as a faculty and has completed their profile.")
        
    assignment = crud_hod.assign_faculty_to_subject(db, faculty.id, course_id, payload.academic_year, payload.semester)
    return {"msg": "Faculty securely assigned to subject", "assignment_id": assignment.id}
