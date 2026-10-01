from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.models import Doctor, Patient, User
from schemas.schemas import DoctorCreate, DoctorUpdate, DoctorResponse
from routers.auth_router import get_current_user, require_admin


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post(
    "",
    response_model=DoctorResponse,
    dependencies=[Depends(require_admin)]
)
def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db)
):
    existing_doctor = db.query(Doctor).filter(
        Doctor.email == doctor_data.email
    ).first()

    if existing_doctor:
        raise HTTPException(
            status_code=400,
            detail="Doctor email already exists"
        )

    doctor = Doctor(
        name=doctor_data.name,
        specialization=doctor_data.specialization,
        email=doctor_data.email,
        is_active=doctor_data.is_active
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


@router.get(
    "",
    response_model=list[DoctorResponse],
    dependencies=[Depends(get_current_user)]
)
def get_doctors(
    db: Session = Depends(get_db)
):
    return db.query(Doctor).all()


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    dependencies=[Depends(get_current_user)]
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
    dependencies=[Depends(require_admin)]
)
def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if doctor_data.email:
        existing_doctor = db.query(Doctor).filter(
            Doctor.email == doctor_data.email,
            Doctor.id != doctor_id
        ).first()

        if existing_doctor:
            raise HTTPException(
                status_code=400,
                detail="Doctor email already exists"
            )

    update_data = doctor_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)

    return doctor


@router.delete(
    "/{doctor_id}",
    dependencies=[Depends(require_admin)]
)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Soft delete
    doctor.is_active = False

    db.commit()

    return {
        "message": "Doctor deactivated successfully"
    }


@router.post(
    "/{doctor_id}/patients/{patient_id}",
    dependencies=[Depends(require_admin)]
)
def assign_patient(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    patient.doctor_id = doctor_id

    db.commit()

    return {
        "message": "Patient assigned successfully",
        "doctor_id": doctor_id,
        "patient_id": patient_id
    }


@router.get(
    "/{doctor_id}/patients"
)
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # Admin can view any doctor's patients.
    # Doctor can view only their own patients.
    if current_user.role == "doctor":
        current_doctor = db.query(Doctor).filter(
            Doctor.email == current_user.email
        ).first()

        if not current_doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor profile not found"
            )

        if current_doctor.id != doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own patients"
            )

    patients = db.query(Patient).filter(
        Patient.doctor_id == doctor_id
    ).all()

    return patients