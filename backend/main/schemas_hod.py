from pydantic import BaseModel
from typing import List, Optional
from main.models import BatchDuration, CourseCategory, KSADomain, POType

# Academic Courses (formerly Programs)
class ProgramBase(BaseModel):
    name: str
    batch_duration: BatchDuration
    
class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(BaseModel):
    name: Optional[str] = None
    batch_duration: Optional[BatchDuration] = None

class ProgramResponse(ProgramBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

# Subjects (formerly Courses)
class CourseBase(BaseModel):
    code: str
    name: str
    credits: int
    semester: int

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

# Elective Combinations
class ElectiveCombinationBase(BaseModel):
    name: str
    required_selection_count: int

class ElectiveCombinationCreate(ElectiveCombinationBase):
    pass

class ElectiveCombinationResponse(ElectiveCombinationBase):
    id: int
    program_id: int
    semester_number: int
    class Config:
        from_attributes = True

# Curriculum
class CurriculumMappingCreate(BaseModel):
    program_id: int
    course_id: int
    semester_number: int
    course_category: CourseCategory
    is_mandatory: bool = True
    elective_combination_id: Optional[int] = None

class CurriculumMappingBulkCreate(BaseModel):
    mappings: List[CurriculumMappingCreate]

class CombinationCourseAdd(BaseModel):
    course_ids: List[int]

# OBE Framework (GAs, PEOs, POs, KSAs)
class GABase(BaseModel):
    name: str
    description: Optional[str] = None
    nheqf_level: float

class GACreate(GABase):
    pass

class GAResponse(GABase):
    id: int
    class Config:
        from_attributes = True

class PEOBase(BaseModel):
    statement: str

class PEOCreate(PEOBase):
    pass

class PEOResponse(PEOBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

class POBase(BaseModel):
    type: POType
    statement: str
    ksa_domain: Optional[KSADomain] = None

class POCreate(POBase):
    pass

class POResponse(POBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

class KSATagBase(BaseModel):
    domain: KSADomain
    tag_level: str
    description: Optional[str] = None

class KSATagCreate(KSATagBase):
    pass

class KSATagResponse(KSATagBase):
    id: int
    class Config:
        from_attributes = True

# Course Outcomes (COs)
class COBase(BaseModel):
    statement: str
    ksa_tag_id: Optional[int] = None

class COCreate(COBase):
    course_id: int

class COResponse(COBase):
    id: int
    course_id: int
    class Config:
        from_attributes = True

class COPOMappingBase(BaseModel):
    co_id: int
    po_id: int
    weightage: int

class COPOMappingBulkCreate(BaseModel):
    mappings: List[COPOMappingBase]

class COPOMappingResponse(COPOMappingBase):
    id: int
    class Config:
        from_attributes = True

class CloneCORequest(BaseModel):
    source_course_id: int
    target_course_id: int

# KSA Tag Definitions
class KSATagBase(BaseModel):
    domain: KSADomain
    tag_level: str
    description: Optional[str] = None
    knowledge_weight: float
    skill_weight: float
    attitude_weight: float

class KSATagCreate(KSATagBase):
    pass

class KSATagResponse(KSATagBase):
    id: int
    class Config:
        from_attributes = True

# Full Traceability Mappings
class PEOGAMappingBase(BaseModel):
    peo_id: int
    ga_id: int
    weightage: int

class PEOGAMappingBulkCreate(BaseModel):
    mappings: List[PEOGAMappingBase]

class PEOGAMappingResponse(PEOGAMappingBase):
    id: int
    class Config:
        from_attributes = True

class POPEOMappingBase(BaseModel):
    po_id: int
    peo_id: int
    weightage: int

class POPEOMappingBulkCreate(BaseModel):
    mappings: List[POPEOMappingBase]

class POPEOMappingResponse(POPEOMappingBase):
    id: int
    class Config:
        from_attributes = True

class AssessmentCOMappingBase(BaseModel):
    assessment_id: int
    co_id: int
    max_marks: float

class AssessmentCOMappingBulkCreate(BaseModel):
    mappings: List[AssessmentCOMappingBase]

class AssessmentCOMappingResponse(AssessmentCOMappingBase):
    id: int
    class Config:
        from_attributes = True

# User Creation by HOD
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    password: str # returned once on creation
