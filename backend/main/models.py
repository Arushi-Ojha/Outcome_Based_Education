import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Boolean, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class OTPVerification(Base):
    __tablename__ = "OTP_Verifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(150), nullable=False)
    otp = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)

class Department(Base):
    __tablename__ = "Departments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False) # Maps to "department id" in requirements

class AcademicTerm(Base):
    __tablename__ = "Academic_Terms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    term_name = Column(String(50), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)

class GA(Base):
    __tablename__ = "GAs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    nheqf_level = Column(Float, nullable=False)

class KSADomain(str, enum.Enum):
    Knowledge = "Knowledge"
    Skill = "Skill"
    Attitude = "Attitude"

class KSATag(Base):
    __tablename__ = "KSA_Tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(SQLEnum(KSADomain), nullable=False)
    tag_level = Column(String(10), nullable=False)
    description = Column(String(255))
    knowledge_weight = Column(Float, nullable=False, default=0.0)
    skill_weight = Column(Float, nullable=False, default=0.0)
    attitude_weight = Column(Float, nullable=False, default=0.0)

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    HOD = "HOD"
    PROGRAM_HEAD = "PROGRAM_HEAD"
    FACULTY = "FACULTY"
    COORDINATOR = "COORDINATOR"

class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class UserInfo(Base):
    __tablename__ = "Users_Info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(Role), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    profile_pic = Column(String(255))
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="SET NULL"))

class HOD(Base):
    __tablename__ = "HODs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users_Info.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

class Faculty(Base):
    __tablename__ = "Faculties"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users_Info.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="CASCADE"), nullable=False)
    designation = Column(String(100))
    joining_date = Column(Date)
    subject_undertaking = Column(String(150))
    employee_id = Column(String(50), nullable=True)
    speciality = Column(String(150), nullable=True)

class BatchDuration(str, enum.Enum):
    UG_4YEAR = "UG_4YEAR"
    PG_2YEAR = "PG_2YEAR"
    PGD_MPG_1YEAR = "PGD/MPG_1YEAR"

class Program(Base):
    __tablename__ = "Programs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    batch_year = Column(String(50), nullable=False)
    batch_duration = Column(SQLEnum(BatchDuration), nullable=False)
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="CASCADE"), nullable=False)

class ProgramHead(Base):
    __tablename__ = "Program_Heads"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users_Info.id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("Programs.id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

class CourseCategory(str, enum.Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    AEC = "AEC"
    SEC = "SEC"
    VAC = "VAC"
    GE = "GE"
    INTERNSHIP_PROJECT = "INTERNSHIP PROJECT"

class CourseSubCategory(str, enum.Enum):
    DISCIPLINE_SPECIFIC_CORE = "Discipline specific core"
    DISCIPLINE_SPECIFIC_ELECTIVE = "Discipline specific elective"

class Course(Base):
    __tablename__ = "Courses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    credits = Column(Integer, nullable=False)
    intended_semester = Column(Integer, nullable=False)
    intended_year = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey("Programs.id", ondelete="CASCADE"), nullable=False)
    is_interdepartmental = Column(Boolean, default=False)
    target_department_id = Column(Integer, ForeignKey("Departments.id", ondelete="SET NULL"), nullable=True)
    course_category = Column(SQLEnum(CourseCategory), nullable=False)
    sub_category = Column(SQLEnum(CourseSubCategory), nullable=True)

class ElectiveCombination(Base):
    __tablename__ = "Elective_Combinations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey("Programs.id", ondelete="CASCADE"), nullable=False)
    semester_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    required_selection_count = Column(Integer, nullable=False, default=1)

class CourseCurriculum(Base):
    __tablename__ = "Course_Curriculum"
    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey("Programs.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("Courses.id", ondelete="CASCADE"), nullable=False)
    semester_number = Column(Integer, nullable=False)
    subject_category = Column(SQLEnum(CourseCategory), nullable=False)
    is_mandatory = Column(Boolean, default=True)
    elective_combination_id = Column(Integer, ForeignKey("Elective_Combinations.id", ondelete="SET NULL"), nullable=True)

class CourseCoordinator(Base):
    __tablename__ = "Course_Coordinators"
    id = Column(Integer, primary_key=True, autoincrement=True)
    faculty_id = Column(Integer, ForeignKey("Faculties.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("Courses.id", ondelete="CASCADE"), nullable=False)
    academic_year = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)

class PEO(Base):
    __tablename__ = "PEOs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    statement = Column(Text, nullable=False)
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="CASCADE"), nullable=False)

class POType(str, enum.Enum):
    PO = "PO"
    PSO = "PSO"

class PO(Base):
    __tablename__ = "POs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(SQLEnum(POType), nullable=False)
    statement = Column(Text, nullable=False)
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="CASCADE"), nullable=False)
    ksa_domain = Column(SQLEnum(KSADomain), nullable=True)

class CO(Base):
    __tablename__ = "COs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    statement = Column(Text, nullable=False)
    course_id = Column(Integer, ForeignKey("Courses.id", ondelete="CASCADE"), nullable=False)
    ksa_tag_id = Column(Integer, ForeignKey("KSA_Tags.id", ondelete="SET NULL"))

class COPOMapping(Base):
    __tablename__ = "CO_PO_Mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    co_id = Column(Integer, ForeignKey("COs.id", ondelete="CASCADE"), nullable=False)
    po_id = Column(Integer, ForeignKey("POs.id", ondelete="CASCADE"), nullable=False)
    weightage = Column(Integer, nullable=False)

class PEOGAMapping(Base):
    __tablename__ = "PEO_GA_Mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    peo_id = Column(Integer, ForeignKey("PEOs.id", ondelete="CASCADE"), nullable=False)
    ga_id = Column(Integer, ForeignKey("GAs.id", ondelete="CASCADE"), nullable=False)
    weightage = Column(Integer, nullable=False)

class POPEOMapping(Base):
    __tablename__ = "PO_PEO_Mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    po_id = Column(Integer, ForeignKey("POs.id", ondelete="CASCADE"), nullable=False)
    peo_id = Column(Integer, ForeignKey("PEOs.id", ondelete="CASCADE"), nullable=False)
    weightage = Column(Integer, nullable=False)

class Assessment(Base):
    __tablename__ = "Assessments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    max_marks = Column(Float, nullable=False)
    threshold_percentage = Column(Float, nullable=False, default=65.0)
    course_id = Column(Integer, ForeignKey("Courses.id", ondelete="CASCADE"), nullable=False)

class AssessmentCOMapping(Base):
    __tablename__ = "Assessment_CO_Mappings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("Assessments.id", ondelete="CASCADE"), nullable=False)
    co_id = Column(Integer, ForeignKey("COs.id", ondelete="CASCADE"), nullable=False)
    max_marks = Column(Float, nullable=False)

class IAMark(Base):
    __tablename__ = "IA_Marks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    score = Column(Float, nullable=False)
    evaluation_date = Column(Date, nullable=False)
    usn = Column(String(30), ForeignKey("Student_Details.usn", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("Assessments.id", ondelete="CASCADE"), nullable=False)
    co_id = Column(Integer, ForeignKey("COs.id", ondelete="CASCADE"), nullable=False)

class StudentDetail(Base):
    __tablename__ = "Student_Details"
    usn = Column(String(30), primary_key=True)
    name = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False, default=1)
    department_id = Column(Integer, ForeignKey("Departments.id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("Programs.id", ondelete="SET NULL"))

class StudentEnrollment(Base):
    __tablename__ = "Student_Enrollments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usn = Column(String(30), ForeignKey("Student_Details.usn", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("Courses.id", ondelete="CASCADE"), nullable=False)
    academic_term_id = Column(Integer, ForeignKey("Academic_Terms.id", ondelete="RESTRICT"), nullable=False)
    semester_number = Column(Integer, nullable=False)
