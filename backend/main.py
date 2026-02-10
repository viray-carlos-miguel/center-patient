# backend/main.py - UPDATED WITH SINGLE REGISTRATION ENDPOINT
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uvicorn
import asyncpg
from pydantic import BaseModel, EmailStr, validator
import os
from dotenv import load_dotenv
import json
import hashlib

load_dotenv()

# Import AI Predictor
try:
    from ai_system.core.gemini_predictor import GeminiClinicalPredictor
    predictor = GeminiClinicalPredictor()
    AI_ENABLED = True
    print("✅ Gemini AI initialized successfully")
except ImportError as e:
    print(f"⚠️ Gemini module not found: {e}")
    AI_ENABLED = False
    # Fallback to simple predictor
    class SimplePredictor:
        def analyze_symptoms(self, symptoms, patient_info):
            return {
                "disease_predictions": [{
                    "disease": "Common Cold",
                    "confidence": 65.5,
                    "matching_symptoms": [],
                    "urgency": "low"
                }],
                "risk_assessment": {
                    "risk_score": 1,
                    "urgency_level": "low",
                    "recommended_action": "Rest and monitor"
                },
                "confidence_score": 0.65,
                "educational_notes": "AI analysis for educational purposes only"
            }
    predictor = SimplePredictor()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medical_center")

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    role: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Registration(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None
    medical_license: Optional[str] = None
    specialization: Optional[str] = None
    agree_to_terms: bool
    acknowledge_educational: bool

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    first_name: str
    last_name: str
    full_name: str
    is_active: bool
    created_at: datetime

class SymptomSubmission(BaseModel):
    description: str
    duration_hours: int
    severity: int
    temperature: Optional[float] = None
    has_fever: bool = False
    has_cough: bool = False
    has_headache: bool = False
    has_nausea: bool = False
    has_fatigue: bool = False
    additional_notes: Optional[str] = None

class AIAssessment(BaseModel):
    possible_conditions: List[str]
    confidence_score: float
    recommended_tests: List[str]
    urgency_level: str
    educational_note: str

class CaseBase(BaseModel):
    symptoms: Dict[str, Any]
    ai_assessment: Dict[str, Any]
    status: str

class CaseResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    symptoms: Dict[str, Any]
    ai_assessment: AIAssessment
    status: str
    doctor_diagnosis: Optional[str] = None
    doctor_notes: Optional[str] = None
    prescription: Optional[Dict[str, Any]] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

class CaseReview(BaseModel):
    doctor_diagnosis: str
    doctor_notes: Optional[str] = None
    prescription: Optional[Dict[str, Any]] = None
    follow_up_required: bool = False
    follow_up_days: Optional[int] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    print("🚀 Starting Medical Center Backend...")
    print(f"📊 PostgreSQL URL: {DATABASE_URL}")
    
    try:
        await init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database warning: {e}")
        print("⚠️ Starting with fallback mode")
    
    yield
    
    print("👋 Shutting down...")

app = FastAPI(
    title="Medical Center API",
    description="Professional Medical Education Platform with PostgreSQL",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Database Connection Pool
pool = None

async def get_connection():
    """Get database connection from pool"""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    return pool

async def init_database():
    """Initialize PostgreSQL database with tables and demo data"""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Create users table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create medical_cases table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS medical_cases (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER,
            doctor_id INTEGER,
            symptoms JSONB NOT NULL,
            ai_assessment JSONB,
            status VARCHAR(50) DEFAULT 'pending_review' 
                CHECK (status IN ('pending_review', 'in_review', 'completed')),
            doctor_diagnosis TEXT,
            doctor_notes TEXT,
            prescription JSONB,
            follow_up_required BOOLEAN DEFAULT false,
            follow_up_days INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create patients table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            date_of_birth DATE,
            phone VARCHAR(50),
            emergency_contact VARCHAR(100),
            blood_type VARCHAR(10),
            allergies TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create doctors table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            medical_license VARCHAR(100) UNIQUE NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            years_of_experience INTEGER DEFAULT 0,
            is_available BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Check if we need to create initial admin
        admin_exists = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE email = 'admin@medical.com'"
        )
        
        if admin_exists == 0:
            print("👨‍⚕️ Creating initial admin account...")
            password_hash = hashlib.sha256("Admin@123".encode()).hexdigest()
            await conn.execute("""
            INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
            VALUES ($1, $2, 'admin', 'System', 'Admin', true)
            """, "admin@medical.com", password_hash)
            print("✅ Admin account created (email: admin@medical.com, password: Admin@123)")
        
        await conn.close()
        print("🎯 PostgreSQL database ready!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

# Authentication helper
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Medical Center API",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "status": "operational"
    }

@app.post("/api/auth/register", response_model=Dict[str, Any])
async def register_user(registration: Registration):
    """Register a new user - auto-detect role by email domain"""
    if not registration.agree_to_terms or not registration.acknowledge_educational:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must agree to terms and acknowledge educational purpose"
        )
    
    # Auto-detect role based on email domain
    email = registration.email.lower()
    if '@medical.com' in email or '@medicalcenter.com' in email or '@hospital.com' in email:
        role = 'doctor'
        print(f"🎓 Detected doctor registration: {email}")
    else:
        role = 'patient'
        print(f"👤 Detected patient registration: {email}")
    
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        # Check if email already exists
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            registration.email
        )
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(registration.password)
        
        try:
            # Start transaction
            async with conn.transaction():
                # Insert new user with auto-detected role
                result = await conn.fetchrow("""
                INSERT INTO users (
                    email, password_hash, role, first_name, last_name, 
                    is_active, created_at
                ) VALUES ($1, $2, $3, $4, $5, true, CURRENT_TIMESTAMP)
                RETURNING id, email, role, first_name, last_name, created_at
                """, 
                registration.email, 
                password_hash, 
                role,
                registration.first_name.strip(),
                registration.last_name.strip())
                
                if role == 'doctor':
                    # Doctor-specific validation
                    if not registration.medical_license or not registration.specialization:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Medical license and specialization are required for doctor registration"
                        )
                    
                    # Check if medical license already exists
                    existing_license = await conn.fetchval(
                        "SELECT COUNT(*) FROM doctors WHERE medical_license = $1",
                        registration.medical_license
                    )
                    
                    if existing_license > 0:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Medical license already registered"
                        )
                    
                    # Create doctor profile
                    await conn.execute("""
                    INSERT INTO doctors (user_id, medical_license, specialization)
                    VALUES ($1, $2, $3)
                    """, result['id'], registration.medical_license.strip(), registration.specialization.strip())
                    
                    print(f"✅ Doctor profile created for {registration.email}")
                else:
                    # Patient-specific validation
                    if not registration.date_of_birth:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Date of birth is required for patient registration"
                        )
                    
                    # Convert date string to date object
                    try:
                        dob_date = datetime.strptime(registration.date_of_birth, "%Y-%m-%d").date()
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid date format. Please use YYYY-MM-DD format."
                        )
                    
                    # Create patient profile
                    await conn.execute("""
                    INSERT INTO patients (user_id, date_of_birth, phone)
                    VALUES ($1, $2, $3)
                    """, result['id'], dob_date, registration.phone or None)
                    
                    print(f"✅ Patient profile created for {registration.email}")
        
        except asyncpg.exceptions.UniqueViolationError as e:
            if 'users_email_key' in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            elif 'doctors_medical_license_key' in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Medical license already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed. Please try again."
                )
        except Exception as e:
            print(f"Registration error details: {e}")
            if "Invalid date format" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Please use YYYY-MM-DD format."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again."
            )
        
        # Prepare response
        full_name = f"{result['first_name']} {result['last_name']}"
        if role == 'doctor':
            full_name = f"Dr. {full_name}"
        
        user_response = {
            "id": result['id'],
            "email": result['email'],
            "role": result['role'],
            "first_name": result['first_name'],
            "last_name": result['last_name'],
            "full_name": full_name,
            "is_active": True,
            "created_at": result['created_at'].isoformat() if result['created_at'] else None
        }
        
        role_message = "Doctor account created successfully" if role == 'doctor' else "Patient account created successfully"
        
        return {
            "success": True,
            "user": user_response,
            "message": role_message,
            "token": f"{role}_token_{result['id']}_{datetime.now().timestamp()}",
            "educational_note": "Educational account created - not for real medical use"
        }

@app.post("/api/auth/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """Authenticate user with PostgreSQL - NO AUTO-REGISTRATION"""
    print("=" * 50)
    print(f"🔐 LOGIN ATTEMPT")
    print(f"📧 Email: '{login_data.email}'")
    
    # --- ADMIN BYPASS: admin / admin ---
    email_trimmed = login_data.email.strip().lower()
    pass_trimmed = login_data.password.strip()
    
    if email_trimmed == "admin" and pass_trimmed == "admin":
        print("🔑 ADMIN BYPASS LOGIN")
        print("=" * 50)
        return {
            "success": True,
            "user": {
                "id": 0,
                "email": "admin@medical.com",
                "role": "doctor",
                "first_name": "Admin",
                "last_name": "User",
                "full_name": "Dr. Admin User",
                "is_active": True,
                "isEducational": True,
                "created_at": datetime.now().isoformat()
            },
            "message": "Admin bypass login successful",
            "token": f"admin-bypass-token-{datetime.now().timestamp()}"
        }
    
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        # Find user - must exist in database
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND is_active = true",
            login_data.email.strip()
        )
        
        if not user:
            print(f"❌ USER NOT FOUND: {login_data.email}")
            
            # Suggest registration based on email domain
            domain = login_data.email.split('@')[-1].lower()
            if domain == 'medical.com':
                suggestion = "Please register as a doctor first."
            else:
                suggestion = "Please register as a patient first."
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User not found. {suggestion}"
            )
        
        print(f"✅ User found: {user['email']} (Role: {user['role']})")
        
        # Calculate hash of input password
        input_hash = hash_password(login_data.password.strip())
        
        if input_hash != user['password_hash']:
            print(f"❌ PASSWORD MISMATCH!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"🎉 LOGIN SUCCESSFUL for {user['email']}!")
        print("=" * 50)
        
        # Prepare user response
        full_name = f"{user['first_name']} {user['last_name']}"
        if user['role'] == 'doctor':
            full_name = f"Dr. {full_name}"
        
        user_response = {
            "id": user['id'],
            "email": user['email'],
            "role": user['role'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": full_name,
            "is_active": user['is_active'],
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        }
        
        return {
            "success": True,
            "user": user_response,
            "message": "Login successful",
            "token": f"auth-token-{user['id']}-{datetime.now().timestamp()}"
        }

# [Keep all other endpoints the same as before...]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )