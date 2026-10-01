from fastapi import FastAPI

from database import Base, engine
from routers.auth_router import router as auth_router
from routers.doctor_router import router as doctor_router
from routers.patient_router import router as patient_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Doctor Patient Management API",
    version="1.0.0"
)


# Authentication routes
app.include_router(auth_router)

# Doctor routes
app.include_router(doctor_router)

# Patient routes
app.include_router(patient_router)


@app.get("/")
def root():
    return {
        "message": "Doctor Patient Management API is running"
    }