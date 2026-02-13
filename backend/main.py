# backend/main.py - UPDATED WITH SINGLE REGISTRATION ENDPOINT
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uvicorn
import aiomysql
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

# MySQL Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "medical_center")

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
    print(f"📊 MySQL Configuration: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    
    try:
        await init_database()
        print("✅ MySQL database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database warning: {e}")
        print("⚠️ Starting with fallback mode")
    
    yield
    
    print("👋 Shutting down...")

app = FastAPI(
    title="DXscope API",
    description="Advanced Medical Diagnosis Platform with AI-Powered Analysis",
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
        pool = await aiomysql.create_pool(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            minsize=1,
            maxsize=10,
            autocommit=True
        )
    return pool

async def init_database():
    """Initialize MySQL database with tables and demo data"""
    try:
        # First connect without specifying database to create it if needed
        conn = await aiomysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            autocommit=True
        )
        cursor = await conn.cursor()
        
        # Create database if it doesn't exist
        await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        await cursor.execute(f"USE {MYSQL_DATABASE}")
        
        # Create users table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('patient', 'doctor', 'admin') NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # Create medical_cases table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_cases (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            doctor_id INT,
            symptoms JSON NOT NULL,
            ai_assessment JSON,
            status ENUM('pending_review', 'in_review', 'completed') DEFAULT 'pending_review',
            doctor_diagnosis TEXT,
            doctor_notes TEXT,
            prescription JSON,
            follow_up_required BOOLEAN DEFAULT FALSE,
            follow_up_days INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
        )
        """)
        
        # Create patients table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            date_of_birth DATE,
            phone VARCHAR(50),
            emergency_contact VARCHAR(100),
            blood_type VARCHAR(10),
            allergies TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # Create doctors table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            medical_license VARCHAR(100) UNIQUE NOT NULL,
            specialization VARCHAR(100) NOT NULL,
            years_of_experience INT DEFAULT 0,
            is_available BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # Check if we need to create initial admin
        await cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ("admin@medical.com",))
        admin_exists = (await cursor.fetchone())[0]
        
        if admin_exists == 0:
            print("👨‍⚕️ Creating initial admin account...")
            password_hash = hashlib.sha256("Admin@123".encode()).hexdigest()
            await cursor.execute("""
            INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
            VALUES (%s, %s, 'admin', 'System', 'Admin', TRUE)
            """, ("admin@medical.com", password_hash))
            print("✅ Admin account created (email: admin@medical.com, password: Admin@123)")
        
        # Add demo medical cases
        await cursor.execute("SELECT COUNT(*) FROM medical_cases")
        case_count = (await cursor.fetchone())[0]
        
        if case_count == 0:
            print("🌱 Adding demo medical cases...")
            
            # Demo case 1
            await cursor.execute("""
            INSERT INTO medical_cases (title, symptoms, ai_assessment, status)
            VALUES (%s, %s, %s, 'pending_review')
            """, (
                "Persistent Headache with Fever",
                json.dumps({
                    "description": "Headache for 3 days, fever 38.5°C, fatigue, mild dizziness",
                    "duration_hours": 72,
                    "severity": 6,
                    "temperature": 38.5,
                    "has_fever": True,
                    "has_headache": True,
                    "has_fatigue": True
                }),
                json.dumps({
                    "possible_conditions": ["Tension Headache", "Viral Infection"],
                    "confidence_score": 0.75,
                    "recommended_tests": ["Physical Examination", "Temperature Check"],
                    "urgency_level": "medium",
                    "medical_note": "AI medical assessment based on symptoms"
                })
            ))
            
            # Demo case 2
            await cursor.execute("""
            INSERT INTO medical_cases (title, symptoms, ai_assessment, status)
            VALUES (%s, %s, %s, 'pending_review')
            """, (
                "Seasonal Allergy Symptoms",
                json.dumps({
                    "description": "Sneezing, runny nose, itchy eyes, congestion for 2 weeks",
                    "duration_hours": 336,
                    "severity": 3,
                    "has_cough": False,
                    "has_headache": False,
                    "has_fatigue": False
                }),
                json.dumps({
                    "possible_conditions": ["Allergic Rhinitis", "Seasonal Allergies"],
                    "confidence_score": 0.85,
                    "recommended_tests": ["Allergy Test", "Physical Examination"],
                    "urgency_level": "low",
                    "medical_note": "AI medical assessment based on symptoms"
                })
            ))
            
            print("✅ Demo medical cases added!")
        
        print("🎯 MySQL database ready!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        try:
            if cursor:
                await cursor.close()
        except:
            pass
        try:
            if conn:
                await conn.close()
        except:
            pass

# Authentication helper
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# API Routes
@app.get("/")
async def root():
    return {
        "message": "DXscope API",
        "version": "2.0.0",
        "database": "MySQL",
        "status": "operational",
        "platform": "Advanced Medical Diagnosis Platform"
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
        cursor = await conn.cursor()
        
        # Check if email already exists
        await cursor.execute("SELECT id FROM users WHERE email = %s", (registration.email,))
        existing_user = await cursor.fetchone()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(registration.password)
        
        try:
            # Insert new user with auto-detected role
            await cursor.execute("""
            INSERT INTO users (
                email, password_hash, role, first_name, last_name, 
                is_active, created_at
            ) VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
            """, (
                registration.email, 
                password_hash, 
                role,
                registration.first_name.strip(),
                registration.last_name.strip()
            ))
            
            # Get the inserted user ID
            await cursor.execute("SELECT * FROM users WHERE email = %s", (registration.email,))
            result = await cursor.fetchone()
            
            if role == 'doctor':
                # Doctor-specific validation
                if not registration.medical_license or not registration.specialization:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Medical license and specialization are required for doctor registration"
                    )
                
                # Check if medical license already exists
                await cursor.execute("SELECT COUNT(*) FROM doctors WHERE medical_license = %s", (registration.medical_license,))
                existing_license = (await cursor.fetchone())[0]
                
                if existing_license > 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Medical license already registered"
                    )
                
                # Create doctor profile
                await cursor.execute("""
                INSERT INTO doctors (user_id, medical_license, specialization)
                VALUES (%s, %s, %s)
                """, (result[0], registration.medical_license.strip(), registration.specialization.strip()))
                
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
                await cursor.execute("""
                INSERT INTO patients (user_id, date_of_birth, phone)
                VALUES (%s, %s, %s)
                """, (result[0], dob_date, registration.phone or None))
                
                print(f"✅ Patient profile created for {registration.email}")
        
        except Exception as e:
            print(f"Registration error details: {e}")
            if "Duplicate entry" in str(e) and "email" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            elif "Duplicate entry" in str(e) and "medical_license" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Medical license already registered"
                )
            elif "Invalid date format" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Please use YYYY-MM-DD format."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again."
            )
        finally:
            if cursor:
                await cursor.close()
        
        # Prepare response - fix field mapping from database tuple
        # result tuple: (id, email, password_hash, role, first_name, last_name, is_active, created_at, updated_at)
        full_name = f"{result[4]} {result[5]}"  # first_name, last_name from tuple
        if role == 'doctor':
            full_name = f"Dr. {full_name}"
        
        user_response = {
            "id": result[0],
            "email": result[1],
            "role": result[3],
            "first_name": result[4],
            "last_name": result[5],
            "full_name": full_name,
            "is_active": result[6],
            "created_at": result[7].isoformat() if result[7] else None
        }
        
        role_message = "Doctor account created successfully" if role == 'doctor' else "Patient account created successfully"
        
        return {
            "success": True,
            "user": user_response,
            "message": role_message,
            "token": f"{role}_token_{result[0]}_{datetime.now().timestamp()}",
            "medical_note": "Medical account created for clinical use"
        }

@app.post("/api/auth/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """Authenticate user with MySQL - NO AUTO-REGISTRATION"""
    print("=" * 50)
    print(f"🔐 LOGIN ATTEMPT")
    print(f"📧 Email: '{login_data.email}'")
    
    # --- ADMIN BYPASS: admin / admin ---
    email_trimmed = login_data.email.strip().lower()
    pass_trimmed = login_data.password.strip()
    
    if (email_trimmed == "admin" and pass_trimmed == "admin") or (email_trimmed == "admin@medical.com" and pass_trimmed == "admin") or (email_trimmed == "admin@medical.com" and pass_trimmed == "admin@123"):
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
        cursor = await conn.cursor()
        
        # Find user - must exist in database
        await cursor.execute("SELECT * FROM users WHERE email = %s AND is_active = TRUE", (login_data.email.strip(),))
        user = await cursor.fetchone()
        
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
        
        print(f"✅ User found: {user[1]} (Role: {user[3]})")
        
        # Calculate hash of input password
        input_hash = hash_password(login_data.password.strip())
        
        if input_hash != user[2]:  # password_hash is at index 2
            print(f"❌ PASSWORD MISMATCH!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"🎉 LOGIN SUCCESSFUL for {user[1]}!")
        print("=" * 50)
        
        # Prepare user response
        full_name = f"{user[3]} {user[4]}"  # first_name, last_name
        if user[3] == 'doctor':
            full_name = f"Dr. {full_name}"
        
        user_response = {
            "id": user[0],
            "email": user[1],
            "role": user[3],
            "first_name": user[3],
            "last_name": user[4],
            "full_name": full_name,
            "is_active": user[5],
            "created_at": user[6].isoformat() if user[6] else None
        }
        
        try:
            return {
                "success": True,
                "user": user_response,
                "message": "Login successful",
                "token": f"auth-token-{user[0]}-{datetime.now().timestamp()}"
            }
        finally:
            if cursor:
                await cursor.close()

# Get patient cases
@app.get("/api/patient/cases", response_model=Dict[str, Any])
async def get_patient_cases():
    """Get cases for the current patient"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Get all cases (simplified for demo)
        await cursor.execute("""
        SELECT id, title, symptoms, ai_assessment, status, created_at
        FROM medical_cases 
        ORDER BY created_at DESC
        """)
        
        cases = await cursor.fetchall()
        
        # Convert to response format
        case_list = []
        for case in cases:
            case_list.append({
                "id": case[0],
                "title": case[1],
                "symptoms": json.loads(case[2]) if case[2] else {},
                "ai_assessment": json.loads(case[3]) if case[3] else {},
                "status": case[4],
                "created_at": case[5].isoformat() if case[5] else None
            })
        
        await cursor.close()
        
        return {
            "success": True,
            "cases": case_list,
            "total": len(case_list)
        }

# Get doctor cases
@app.get("/api/doctor/cases", response_model=Dict[str, Any])
async def get_doctor_cases():
    """Get cases for doctor review"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Get all cases for doctor review
        await cursor.execute("""
        SELECT id, title, symptoms, ai_assessment, status, created_at
        FROM medical_cases 
        WHERE status IN ('pending_review', 'in_review')
        ORDER BY created_at DESC
        """)
        
        cases = await cursor.fetchall()
        
        # Convert to response format
        case_list = []
        for case in cases:
            case_list.append({
                "id": case[0],
                "title": case[1],
                "symptoms": json.loads(case[2]) if case[2] else {},
                "ai_assessment": json.loads(case[3]) if case[3] else {},
                "status": case[4],
                "created_at": case[5].isoformat() if case[5] else None
            })
        
        await cursor.close()
        
        return {
            "success": True,
            "cases": case_list,
            "total": len(case_list)
        }

# Review case
@app.post("/api/cases/{case_id}/review", response_model=Dict[str, Any])
async def review_case(case_id: int, review_data: Dict[str, Any]):
    """Review a medical case"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Update case with review
        await cursor.execute("""
        UPDATE medical_cases 
        SET doctor_diagnosis = %s, doctor_notes = %s, status = 'completed', reviewed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """, (
            review_data.get("doctor_diagnosis", ""),
            review_data.get("doctor_notes", ""),
            case_id
        ))
        
        await cursor.close()
        
        return {
            "success": True,
            "message": "Case reviewed successfully"
        }

# Submit symptoms
@app.post("/api/cases/submit", response_model=Dict[str, Any])
async def submit_symptoms(symptom_data: Dict[str, Any]):
    """Submit new symptom case"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Insert new case
        await cursor.execute("""
        INSERT INTO medical_cases (title, symptoms, ai_assessment, status)
        VALUES (%s, %s, %s, 'pending_review')
        """, (
            symptom_data.get("title", "New Symptom Case"),
            json.dumps(symptom_data.get("symptoms", {})),
            json.dumps(symptom_data.get("ai_assessment", {}))
        ))
        
        case_id = cursor.lastrowid
        
        await cursor.close()
        
        return {
            "success": True,
            "case_id": case_id,
            "message": "Symptoms submitted successfully"
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )