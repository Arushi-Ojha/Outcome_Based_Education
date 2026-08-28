from pydantic import BaseModel
from typing import Optional
from main.models import CourseCategory, CourseSubCategory

class CourseCreate(BaseModel):
    course_id: str
    name: str
    credits: int
    intended_semester: int
    intended_year: int
    program_id: int
    is_interdepartmental: bool = False
    target_department_id: Optional[int] = None
    course_category: CourseCategory
    sub_category: Optional[CourseSubCategory] = None

class CourseResponse(BaseModel):
    id: int
    course_id: str
    name: str
    credits: int
    intended_semester: int
    intended_year: int
    course_category: CourseCategory
