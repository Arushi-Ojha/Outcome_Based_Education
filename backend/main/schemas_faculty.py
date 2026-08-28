from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# Assignment Schema
class FacultyAssignmentRequest(BaseModel):
    academic_year: str
    semester: int

# Bulk Upload Schemas
class StudentData(BaseModel):
    usn: str
    name: str
    program_id: int
    semester: int
    department_id: int

class BulkStudentUploadRequest(BaseModel):
    academic_term_id: int
    semester_number: int
    students: List[StudentData]

class AssessmentScore(BaseModel):
    assessment_id: int
    co_id: int
    score: float
    evaluation_date: date

class StudentMarks(BaseModel):
    usn: str
    marks: List[AssessmentScore]

class BulkMarksUploadRequest(BaseModel):
    student_marks: List[StudentMarks]

# Faculty Management Schemas
class FacultyUploadItem(BaseModel):
    employee_id: str
    name: str
    speciality: str
    email: EmailStr

class FacultyUploadRequest(BaseModel):
    academic_year: str
    semester: int
    faculty_list: List[FacultyUploadItem]

class FacultyCourseResponse(BaseModel):
    employee_id: Optional[str]
    name: str
    speciality: Optional[str]
    email: EmailStr
    total_courses_assigned: int

class FacultyDropdownResponse(BaseModel):
    id: int # Faculty.id
    user_id: int
    employee_id: Optional[str]
    name: str
    email: str
    speciality: Optional[str]
