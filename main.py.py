from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

doctors = []
patients = []


class Doctor(BaseModel):
    name: str
    specialization: str
    email: EmailStr
    is_active: bool = True


class Patient(BaseModel):
    name: str
    age: int = Field(gt=0)
    phone: str


@app.post("/doctors")
def add_doctor(doctor: Doctor):
    new_doctor = doctor.model_dump()
    new_doctor["id"] = len(doctors) + 1
    doctors.append(new_doctor)
    return new_doctor


@app.get("/doctors")
def get_doctors():
    return doctors


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    raise HTTPException(status_code=404, detail="Doctor not found")


@app.post("/patients")
def add_patient(patient: Patient):
    new_patient = patient.model_dump()
    new_patient["id"] = len(patients) + 1
    patients.append(new_patient)
    return new_patient


@app.get("/patients")
def get_patients():
    return patients