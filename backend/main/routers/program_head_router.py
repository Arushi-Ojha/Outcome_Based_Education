from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from main.database import get_db
from main.auth import get_current_program_head
from main.schemas_program_head import CourseCreate, CourseResponse
from main.crud_program_head import create_course

router = APIRouter(
    prefix="/program-head",
    tags=["program head"],
    dependencies=[Depends(get_current_program_head)]
)

@router.post("/course", response_model=CourseResponse)
def api_create_course(course_data: CourseCreate, db: Session = Depends(get_db)):
    return create_course(db, course_data)

from main import schemas_hod, crud_hod
from fastapi import HTTPException

@router.post("/programs/{program_id}/semesters/{sem_number}/combinations", response_model=schemas_hod.ElectiveCombinationResponse)
def create_combination(program_id: int, sem_number: int, combination: schemas_hod.ElectiveCombinationCreate, db: Session = Depends(get_db)):
    return crud_hod.create_elective_combination(db, combination, program_id, sem_number)

@router.post("/combinations/{combination_id}/courses")
def add_courses_to_combination(combination_id: int, payload: schemas_hod.CombinationCourseAdd, program_id: int, db: Session = Depends(get_db)):
    success = crud_hod.add_courses_to_combination(db, combination_id, program_id, payload.course_ids)
    if not success:
        raise HTTPException(status_code=404, detail="Elective Combination not found")
    return {"msg": f"Added {len(payload.course_ids)} courses to combination"}
