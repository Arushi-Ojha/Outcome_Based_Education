from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from main.database import get_db
from main.auth import get_current_admin
from main.schemas_admin import DepartmentCreate, DepartmentResponse, ProgramCreate, ProgramResponse
from main.crud_admin import create_department, create_program
from main import schemas
from main import schemas_faculty
from main import crud_faculty
from typing import List

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)]
)

@router.post("/department", response_model=DepartmentResponse)
def api_create_department(dept_data: DepartmentCreate, db: Session = Depends(get_db)):
    return create_department(db, dept_data)

@router.post("/program", response_model=ProgramResponse)
def api_create_program(prog_data: ProgramCreate, db: Session = Depends(get_db)):
    return create_program(db, prog_data)

@router.post("/reset-password")
def api_reset_password(payload: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    from main.crud_admin import reset_user_password
    return reset_user_password(db, payload.email)

@router.post("/courses/{course_id}/faculty-upload")
def upload_faculty_for_course(course_id: int, department_id: int, payload: schemas_faculty.FacultyUploadRequest, db: Session = Depends(get_db)):
    # Admin must specify the department_id
    return crud_faculty.upload_and_assign_faculty(db, course_id, payload, department_id)

@router.get("/courses/{course_id}/assigned-faculty", response_model=List[schemas_faculty.FacultyCourseResponse])
def get_assigned_faculty(course_id: int, db: Session = Depends(get_db)):
    return crud_faculty.get_assigned_faculty(db, course_id)

@router.get("/departments/{department_id}/faculty-dropdown", response_model=List[schemas_faculty.FacultyDropdownResponse])
def get_faculty_dropdown(department_id: int, db: Session = Depends(get_db)):
    return crud_faculty.get_faculty_dropdown(db, department_id)
