from sqlalchemy.orm import Session
from fastapi import HTTPException
from main.models import Course, CourseCategory, Department, Program
from main.schemas_program_head import CourseCreate, CourseResponse

def create_course(db: Session, course_data: CourseCreate):
    # Check if course_id exists
    if db.query(Course).filter(Course.course_id == course_data.course_id).first():
        raise HTTPException(status_code=400, detail="Course with this ID already exists")

    if not db.query(Program).filter(Program.id == course_data.program_id).first():
         raise HTTPException(status_code=404, detail="Program not found")

    if course_data.is_interdepartmental:
        if not course_data.target_department_id:
            raise HTTPException(status_code=400, detail="Target department must be specified for interdepartmental courses")
        if not db.query(Department).filter(Department.id == course_data.target_department_id).first():
            raise HTTPException(status_code=404, detail="Target department not found")
    else:
        # If not interdepartmental, it shouldn't have a target department
        course_data.target_department_id = None

    if course_data.course_category in (CourseCategory.MAJOR, CourseCategory.MINOR):
        if not course_data.sub_category:
            raise HTTPException(status_code=400, detail="Sub category is required for Major/Minor courses")
    else:
        course_data.sub_category = None

    new_course = Course(
        course_id=course_data.course_id,
        name=course_data.name,
        credits=course_data.credits,
        intended_semester=course_data.intended_semester,
        intended_year=course_data.intended_year,
        program_id=course_data.program_id,
        is_interdepartmental=course_data.is_interdepartmental,
        target_department_id=course_data.target_department_id,
        course_category=course_data.course_category,
        sub_category=course_data.sub_category
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return CourseResponse(
        id=new_course.id,
        course_id=new_course.course_id,
        name=new_course.name,
        credits=new_course.credits,
        intended_semester=new_course.intended_semester,
        intended_year=new_course.intended_year,
        course_category=new_course.course_category
    )
