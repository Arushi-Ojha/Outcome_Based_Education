from pydantic import BaseModel
from typing import List, Optional
from main.models import DegreeType, SubjectCategory, KSADomain, POType

# Academic Courses (formerly Programs)
class AcademicCourseBase(BaseModel):
    name: str
    degree_type: DegreeType
    
class AcademicCourseCreate(AcademicCourseBase):
    pass

class AcademicCourseUpdate(BaseModel):
    name: Optional[str] = None
    degree_type: Optional[DegreeType] = None

class AcademicCourseResponse(AcademicCourseBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

# Subjects (formerly Courses)
class SubjectBase(BaseModel):
    code: str
    name: str
    credits: int
    semester: int

class SubjectCreate(SubjectBase):
    pass

class SubjectResponse(SubjectBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

# Elective Baskets
class ElectiveBasketBase(BaseModel):
    name: str
    required_selection_count: int

class ElectiveBasketCreate(ElectiveBasketBase):
    pass

class ElectiveBasketResponse(ElectiveBasketBase):
    id: int
    academic_course_id: int
    semester_number: int
    class Config:
        from_attributes = True

# Curriculum
class CurriculumMappingCreate(BaseModel):
    academic_course_id: int
    subject_id: int
    semester_number: int
    subject_category: SubjectCategory
    is_mandatory: bool = True
    elective_basket_id: Optional[int] = None

class CurriculumMappingBulkCreate(BaseModel):
    mappings: List[CurriculumMappingCreate]

class BasketCourseAdd(BaseModel):
    subject_ids: List[int]

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
    subject_id: int

class COResponse(COBase):
    id: int
    subject_id: int
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
    source_subject_id: int
    target_subject_id: int

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
