from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from main.database import get_db
from main import models, schemas, auth
from main.email_utils import send_otp_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request-otp")
def request_otp(req: schemas.EmailRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.UserInfo).filter(models.UserInfo.email == req.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Generate 6 digit OTP
    otp_code = str(random.randint(100000, 999999))
    expiration = datetime.utcnow() + timedelta(minutes=10)
    
    # Store or update OTP
    db_otp = db.query(models.OTPVerification).filter(models.OTPVerification.email == req.email).first()
    if db_otp:
        db_otp.otp = otp_code
        db_otp.expires_at = expiration
    else:
        new_otp = models.OTPVerification(email=req.email, otp=otp_code, expires_at=expiration)
        db.add(new_otp)
    db.commit()
    
    # Send email
    send_otp_email(req.email, otp_code)
    
    return {"msg": "OTP sent successfully to your email"}

@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserInfo).filter(models.UserInfo.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Verify OTP
    db_otp = db.query(models.OTPVerification).filter(
        models.OTPVerification.email == user.email,
        models.OTPVerification.otp == user.otp
    ).first()
    
    if not db_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if db_otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    # Delete OTP after successful verification
    db.delete(db_otp)
    
    # Auto-approve ADMIN and HOD for initial setup, otherwise PENDING
    status_val = models.UserStatus.PENDING
    if user.role in [models.Role.ADMIN, models.Role.HOD]:
        status_val = models.UserStatus.APPROVED
        
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.UserInfo(
        name=user.name,
        email=user.email,
        password_hash=hashed_pwd,
        role=user.role,
        status=status_val
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 spec requires the field to be named 'username', but we allow email or name here
    user = db.query(models.UserInfo).filter(
        (models.UserInfo.email == form_data.username) | 
        (models.UserInfo.name == form_data.username)
    ).first()
    
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status == models.UserStatus.REJECTED:
        raise HTTPException(status_code=403, detail="Account is rejected")
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/complete-profile")
def complete_profile(profile: schemas.ProfileComplete, db: Session = Depends(get_db), current_user: models.UserInfo = Depends(auth.get_current_user)):
    """Allows a PENDING user to select their department. Still requires HOD approval afterwards."""
    if current_user.status != models.UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="Profile is already complete or approved")
        
    current_user.department_id = profile.department_id
    db.commit()
    return {"msg": "Profile completed. Awaiting HOD approval."}
