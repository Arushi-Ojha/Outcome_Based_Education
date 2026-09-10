from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from main import models, schemas_faculty
import secrets
from main.auth import get_password_hash
from main.email_utils import send_credentials_email
from sqlalchemy import func

def verify_faculty_assignment(db: Session, user_id: int, course_id: int):
    # Get faculty record
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user_id).first()
    if not faculty:
        raise HTTPException(status_code=403, detail="You are not registered as a Faculty member.")
        
    # Check assignment
    assignment = db.query(models.CourseCoordinator).filter(
        models.CourseCoordinator.faculty_id == faculty.id,
        models.CourseCoordinator.course_id == course_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=403, detail="You are not assigned to teach this subject.")
    return faculty, assignment

def process_bulk_students(db: Session, faculty_user_id: int, payload: schemas_faculty.BulkStudentUploadRequest):
    # Fetch faculty profile
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == faculty_user_id).first()
    if not faculty:
        raise HTTPException(status_code=403, detail="You are not registered as a Faculty member.")

    # Get all course_ids this faculty is assigned to
    assignments = db.query(models.CourseCoordinator).filter(models.CourseCoordinator.faculty_id == faculty.id).all()
    assigned_course_ids = [a.course_id for a in assignments]
    if not assigned_course_ids:
        raise HTTPException(status_code=403, detail="You are not assigned to teach any subjects.")

    usns = [student.usn for student in payload.students]
    
    # Fetch existing students to avoid duplicates
    existing_students = db.query(models.StudentDetail).filter(models.StudentDetail.usn.in_(usns)).all()
    existing_usn_set = {s.usn for s in existing_students}
    
    # Create missing students
    new_students = []
    for student_data in payload.students:
        if student_data.usn not in existing_usn_set:
            new_student = models.StudentDetail(
                usn=student_data.usn,
                name=student_data.name,
                program_id=student_data.program_id,
                semester=student_data.semester,
                department_id=student_data.department_id
            )
            new_students.append(new_student)
            existing_usn_set.add(student_data.usn)
            
    if new_students:
        db.add_all(new_students)
        db.commit()
        
    # Auto-enrollment logic
    subjects = db.query(models.Course).filter(models.Course.id.in_(assigned_course_ids)).all()
    subject_map = {s.id: s.intended_semester for s in subjects} # Maps course_id -> semester
    
    # Group students by semester
    semester_students = {}
    for s in payload.students:
        semester_students.setdefault(s.semester, []).append(s.usn)
        
    new_enrollments = []
    for course_id, subject_semester in subject_map.items():
        usns_for_this_sem = semester_students.get(subject_semester, [])
        if not usns_for_this_sem:
            continue
            
        existing_enrollments = db.query(models.StudentEnrollment).filter(
            models.StudentEnrollment.course_id == course_id,
            models.StudentEnrollment.usn.in_(usns_for_this_sem),
            models.StudentEnrollment.academic_term_id == payload.academic_term_id
        ).all()
        enrolled_usns = {e.usn for e in existing_enrollments}
        
        for usn in usns_for_this_sem:
            if usn not in enrolled_usns:
                new_enrollments.append(models.StudentEnrollment(
                    usn=usn,
                    course_id=course_id,
                    academic_term_id=payload.academic_term_id,
                    semester_number=subject_semester
                ))
                
    if new_enrollments:
        db.add_all(new_enrollments)
        db.commit()
        
    return {
        "students_created": len(new_students),
        "students_enrolled": len(new_enrollments)
    }

def process_bulk_marks(db: Session, course_id: int, payload: schemas_faculty.BulkMarksUploadRequest):
    new_marks = []
    for student_data in payload.student_marks:
        for mark_data in student_data.marks:
            new_marks.append(models.IAMark(
                score=mark_data.score,
                evaluation_date=mark_data.evaluation_date,
                usn=student_data.usn,
                assessment_id=mark_data.assessment_id,
                co_id=mark_data.co_id
            ))
            
    if new_marks:
        db.bulk_save_objects(new_marks)
        db.commit()
        
    return {
        "marks_uploaded": len(new_marks)
    }

# ==========================================
# FACULTY ASSIGNMENT & UPLOAD
# ==========================================
def upload_and_assign_faculty(db: Session, course_id: int, payload: schemas_faculty.FacultyUploadRequest, department_id: int):
    new_users_created = 0
    updated_users = 0
    assignments_created = 0

    for item in payload.faculty_list:
        # Check if email exists
        user = db.query(models.UserInfo).filter(models.UserInfo.email == item.email).first()
        
        if not user:
            # Create new UserInfo
            raw_password = secrets.token_urlsafe(8)
            user = models.UserInfo(
                name=item.name,
                email=item.email,
                password_hash=get_password_hash(raw_password),
                role=models.Role.FACULTY,
                status=models.UserStatus.APPROVED,
                department_id=department_id
            )
            db.add(user)
            db.flush() # To get user.id
            
            # Email them
            send_credentials_email(user.email, user.role.value, raw_password)
            new_users_created += 1
        else:
            # Update existing user's name if it changed (optional, but requested by some flows)
            user.name = item.name
            updated_users += 1
            
        # Get or Create Faculty profile
        faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user.id).first()
        if not faculty:
            faculty = models.Faculty(
                user_id=user.id,
                department_id=department_id
            )
            db.add(faculty)
            db.flush()
            
        # Update Faculty profile details
        faculty.employee_id = item.employee_id
        faculty.speciality = item.speciality
        
        # Check if already assigned to this course
        existing_assignment = db.query(models.CourseCoordinator).filter(
            models.CourseCoordinator.faculty_id == faculty.id,
            models.CourseCoordinator.course_id == course_id,
            models.CourseCoordinator.academic_year == payload.academic_year,
            models.CourseCoordinator.semester == payload.semester
        ).first()
        
        if not existing_assignment:
            assignment = models.CourseCoordinator(
                faculty_id=faculty.id,
                course_id=course_id,
                academic_year=payload.academic_year,
                semester=payload.semester
            )
            db.add(assignment)
            assignments_created += 1
            
    db.commit()
    return {
        "new_users_created": new_users_created,
        "existing_users_updated": updated_users,
        "new_assignments": assignments_created
    }

def get_assigned_faculty(db: Session, course_id: int):
    # Fetch all assignments for the course
    assignments = db.query(models.CourseCoordinator).filter(models.CourseCoordinator.course_id == course_id).all()
    faculty_ids = {a.faculty_id for a in assignments}
    
    result = []
    for f_id in faculty_ids:
        faculty = db.query(models.Faculty).filter(models.Faculty.id == f_id).first()
        if not faculty:
            continue
            
        user = db.query(models.UserInfo).filter(models.UserInfo.id == faculty.user_id).first()
        if not user:
            continue
            
        # Count total courses assigned to this faculty
        total_assigned = db.query(models.CourseCoordinator).filter(models.CourseCoordinator.faculty_id == f_id).count()
        
        result.append(schemas_faculty.FacultyCourseResponse(
            employee_id=faculty.employee_id,
            name=user.name,
            speciality=faculty.speciality,
            email=user.email,
            total_courses_assigned=total_assigned
        ))
        
    return result

def get_faculty_dropdown(db: Session, department_id: int):
    faculties = db.query(models.Faculty).filter(models.Faculty.department_id == department_id).all()
    result = []
    for f in faculties:
        user = db.query(models.UserInfo).filter(models.UserInfo.id == f.user_id).first()
        if user:
            result.append(schemas_faculty.FacultyDropdownResponse(
                id=f.id,
                user_id=user.id,
                employee_id=f.employee_id,
                name=user.name,
                email=user.email,
                speciality=f.speciality
            ))
    return result

