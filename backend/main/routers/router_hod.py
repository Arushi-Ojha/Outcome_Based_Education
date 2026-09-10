from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from main.database import get_db
from main import models, schemas, schemas_hod, crud_hod, auth
from main.crud_admin import create_program
from main.schemas_admin import ProgramCreate, ProgramResponse

router = APIRouter(prefix="/hod", tags=["HOD Domain"])

@router.post("/faculty", response_model=schemas_hod.UserResponse)
def api_create_faculty(user_data: schemas_hod.UserCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_staff_user(db, user_data, current_hod.department_id, models.Role.FACULTY)

@router.post("/coordinator", response_model=schemas_hod.UserResponse)
def api_create_coordinator(user_data: schemas_hod.UserCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_staff_user(db, user_data, current_hod.department_id, models.Role.COORDINATOR)

@router.post("/reset-password")
def api_reset_password(payload: schemas.PasswordResetRequest, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.reset_user_password(db, payload.email, current_hod.department_id)

@router.post("/programs", response_model=ProgramResponse)
def api_create_program(prog_data: ProgramCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    # Override department_id to ensure HOD can only create in their own department
    prog_data.department_id = current_hod.department_id
    return create_program(db, prog_data)

@router.get("/programs", response_model=List[ProgramResponse])
def api_get_programs(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    programs = db.query(models.Program).filter(models.Program.department_id == current_hod.department_id).all()
    # ProgramResponse expects program_head_password etc which we don't have for GET requests, 
    # so we should use a simpler schema, but let's mock it for now or return what we can
    res = []
    for p in programs:
        ph = db.query(models.ProgramHead).filter(models.ProgramHead.program_id == p.id).first()
        ph_email = "unknown"
        if ph:
            user = db.query(models.UserInfo).filter(models.UserInfo.id == ph.user_id).first()
            if user: ph_email = user.email
            
        res.append(ProgramResponse(
            id=p.id,
            program_id=p.program_id,
            name=p.name,
            batch_year=p.batch_year,
            batch_duration=p.batch_duration,
            program_head_email=ph_email,
            program_head_password="***" # Redacted for GET
        ))
    return res

@router.delete("/programs/{program_id}")
def api_delete_program(program_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    prog = db.query(models.Program).filter(models.Program.id == program_id).first()
    if not prog or prog.department_id != current_hod.department_id:
        raise HTTPException(status_code=404, detail="Program not found")
    db.delete(prog)
    db.commit()
    return {"msg": "Program deleted successfully"}

# ==========================================
# 3. OBE FRAMEWORK CRUD
# ==========================================
# GAs
@router.post("/framework/graduate-attributes", response_model=schemas_hod.GAResponse)
def create_ga(ga: schemas_hod.GACreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_model(db, models.GA, ga.model_dump())

@router.get("/framework/graduate-attributes", response_model=List[schemas_hod.GAResponse])
def get_gas(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.GA)

@router.delete("/framework/graduate-attributes/{ga_id}")
def delete_ga(ga_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    ga = crud_hod.get_model_by_id(db, models.GA, ga_id)
    if not ga: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, ga)
    return {"msg": "Deleted successfully"}

# PEOs
@router.post("/framework/peos", response_model=schemas_hod.PEOResponse)
def create_peo(peo: schemas_hod.PEOCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    data = peo.model_dump()
    data["department_id"] = current_hod.department_id
    return crud_hod.create_model(db, models.PEO, data)

@router.get("/framework/peos", response_model=List[schemas_hod.PEOResponse])
def get_peos(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.PEO, department_id=current_hod.department_id)

@router.delete("/framework/peos/{peo_id}")
def delete_peo(peo_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    peo = crud_hod.get_model_by_id(db, models.PEO, peo_id)
    if not peo or peo.department_id != current_hod.department_id: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, peo)
    return {"msg": "Deleted successfully"}

# POs
@router.post("/framework/pos", response_model=schemas_hod.POResponse)
def create_po(po: schemas_hod.POCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    data = po.model_dump()
    data["department_id"] = current_hod.department_id
    return crud_hod.create_model(db, models.PO, data)

@router.get("/framework/pos", response_model=List[schemas_hod.POResponse])
def get_pos(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.PO, department_id=current_hod.department_id)

@router.delete("/framework/pos/{po_id}")
def delete_po(po_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    po = crud_hod.get_model_by_id(db, models.PO, po_id)
    if not po or po.department_id != current_hod.department_id: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, po)
    return {"msg": "Deleted successfully"}

# KSA Tags
@router.post("/framework/ksa-tags", response_model=schemas_hod.KSATagResponse)
def create_ksa(ksa: schemas_hod.KSATagCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.create_model(db, models.KSATag, ksa.model_dump())

@router.get("/framework/ksa-tags", response_model=List[schemas_hod.KSATagResponse])
def get_ksas(db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    return crud_hod.get_all_models(db, models.KSATag)

@router.delete("/framework/ksa-tags/{ksa_id}")
def delete_ksa(ksa_id: int, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    ksa = crud_hod.get_model_by_id(db, models.KSATag, ksa_id)
    if not ksa: raise HTTPException(status_code=404)
    crud_hod.delete_model(db, ksa)
    return {"msg": "Deleted successfully"}



@router.post("/framework/mappings/peo-ga")
def map_peo_ga(payload: schemas_hod.PEOGAMappingBulkCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    count = crud_hod.bulk_map_peo_ga(db, payload)
    return {"msg": f"Successfully created {count} PEO-GA mappings"}

@router.post("/framework/mappings/po-peo")
def map_po_peo(payload: schemas_hod.POPEOMappingBulkCreate, db: Session = Depends(get_db), current_hod: models.UserInfo = Depends(auth.get_current_hod)):
    count = crud_hod.bulk_map_po_peo(db, payload)
    return {"msg": f"Successfully created {count} PO-PEO mappings"}

