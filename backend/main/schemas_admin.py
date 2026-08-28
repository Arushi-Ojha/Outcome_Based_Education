from pydantic import BaseModel, EmailStr
from typing import Optional
from main.models import BatchDuration

class DepartmentCreate(BaseModel):
    department_name: str
    department_id: str
    hod_name: str
    hod_email: EmailStr

class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    hod_email: str
    hod_password: str

class ProgramCreate(BaseModel):
    program_name: str
    program_id: str
    batch_year: str
    batch_duration: BatchDuration
    program_head_name: str
    program_head_email: EmailStr
    department_id: int

class ProgramResponse(BaseModel):
    id: int
    program_id: str
    name: str
    batch_year: str
    batch_duration: BatchDuration
    program_head_email: str
    program_head_password: str
