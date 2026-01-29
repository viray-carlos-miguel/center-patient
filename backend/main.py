from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import json

from database.database import get_db, init_db
from models import User, Doctor, Patient, MedicalCase, CaseAssessment, Appointment
from pydantic import BaseModel, EmailStr, validator
from passlib.context import CryptContext
from jose import JWTError, jwt

# Initialize FastAPI
app = FastAPI(
    title="Medical Center API",
    description="Complete healthcare management system with PostgreSQL",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.20:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"  # Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['patient', 'doctor', 'admin']:
            raise ValueError('Role must be patient, doctor, or admin')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    first_name: str
    last_name: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class DoctorCreate(BaseModel):
    medical_license: str
    specialization: str
    qualifications: Optional[str] = None
    years_of_experience: Optional[int] = None
    consultation_fee: Optional[float] = None

class PatientCreate(BaseModel):
    blood_type: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

class MedicalCaseCreate(BaseModel):
    title: str
    symptoms: str
    severity: str = "medium"
    description: Optional[str] = None

# Auth functions
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

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).filter(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

# Startup event
@app.on_event("startup")
async def startup_event():
    await init_db()

# Routes
@app.get("/")
async def root():
    return {"message": "Medical Center API with PostgreSQL", "status": "running"}

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create role-specific record
    if user_data.role == "doctor":
        doctor_data = DoctorCreate(
            medical_license=f"MD-{uuid.uuid4().hex[:6].upper()}",
            specialization="General Medicine"
        )
        doctor = Doctor(
            user_id=user.id,
            medical_license=doctor_data.medical_license,
            specialization=doctor_data.specialization
        )
        db.add(doctor)
    
    elif user_data.role == "patient":
        patient = Patient(user_id=user.id)
        db.add(patient)
    
    await db.commit()
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@app.post("/api/auth/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)

# Patient endpoints
@app.post("/api/patient/cases")
async def create_medical_case(
    case_data: MedicalCaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can create cases")
    
    case = MedicalCase(
        patient_id=current_user.id,
        title=case_data.title,
        symptoms=case_data.symptoms,
        severity=case_data.severity,
        description=case_data.description,
        status="pending"
    )
    
    db.add(case)
    await db.commit()
    await db.refresh(case)
    
    return {"success": True, "case": case}

@app.get("/api/patient/cases")
async def get_patient_cases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view their cases")
    
    result = await db.execute(
        select(MedicalCase).filter(MedicalCase.patient_id == current_user.id)
        .order_by(MedicalCase.created_at.desc())
    )
    cases = result.scalars().all()
    
    return {"cases": cases}

# Doctor endpoints
@app.get("/api/doctor/case-queue")
async def get_case_queue(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can access case queue")
    
    result = await db.execute(
        select(MedicalCase).filter(
            and_(
                MedicalCase.status == "pending",
                or_(
                    MedicalCase.doctor_id == None,
                    MedicalCase.doctor_id == current_user.id
                )
            )
        )
        .order_by(MedicalCase.priority.asc(), MedicalCase.created_at.asc())
    )
    cases = result.scalars().all()
    
    return {"cases": cases}

@app.post("/api/doctor/cases/{case_id}/assign")
async def assign_case_to_doctor(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can assign cases")
    
    result = await db.execute(select(MedicalCase).filter(MedicalCase.id == uuid.UUID(case_id)))
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.doctor_id = current_user.id
    case.status = "under_review"
    await db.commit()
    
    return {"success": True, "message": "Case assigned to doctor"}

@app.get("/api/doctor/stats")
async def get_doctor_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can view stats")
    
    # Get case counts
    total_cases = await db.execute(
        select(MedicalCase).filter(MedicalCase.doctor_id == current_user.id)
    )
    pending_cases = await db.execute(
        select(MedicalCase).filter(
            and_(
                MedicalCase.doctor_id == current_user.id,
                MedicalCase.status == "pending"
            )
        )
    )
    
    # Get appointments today
    today = datetime.utcnow().date()
    today_appointments = await db.execute(
        select(Appointment).filter(
            and_(
                Appointment.doctor_id == current_user.id,
                Appointment.appointment_date == today,
                Appointment.status.in_(["scheduled", "confirmed"])
            )
        )
    )
    
    return {
        "total_cases": total_cases.rowcount,
        "pending_cases": pending_cases.rowcount,
        "today_appointments": today_appointments.rowcount
    }

# Admin endpoints
@app.get("/api/admin/users")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all users")
    
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()
    
    return {"users": users}

@app.put("/api/admin/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    activate: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can activate/deactivate users")
    
    result = await db.execute(select(User).filter(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = activate
    await db.commit()
    
    return {"success": True, "message": f"User {'activated' if activate else 'deactivated'}"}

# Dashboard data
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_users = await db.execute(select(User))
    total_cases = await db.execute(select(MedicalCase))
    pending_cases = await db.execute(select(MedicalCase).filter(MedicalCase.status == "pending"))
    today_appointments = await db.execute(
        select(Appointment).filter(Appointment.appointment_date == datetime.utcnow().date())
    )
    
    return {
        "total_users": total_users.rowcount,
        "total_cases": total_cases.rowcount,
        "pending_cases": pending_cases.rowcount,
        "today_appointments": today_appointments.rowcount
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)