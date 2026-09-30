# FastAPI Doctor and Patient API

## Overview
A simple REST API built using FastAPI to manage Doctors and Patients.

## Technologies Used
- Python 3.9+
- FastAPI
- Pydantic
- Uvicorn
- In-memory storage

## APIs

### Doctor APIs
- POST /doctors - Create a doctor
- GET /doctors - List all doctors
- GET /doctors/{doctor_id} - Get doctor by ID

### Patient APIs
- POST /patients - Create a patient
- GET /patients - List all patients

## Validation
- Doctor email must be valid.
- Patient age must be greater than 0.
- Pydantic models are used for validation.
- HTTPException is used for error handling.

## How to Run

Install dependencies:

```bash
pip install fastapi uvicorn pydantic[email]