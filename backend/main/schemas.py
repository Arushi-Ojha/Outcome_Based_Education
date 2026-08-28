from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from main.models import Role, UserStatus, KSADomain, BatchDuration, CourseCategory, POType

# ==========================================
# AUTH & USER SCHEMAS
# ==========================================

class EmailRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
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

class ProgramCreate(BaseModel):
    name: str
    batch_duration: BatchDuration
    department_id: int

class ProgramResponse(ProgramCreate):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# SUBJECT & OBE FRAMEWORK SCHEMAS
# ==========================================

class CourseBase(BaseModel):
    code: str
    name: str
    credits: int
    semester: int

class CourseCreate(BaseModel):
    code: str
    name: str
    credits: int
    semester: int
    department_id: int

class CourseResponse(CourseCreate):
    id: int

    class Config:
        from_attributes = True

class AssessmentCreate(BaseModel):
    name: str
    max_marks: float
    threshold_percentage: float = 65.0
    course_id: int

class IAMarkCreate(BaseModel):
    score: float
    evaluation_date: date
    usn: str
    assessment_id: int
    co_id: int

class IAMarkBulkCreate(BaseModel):
    marks: List[IAMarkCreate]
