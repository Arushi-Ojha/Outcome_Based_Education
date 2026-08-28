import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from main.database import get_db
from main.models import UserInfo, Role, UserStatus

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserInfo).filter(UserInfo.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: UserInfo = Depends(get_current_user)):
    if current_user.status != UserStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Inactive or pending user account")
    return current_user

# --- Role Based Dependency Injectors ---

def get_current_admin(current_user: UserInfo = Depends(get_current_active_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough privileges, requires ADMIN")
    return current_user

def get_current_hod(current_user: UserInfo = Depends(get_current_active_user)):
    if current_user.role != Role.HOD:
        raise HTTPException(status_code=403, detail="Not enough privileges, requires HOD")
    return current_user

def get_current_coordinator(current_user: UserInfo = Depends(get_current_active_user)):
    if current_user.role != Role.COORDINATOR:
        raise HTTPException(status_code=403, detail="Not enough privileges, requires COORDINATOR")
    return current_user

def get_current_faculty(current_user: UserInfo = Depends(get_current_active_user)):
    if current_user.role != Role.FACULTY:
        raise HTTPException(status_code=403, detail="Not enough privileges, requires FACULTY")
    return current_user

def get_current_program_head(current_user: UserInfo = Depends(get_current_active_user)):
    if current_user.role != Role.PROGRAM_HEAD:
        raise HTTPException(status_code=403, detail="Not enough privileges, requires PROGRAM_HEAD")
    return current_user
