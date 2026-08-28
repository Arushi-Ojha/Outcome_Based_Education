import secrets
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from main.models import Department, UserInfo, HOD, Role, UserStatus, Program, ProgramHead
from main.schemas_admin import DepartmentCreate, DepartmentResponse, ProgramCreate, ProgramResponse
from main.auth import get_password_hash
from main.email_utils import send_credentials_email

def create_department(db: Session, dept_data: DepartmentCreate):
    # Check if department code exists
    if db.query(Department).filter(Department.code == dept_data.department_id).first():
        raise HTTPException(status_code=400, detail="Department with this ID already exists")
    
    # Check if HOD email exists
    if db.query(UserInfo).filter(UserInfo.email == dept_data.hod_email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create Department
    new_dept = Department(name=dept_data.department_name, code=dept_data.department_id)
    db.add(new_dept)
    db.flush() # get new_dept.id

    # Create HOD UserInfo
    raw_password = secrets.token_urlsafe(8)
    new_user = UserInfo(
        name=dept_data.hod_name,
        email=dept_data.hod_email,
        password_hash=get_password_hash(raw_password),
        role=Role.HOD,
        status=UserStatus.APPROVED,
        department_id=new_dept.id
    )
    db.add(new_user)
    db.flush()

    # Create HOD entry
    new_hod = HOD(
        user_id=new_user.id,
        department_id=new_dept.id,
        start_date=date.today()
    )
    db.add(new_hod)
    db.commit()
    db.refresh(new_dept)

    # Email HOD credentials
    send_credentials_email(dept_data.hod_email, "HOD", raw_password)

    return DepartmentResponse(
        id=new_dept.id,
        name=new_dept.name,
        code=new_dept.code,
        hod_email=dept_data.hod_email,
        hod_password=raw_password
    )

def create_program(db: Session, prog_data: ProgramCreate):
    # Check if program id exists
    if db.query(Program).filter(Program.program_id == prog_data.program_id).first():
        raise HTTPException(status_code=400, detail="Program with this ID already exists")

    # Check if dept exists
    if not db.query(Department).filter(Department.id == prog_data.department_id).first():
        raise HTTPException(status_code=404, detail="Department not found")

    # Check if Program Head email exists
    if db.query(UserInfo).filter(UserInfo.email == prog_data.program_head_email).first():
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create Program
    new_prog = Program(
        program_id=prog_data.program_id,
        name=prog_data.program_name,
        batch_year=prog_data.batch_year,
        batch_duration=prog_data.batch_duration,
        department_id=prog_data.department_id
    )
    db.add(new_prog)
    db.flush()

    # Create Program Head UserInfo
    raw_password = secrets.token_urlsafe(8)
    new_user = UserInfo(
        name=prog_data.program_head_name,
        email=prog_data.program_head_email,
        password_hash=get_password_hash(raw_password),
        role=Role.PROGRAM_HEAD,
        status=UserStatus.APPROVED,
        department_id=prog_data.department_id
    )
    db.add(new_user)
    db.flush()

    # Create Program Head entry
    new_ph = ProgramHead(
        user_id=new_user.id,
        program_id=new_prog.id,
        start_date=date.today()
    )
    db.add(new_ph)
    db.commit()
    db.refresh(new_prog)

    # Email Program Head credentials
    send_credentials_email(prog_data.program_head_email, "Program Head", raw_password)

    return ProgramResponse(
        id=new_prog.id,
        program_id=new_prog.program_id,
        name=new_prog.name,
        batch_year=new_prog.batch_year,
        batch_duration=new_prog.batch_duration,
        program_head_email=prog_data.program_head_email,
        program_head_password=raw_password
    )

def reset_user_password(db: Session, email: str):
    user = db.query(UserInfo).filter(UserInfo.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    raw_password = secrets.token_urlsafe(8)
    user.password_hash = get_password_hash(raw_password)
    db.commit()
    
    send_credentials_email(user.email, user.role.value, raw_password)
    return {"msg": f"Password reset successfully. New credentials sent to {email}"}
