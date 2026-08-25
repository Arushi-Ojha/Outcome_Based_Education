from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from main.database import get_db, engine
from main import models, auth

router = APIRouter(prefix="/analytics", tags=["Analytics Domain"])

@router.get("/co-attainment/{subject_id}")
def get_co_attainment(subject_id: int, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(auth.get_current_active_user)):
    """Calculate CO attainment per course (percentage of students crossing the threshold)"""
    
    query = f"""
    SELECT iam.score, a.max_marks, a.threshold_percentage, iam.co_id
    FROM IA_Marks iam
    JOIN Assessments a ON iam.assessment_id = a.id
    WHERE a.subject_id = {subject_id}
    """
    
    # Load into Pandas dataframe for vectorized calculation
    df = pd.read_sql(query, engine)
    
    if df.empty:
        return {"msg": "No marks data found for this course", "data": {}}
        
    df['percentage'] = (df['score'] / df['max_marks']) * 100
    df['crossed_threshold'] = df['percentage'] >= df['threshold_percentage']
    
    # Calculate % of students crossing threshold per CO
    attainment = (df.groupby('co_id')['crossed_threshold'].mean() * 100).round(2)
    
    return {"subject_id": subject_id, "co_attainment": attainment.to_dict()}

@router.get("/po-attainment/{academic_course_id}")
def get_po_attainment(academic_course_id: int, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(auth.get_current_active_user)):
    """Calculate PO attainment per program using Pandas matrix multiplication"""
    # This requires fetching CO attainments for all courses in the program
    # and multiplying them by the CO-PO weightages.
    # Stub logic showcasing pandas structure
    return {"academic_course_id": academic_course_id, "msg": "PO attainment matrix placeholder"}

@router.get("/ksa-dashboard/{usn}")
def get_student_ksa(usn: str, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(auth.get_current_active_user)):
    """Generate a student's personalized KSA tags dashboard across all subjects"""
    # Stub logic showcasing pandas structure
    return {"msg": f"Personalized KSA aggregation for USN {usn} will go here"}
