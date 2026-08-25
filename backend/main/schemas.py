from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from main.models import Role, UserStatus, KSADomain, DegreeType, SubjectCategory, POType

# ==========================================
# AUTH & USER SCHEMAS
# ==========================================

class EmailRequest(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role
    otp: str

class ProfileComplete(BaseModel):
    department_id: int

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role
    status: UserStatus
    department_id: Optional[int]

    class Config:
        from_attributes = True

# ==========================================
# DEPARTMENT & COURSE SCHEMAS
# ==========================================

class DepartmentCreate(BaseModel):
    name: str
    code: str

class DepartmentResponse(DepartmentCreate):
    id: int

    class Config:
        from_attributes = True

class AcademicCourseCreate(BaseModel):
    name: str
    degree_type: DegreeType
    department_id: int

class AcademicCourseResponse(AcademicCourseCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# SUBJECT & OBE FRAMEWORK SCHEMAS
# ==========================================

class SubjectBase(BaseModel):
    code: str
    name: str
    credits: int
    semester: int

class SubjectCreate(BaseModel):
    code: str
    name: str
    credits: int
    semester: int
    department_id: int

class SubjectResponse(SubjectCreate):
    id: int

    class Config:
        from_attributes = True

class AssessmentCreate(BaseModel):
    name: str
    max_marks: float
    threshold_percentage: float = 65.0
    subject_id: int

class IAMarkCreate(BaseModel):
    score: float
    evaluation_date: date
    usn: str
    assessment_id: int
    co_id: int

class IAMarkBulkCreate(BaseModel):
    marks: List[IAMarkCreate]
