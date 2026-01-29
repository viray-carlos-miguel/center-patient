from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

app = FastAPI(title="Medical Center API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.20:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class User(BaseModel):
    id: str
    email: str
    role: str
    name: str

class SymptomSubmission(BaseModel):
    symptoms: str
    severity: str
    duration: str
    additional_info: Optional[str] = ""

# Mock data
cases_db = [
    {
        "id": "case_001",
        "patient_id": "1",
        "patient_name": "Demo Patient",
        "symptoms": "Headache, fever, fatigue",
        "severity": "moderate",
        "duration": "2 days",
        "status": "pending",
        "submitted_at": datetime.now().isoformat(),
        "ai_assessment": "Possible viral infection. Monitor temperature."
    }
]

doctor_queue = [
    {
        "id": "case_002",
        "patient_id": "2",
        "patient_name": "John Smith",
        "symptoms": "Fever, body aches",
        "severity": "severe",
        "duration": "1 day",
        "status": "pending",
        "submitted_at": datetime.now().isoformat(),
        "ai_assessment": "Possible influenza."
    }
]

# Routes
@app.get("/")
def root():
    return {"message": "Medical Center API running", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# LOGIN ENDPOINT
@app.post("/api/auth/login")
async def login(data: dict):
    email = data.get("email", "")
    role = data.get("role", "")

    print(f"Login attempt: {email} as {role}")

    if email == "patient@example.com" and role == "patient":
        user = {
            "id": "1",
            "email": email,
            "role": "patient",
            "name": "Demo Patient"
        }
        return {"success": True, "user": user}

    if email == "doctor@example.com" and role == "doctor":
        user = {
            "id": "2",
            "email": email,
            "role": "doctor",
            "name": "Demo Doctor"
        }
        return {"success": True, "user": user}

    return {"success": False, "message": "Use patient@example.com or doctor@example.com"}

# CURRENT USER ENDPOINT
@app.get("/api/auth/current-user")
async def get_current_user():
    return {
        "id": "1",
        "email": "patient@example.com",
        "role": "patient",
        "name": "Demo Patient"
    }

# PATIENT CASES ENDPOINT
@app.get("/api/patient/cases")
async def get_patient_cases():
    return cases_db

# SUBMIT SYMPTOMS ENDPOINT
@app.post("/api/patient/submit-symptoms")
async def submit_symptoms(data: dict):
    new_case = {
        "id": f"case_{uuid.uuid4().hex[:8]}",
        "patient_id": "1",
        "patient_name": "Demo Patient",
        "symptoms": data.get("symptoms", ""),
        "severity": data.get("severity", "moderate"),
        "duration": data.get("duration", "1 day"),
        "status": "pending",
        "submitted_at": datetime.now().isoformat(),
        "ai_assessment": "AI assessment: Educational purposes only."
    }
    cases_db.append(new_case)
    doctor_queue.append(new_case)
    return {"success": True, "case": new_case}

# DOCTOR QUEUE ENDPOINT
@app.get("/api/doctor/case-queue")
async def get_case_queue():
    return doctor_queue

# CASE DETAILS ENDPOINT
@app.get("/api/doctor/case/{case_id}")
async def get_case_details(case_id: str):
    all_cases = cases_db + doctor_queue
    for case in all_cases:
        if case["id"] == case_id:
            return case
    raise HTTPException(status_code=404, detail="Case not found")

# REVIEW CASE ENDPOINT
@app.post("/api/doctor/case/{case_id}/review")
async def review_case(case_id: str, data: dict):
    all_cases = cases_db + doctor_queue
    for case in all_cases:
        if case["id"] == case_id:
            case.update(data)
            case["status"] = "reviewed"
            return {"success": True, "case": case}
    raise HTTPException(status_code=404, detail="Case not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
