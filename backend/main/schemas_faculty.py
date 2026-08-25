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
    academic_course_id: int
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
