from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from main.database import get_db
from main import models, schemas, auth

router = APIRouter(prefix="/faculty", tags=["Faculty Domain"])

from main import crud_faculty
from main import schemas_faculty

@router.post("/students/bulk-upload")
def bulk_upload_students(payload: schemas_faculty.BulkStudentUploadRequest, db: Session = Depends(get_db), current_faculty: models.UserInfo = Depends(auth.get_current_faculty)):
    result = crud_faculty.process_bulk_students(db, current_faculty.id, payload)
    
    return {
        "msg": "Student data uploaded and auto-allocated successfully",
        "details": result
    }

@router.post("/subjects/{subject_id}/marks")
def bulk_upload_marks(subject_id: int, payload: schemas_faculty.BulkMarksUploadRequest, db: Session = Depends(get_db), current_faculty: models.UserInfo = Depends(auth.get_current_faculty)):
    faculty, assignment = crud_faculty.verify_faculty_assignment(db, current_faculty.id, subject_id)
    result = crud_faculty.process_bulk_marks(db, subject_id, payload)
    
    return {
        "msg": "IA marks uploaded successfully",
        "details": result
    }
