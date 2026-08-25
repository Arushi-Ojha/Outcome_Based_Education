from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from main import models, schemas_faculty

def verify_faculty_assignment(db: Session, user_id: int, subject_id: int):
    # Get faculty record
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == user_id).first()
    if not faculty:
        raise HTTPException(status_code=403, detail="You are not registered as a Faculty member.")
        
    # Check assignment
    assignment = db.query(models.SubjectCoordinator).filter(
        models.SubjectCoordinator.faculty_id == faculty.id,
        models.SubjectCoordinator.subject_id == subject_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=403, detail="You are not assigned to teach this subject.")
    return faculty, assignment

def process_bulk_students(db: Session, faculty_user_id: int, payload: schemas_faculty.BulkStudentUploadRequest):
    # Fetch faculty profile
    faculty = db.query(models.Faculty).filter(models.Faculty.user_id == faculty_user_id).first()
    if not faculty:
        raise HTTPException(status_code=403, detail="You are not registered as a Faculty member.")

    # Get all subject_ids this faculty is assigned to
    assignments = db.query(models.SubjectCoordinator).filter(models.SubjectCoordinator.faculty_id == faculty.id).all()
    assigned_subject_ids = [a.subject_id for a in assignments]
    if not assigned_subject_ids:
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
                academic_course_id=student_data.academic_course_id,
                semester=student_data.semester,
                department_id=student_data.department_id
            )
            new_students.append(new_student)
            existing_usn_set.add(student_data.usn)
            
    if new_students:
        db.add_all(new_students)
        db.commit()
        
    # Auto-enrollment logic
    subjects = db.query(models.Subject).filter(models.Subject.id.in_(assigned_subject_ids)).all()
    subject_map = {s.id: s.semester for s in subjects} # Maps subject_id -> semester
    
    # Group students by semester
    semester_students = {}
    for s in payload.students:
        semester_students.setdefault(s.semester, []).append(s.usn)
        
    new_enrollments = []
    for subject_id, subject_semester in subject_map.items():
        usns_for_this_sem = semester_students.get(subject_semester, [])
        if not usns_for_this_sem:
            continue
            
        existing_enrollments = db.query(models.StudentEnrollment).filter(
            models.StudentEnrollment.subject_id == subject_id,
            models.StudentEnrollment.usn.in_(usns_for_this_sem),
            models.StudentEnrollment.academic_term_id == payload.academic_term_id
        ).all()
        enrolled_usns = {e.usn for e in existing_enrollments}
        
        for usn in usns_for_this_sem:
            if usn not in enrolled_usns:
                new_enrollments.append(models.StudentEnrollment(
                    usn=usn,
                    subject_id=subject_id,
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

def process_bulk_marks(db: Session, subject_id: int, payload: schemas_faculty.BulkMarksUploadRequest):
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
