from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db

from app.database import SessionLocal
from app.models.patient import Patient
from app.schemas.patient_schema import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# ==========================
# Database Dependency
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# CREATE PATIENT
# ==========================
@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = Patient(**patient.model_dump())

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient


# ==========================
# GET ALL PATIENTS
# ==========================
@router.get("/", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).order_by(Patient.id.desc()).all()


# ==========================================
# SEARCH PATIENTS
# ==========================================

@router.get("/search")
def search_patients(query: str, db: Session = Depends(get_db)):
    patients = db.query(Patient).filter(
        or_(
            Patient.full_name.ilike(f"%{query}%"),
            Patient.phone.ilike(f"%{query}%")
        )
    ).all()

    return patients


# ==========================
# GET SINGLE PATIENT
# ==========================
@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


# ==========================
# UPDATE PATIENT
# ==========================
@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    updates = patient_data.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)

    return patient


# ==========================================
# DELETE PATIENT
# ==========================================

@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    db.delete(patient)
    db.commit()

    return {
        "message": "Patient deleted successfully"
    }