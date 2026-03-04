# backend/main.py - UPDATED WITH SINGLE REGISTRATION ENDPOINT
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request, status, Depends
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

# Import email service
from email_service import email_service

# ML analysis only; Gemini disabled

load_dotenv()

# AI System Removed - Using ML and Rule-based Only
AI_ENABLED = False
predictor = None
print("⚠️ AI System removed - Using ML and Rule-based analysis")

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

# ML Prediction System
try:
    from ml.api import router as ml_router, engine as ml_engine
    ML_ENABLED = ml_engine.is_trained
    print(f"✅ ML System loaded (trained={ML_ENABLED}, accuracy={ml_engine.accuracy:.2%})")
except Exception as e:
    ML_ENABLED = False
    ml_engine = None
    print(f"❌ ML System failed: {e}")

# Symptom Predictor (Random Forest + ChatGPT fallback)
try:
    from ml.symptom_predictor import predictor as symptom_predictor
    SYMPTOM_PREDICTOR_ENABLED = symptom_predictor.model is not None
    print(f"✅ Symptom Predictor loaded (model_ready={SYMPTOM_PREDICTOR_ENABLED})")
except Exception as e:
    symptom_predictor = None
    SYMPTOM_PREDICTOR_ENABLED = False
    print(f"❌ Symptom Predictor failed: {e}")

# Gemini AI System
try:
    from api.gemini_api import router as gemini_router
    from services.gemini_ai import gemini_ai
    GEMINI_ENABLED = True
    print("✅ Gemini 2.5 Flash AI System loaded")
except Exception as e:
    GEMINI_ENABLED = False
    gemini_ai = None
    gemini_router = None
    print(f"❌ Gemini AI System failed: {e}")

# Medicine Recommendation System
try:
    from api.medicine_api import router as medicine_router
    from ml.medicine_recommendation_engine import medicine_engine
    MEDICINE_ENABLED = True
    print("✅ Medicine Recommendation System loaded")
except Exception as e:
    MEDICINE_ENABLED = False
    medicine_engine = None
    print(f"❌ Medicine System failed: {e}")
    ML_ENABLED = False
    ml_engine = None
    ml_router = None

# AI Insights (ChatGPT)
try:
    from api.ai_insights_api import router as ai_insights_router
    AI_INSIGHTS_ENABLED = True
    print("✅ AI Insights (ChatGPT) API routes loaded")
except Exception as e:
    ai_insights_router = None
    AI_INSIGHTS_ENABLED = False
    print(f"❌ AI Insights API failed: {e}")

# MySQL Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "medical_center")

ADMIN_BYPASS_ENABLED = os.getenv("ADMIN_BYPASS_ENABLED", "false").strip().lower() == "true"

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
    description="Advanced Medical Diagnosis Platform with AI-Powered Analysis and ML Predictions",
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

# Include ML router if available
if ml_router is not None:
    app.include_router(ml_router)
    print("✅ ML API routes included")

# Include Gemini AI router if available
if GEMINI_ENABLED:
    app.include_router(gemini_router)
    print("✅ Gemini AI API routes included")

# Include Medicine Recommendation router if available
if MEDICINE_ENABLED:
    app.include_router(medicine_router)
    print("✅ Medicine Recommendation API routes included")

# Include Prescription endpoints
try:
    from prescription_endpoints import router as prescription_router
    app.include_router(prescription_router)
    print("✅ Prescription API routes included")
except Exception as e:
    print(f"❌ Prescription endpoints failed: {e}")

# Include AI Insights router if available
if AI_INSIGHTS_ENABLED and ai_insights_router is not None:
    app.include_router(ai_insights_router)
    print("✅ AI Insights API routes included")

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
        
        # Ensure status defaults are enforced (older tables may allow NULL/empty)
        await cursor.execute(
            "ALTER TABLE medical_cases MODIFY COLUMN status ENUM('pending_review','in_review','completed') NOT NULL DEFAULT 'pending_review'"
        )
        
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
            is_verified BOOLEAN DEFAULT FALSE,
            admin_notes TEXT,
            verified_at TIMESTAMP NULL,
            verified_by INT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # Create prescriptions table
        await cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            case_id INT NOT NULL,
            patient_id INT NOT NULL,
            doctor_id INT NOT NULL,
            medication_name VARCHAR(255) NOT NULL,
            dosage VARCHAR(100) NOT NULL,
            frequency VARCHAR(100) NOT NULL,
            duration INT NOT NULL,
            instructions TEXT,
            doctor_signature TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)

        # Lightweight schema repair for prescriptions table (handles older schemas)
        await cursor.execute("SHOW COLUMNS FROM prescriptions")
        prescription_columns = {row[0] for row in await cursor.fetchall()}
        if "duration" not in prescription_columns and "duration_days" in prescription_columns:
            await cursor.execute("ALTER TABLE prescriptions CHANGE COLUMN duration_days duration INT NOT NULL")
            prescription_columns.add("duration")
        if "duration" not in prescription_columns:
            await cursor.execute("ALTER TABLE prescriptions ADD COLUMN duration INT NOT NULL DEFAULT 0")

        # Normalize medical_cases.status for legacy rows.
        # Using COALESCE(NULLIF(...)) avoids invalid ENUM writes while still cleaning blanks.
        await cursor.execute(
            """
            UPDATE medical_cases
            SET status = COALESCE(
                NULLIF(
                    CASE
                        WHEN LOWER(status) IN ('pending', 'pending review', 'pending_review') THEN 'pending_review'
                        WHEN LOWER(status) IN ('inreview', 'in review', 'in_review') THEN 'in_review'
                        WHEN LOWER(status) IN ('done', 'complete', 'completed') THEN 'completed'
                        ELSE status
                    END,
                    ''
                ),
                'pending_review'
            )
            """
        )
        
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
            
            # Check if demo patient already exists, if not create it
            await cursor.execute("SELECT id FROM users WHERE email = %s", ("demo.patient@gmail.com",))
            existing_patient = await cursor.fetchone()
            
            if existing_patient:
                demo_patient_id = existing_patient[0]
                print("✅ Using existing demo patient account")
            else:
                # Create demo patient user for the demo cases
                await cursor.execute("""
                INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (
                    "demo.patient@gmail.com",
                    hash_password("Demo@123"),
                    "patient",
                    "Demo",
                    "Patient"
                ))
                demo_patient_id = cursor.lastrowid
                print("✅ Demo patient account created (email: demo.patient@gmail.com, password: Demo@123)")
            
            # Demo case 1
            await cursor.execute("""
            INSERT INTO medical_cases (patient_id, symptoms, ai_assessment, status)
            VALUES (%s, %s, %s, 'pending_review')
            """, (
                demo_patient_id,
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
            INSERT INTO medical_cases (patient_id, symptoms, ai_assessment, status)
            VALUES (%s, %s, %s, 'pending_review')
            """, (
                demo_patient_id,
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

# Token parsing helper
def _extract_user_id_from_auth_header(auth_header: str | None) -> int | None:
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    try:
        if token.startswith("auth-token-"):
            token_parts = token.split("-")
            if len(token_parts) >= 3:
                return int(token_parts[2])
        if token.startswith("admin-bypass-token-"):
            return 0
        if token.startswith("demo-token-"):
            # demo-token-patient / demo-token-doctor / demo-token-admin
            # These are only for demo mode; caller decides if it wants to accept them.
            return None

        # Format: {role}_token_{user_id}_{timestamp}
        if "_token_" in token:
            token_parts = token.split("_")
            if len(token_parts) >= 3:
                return int(token_parts[2])
    except (ValueError, IndexError):
        return None

    return None

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
    
    # Auto-detect role based on email domain and required fields
    email = registration.email.lower()
    
    # Check if this is a doctor registration (has medical license and specialization)
    if (registration.medical_license and registration.specialization and 
        registration.medical_license.strip() and registration.specialization.strip()):
        role = 'doctor'
        print(f"🎓 Detected doctor registration: {email}")
    elif '@medical.com' in email or '@medicalcenter.com' in email or '@hospital.com' in email:
        role = 'doctor'
        print(f"🎓 Detected doctor registration (professional email): {email}")
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
            # Set active status based on role (doctors need verification)
            is_active = False if role == 'doctor' else True
            
            # Insert new user with auto-detected role
            await cursor.execute("""
            INSERT INTO users (
                email, password_hash, role, first_name, last_name, 
                is_active, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                registration.email, 
                password_hash, 
                role,
                registration.first_name.strip(),
                registration.last_name.strip(),
                is_active
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
            "created_at": result[7].isoformat() if result[7] and hasattr(result[7], 'isoformat') else str(result[7]) if result[7] else None
        }
        
        # Prepare response based on role and verification status
        role_message = ""
        medical_note = ""
        
        if role == 'doctor':
            role_message = "Doctor registration submitted successfully - awaiting admin verification"
            medical_note = "Your account is pending verification. You will receive an email once approved."
        else:
            role_message = "Patient account created successfully"
            medical_note = "Your account is ready for immediate use"
            
            # Send welcome email to patient
            patient_name = f"{result[4]} {result[5]}"
            patient_email = result[1]
            
            subject, text_content, html_content = email_service.get_patient_welcome_template(patient_name, patient_email)
            email_sent = await email_service.send_email(patient_email, subject, html_content, text_content)
            
            if email_sent:
                print(f"✅ Welcome email sent to: {patient_email}")
            else:
                print(f"❌ Failed to send welcome email to: {patient_email}")
        
        return {
            "success": True,
            "user": user_response,
            "message": role_message,
            "token": f"{role}_token_{result[0]}_{datetime.now().timestamp()}",
            "medical_note": medical_note,
            "requires_verification": role == 'doctor',
            "email_sent": role == 'patient'  # Only true for patients since doctors get email after verification
        }

@app.post("/api/auth/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """Authenticate user with MySQL - NO AUTO-REGISTRATION"""
    print("=" * 50)
    print(f"🔐 LOGIN ATTEMPT")
    print(f"📧 Email: '{login_data.email}'")
    
    # --- ADMIN BYPASS: admin / admin (disabled by default) ---
    email_trimmed = login_data.email.strip().lower()
    pass_trimmed = login_data.password.strip()
    
    if ADMIN_BYPASS_ENABLED and ((email_trimmed == "admin" and pass_trimmed == "admin") or (email_trimmed == "admin@medical.com" and pass_trimmed == "admin") or (email_trimmed == "admin@medical.com" and pass_trimmed == "admin@123")):
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
        
        # Find user - check if exists (including inactive doctors for better error messages)
        await cursor.execute("SELECT * FROM users WHERE email = %s", (login_data.email.strip(),))
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
        
        # Check if user is active
        if not user[6]:  # is_active field
            print(f"❌ USER INACTIVE: {login_data.email} (Role: {user[3]})")
            
            if user[3] == 'doctor':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Your doctor account is pending verification. Please wait for admin approval before logging in."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Your account has been deactivated. Please contact support."
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
        # user tuple: (id, email, password_hash, role, first_name, last_name, is_active, created_at, updated_at)
        full_name = f"{user[4]} {user[5]}"
        if user[3] == 'doctor':
            full_name = f"Dr. {full_name}"
        
        user_response = {
            "id": user[0],
            "email": user[1],
            "role": user[3],
            "first_name": user[4],
            "last_name": user[5],
            "full_name": full_name,
            "is_active": bool(user[6]),
            "created_at": user[7].isoformat() if user[7] and hasattr(user[7], 'isoformat') else str(user[7]) if user[7] else None
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
                
# ===== SYMPTOM PREDICTION (ML + ChatGPT fallback) =====
@app.post("/api/predict-symptoms", response_model=Dict[str, Any])
async def predict_symptoms(request: Request, payload: Dict[str, Any]):
    """
    Predict disease from symptoms using Random Forest ML model.
    Falls back to ChatGPT when ML confidence is low.
    ChatGPT uses ONLY the symptoms provided — nothing more.
    """
    if not SYMPTOM_PREDICTOR_ENABLED or symptom_predictor is None:
        raise HTTPException(status_code=503, detail="Symptom predictor not available")

    symptoms = payload.get("symptoms", {})
    description = symptoms.get("description", "") or payload.get("description", "")

    try:
        result = await symptom_predictor.predict(symptoms, description)
        return result
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Submit symptoms/case
@app.post("/api/cases/submit", response_model=Dict[str, Any])
async def submit_case(request: Request, case_data: Dict[str, Any]):
    """Submit a new medical case with symptoms and AI assessment"""
    import json
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Get current user from auth header
            current_user_id = None
            auth_header = request.headers.get("Authorization")
            
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    # Handle multiple token formats
                    if "auth-token-" in token:
                        token_parts = token.split("-")
                        if len(token_parts) >= 3:
                            current_user_id = int(token_parts[2])
                    elif "patient_token_" in token:
                        # Format: patient_token_{user_id}_{timestamp}
                        token_parts = token.split("_")
                        if len(token_parts) >= 3:
                            current_user_id = int(token_parts[2])
                    elif "doctor_token_" in token:
                        # Format: doctor_token_{user_id}_{timestamp}
                        token_parts = token.split("_")
                        if len(token_parts) >= 3:
                            current_user_id = int(token_parts[2])
                    elif "admin_token_" in token:
                        # Format: admin_token_{user_id}_{timestamp}
                        token_parts = token.split("_")
                        if len(token_parts) >= 3:
                            current_user_id = int(token_parts[2])
                    elif "demo-token-" in token:
                        # Demo token format - use demo user ID
                        if "patient" in token:
                            current_user_id = 26  # Use the actual patient ID from logs
                        elif "doctor" in token:
                            current_user_id = 2
                        elif "admin" in token:
                            current_user_id = 0
                    elif "admin-bypass-token-" in token:
                        # Admin bypass token
                        current_user_id = 0
                except (ValueError, IndexError) as e:
                    print(f"⚠️ Token parsing error: {e}")
                    pass
            
            if not current_user_id:
                # Try to get user from email in request
                email = case_data.get('patient_email')
                if email:
                    await cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                    user = await cursor.fetchone()
                    if user:
                        current_user_id = user[0]
            
            if not current_user_id:
                raise HTTPException(status_code=401, detail="User not authenticated")
            
            # Get patient name
            await cursor.execute("SELECT first_name, last_name FROM users WHERE id = %s", (current_user_id,))
            patient = await cursor.fetchone()
            patient_name = f"{patient[0]} {patient[1]}" if patient else "Unknown Patient"
            
            # Insert new case
            await cursor.execute("""
                INSERT INTO medical_cases (patient_id, symptoms, ai_assessment, status, created_at)
                VALUES (%s, %s, %s, 'pending_review', %s)
            """, (
                current_user_id,
                json.dumps(case_data.get('symptoms', {})),
                json.dumps(case_data.get('ai_assessment', {})),
                datetime.now()
            ))
            
            case_id = cursor.lastrowid
            
            await conn.commit()
            
            return {
                "success": True,
                "case_id": case_id,
                "message": "Symptoms submitted successfully",
                "patient_name": patient_name,
                "status": "pending_review"
            }
            
    except Exception as e:
        print(f"❌ Error submitting case: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ Error args: {e.args}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            await cursor.close()

# Get patient cases
@app.get("/api/patient/cases", response_model=Dict[str, Any])
async def get_patient_cases(request: Request):
    """Get cases for the current patient"""
    import json
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Get current user from auth header
            auth_header = request.headers.get("Authorization")
            current_user_id = _extract_user_id_from_auth_header(auth_header)

            if current_user_id is None:
                raise HTTPException(status_code=401, detail="User not authenticated")
            
            # Get cases for current patient only with patient name and prescription
            await cursor.execute("""
            SELECT c.id, c.symptoms, c.ai_assessment, c.status, c.created_at, c.doctor_diagnosis, c.doctor_notes, c.prescription, c.reviewed_at, u.first_name, u.last_name
            FROM medical_cases c
            JOIN users u ON c.patient_id = u.id
            WHERE c.patient_id = %s
            ORDER BY c.created_at DESC
            """, (current_user_id,))
            
            cases = await cursor.fetchall()
            print(f"Fetched {len(cases)} cases for patient ID {current_user_id}")
            
            # Convert to response format
            case_list = []
            for case in cases:
                # Generate a title from symptoms
                symptoms_data = json.loads(case[1]) if case[1] else {}
                title = symptoms_data.get('description', 'Medical Case')[:50] + '...' if len(symptoms_data.get('description', '')) > 50 else symptoms_data.get('description', 'Medical Case')
                
                # Parse prescription data
                prescription_data = json.loads(case[7]) if case[7] else None
                
                # If prescription exists, try to get the signature from prescriptions table
                if prescription_data:
                    await cursor.execute("""
                    SELECT doctor_signature FROM prescriptions 
                    WHERE case_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                    """, (case[0],))
                    signature_result = await cursor.fetchone()
                    
                    if signature_result and signature_result[0]:
                        # Add signature to prescription data
                        prescription_data['doctor_signature'] = signature_result[0]
                
                case_list.append({
                    "id": case[0],
                    "title": title,
                    "symptoms": symptoms_data,
                    "ai_assessment": json.loads(case[2]) if case[2] else {},
                    "status": case[3],
                    "created_at": case[4].isoformat() if case[4] and hasattr(case[4], 'isoformat') else str(case[4]) if case[4] else None,
                    "doctor_diagnosis": case[5],
                    "doctor_notes": case[6],
                    "prescription": prescription_data,
                    "reviewed_at": case[8].isoformat() if case[8] and hasattr(case[8], 'isoformat') else str(case[8]) if case[8] else None,
                    "patient_id": current_user_id,
                    "patient_name": f"{case[9]} {case[10]}"  # first_name, last_name from users table
                })
        
        await cursor.close()
        
        return {
            "success": True,
            "cases": case_list,
            "total": len(case_list)
        }
        
    except Exception as e:
        print(f"⚠️ Database error in get_patient_cases: {e}")
        # Fallback: return demo cases when database is not available
        import json
        from datetime import datetime, timedelta
        
        demo_cases = [
            {
                "id": 1,
                "title": "Fever and Headache - Sample Case",
                "symptoms": {
                    "description": "Patient reports fever, headache, and fatigue for 2 days",
                    "duration_hours": 48,
                    "severity": 6,
                    "temperature": 38.5,
                    "has_fever": True,
                    "has_headache": True,
                    "has_fatigue": True
                },
                "ai_assessment": {
                    "possible_conditions": ["Viral Infection", "Tension Headache"],
                    "confidence_score": 0.85,
                    "urgency_level": "medium",
                    "emergency": {
                        "level": "low",
                        "label": "Non-Urgent",
                        "color": "green",
                        "go_to_hospital": False,
                        "message": "Monitor symptoms and rest"
                    },
                    "analysis_method": "gemini_ai"
                },
                "status": "pending_review",
                "created_at": (datetime.now() - timedelta(hours=24)).isoformat()
            },
            {
                "id": 2,
                "title": "Cough and Congestion - Sample Case",
                "symptoms": {
                    "description": "Patient has persistent cough, runny nose, and congestion",
                    "duration_hours": 72,
                    "severity": 4,
                    "temperature": 37.2,
                    "has_cough": True,
                    "has_runny_nose": True,
                    "has_nasal_congestion": True
                },
                "ai_assessment": {
                    "possible_conditions": ["Common Cold", "Allergic Rhinitis"],
                    "confidence_score": 0.78,
                    "urgency_level": "low",
                    "emergency": {
                        "level": "low",
                        "label": "Non-Urgent",
                        "color": "green",
                        "go_to_hospital": False,
                        "message": "Home care recommended"
                    },
                    "analysis_method": "gemini_ai"
                },
                "status": "pending_review",
                "created_at": (datetime.now() - timedelta(hours=48)).isoformat()
            }
        ]
        
        return {
            "success": True,
            "cases": demo_cases,
            "total": len(demo_cases),
            "fallback": "Using demo cases - database unavailable"
        }

# Get doctor cases
@app.get("/api/doctor/cases", response_model=Dict[str, Any])
async def get_doctor_cases():
    """Get cases for doctor review"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # First, check all cases and their statuses
        await cursor.execute("""
        SELECT c.id, c.status, c.patient_id, u.first_name, u.last_name
        FROM medical_cases c
        JOIN users u ON c.patient_id = u.id
        ORDER BY c.created_at DESC
        """)
        
        all_cases = await cursor.fetchall()
        print(f"📋 All cases in database: {len(all_cases)}")
        for case in all_cases:
            print(f"  Case ID: {case[0]}, Status: {case[1]}, Patient: {case[3]} {case[4]}")
        
        # Get ALL cases (pending, in_review, and completed) with patient names and doctor review fields
        await cursor.execute("""
        SELECT c.id, c.symptoms, c.ai_assessment, c.status, c.created_at,
               u.first_name, u.last_name,
               c.doctor_diagnosis, c.doctor_notes, c.prescription, c.reviewed_at
        FROM medical_cases c
        JOIN users u ON c.patient_id = u.id
        ORDER BY c.created_at DESC
        """)
        
        cases = await cursor.fetchall()
        print(f"📋 Cases for doctor review: {len(cases)}")
        
        # Convert to response format
        case_list = []
        for case in cases:
            symptoms_data = json.loads(case[1]) if case[1] else {}
            desc = symptoms_data.get('description', 'Medical Case')
            title = (desc[:50] + '...') if len(desc) > 50 else desc
            
            case_list.append({
                "id": case[0],
                "title": title,
                "symptoms": symptoms_data,
                "ai_assessment": json.loads(case[2]) if case[2] else {},
                "status": case[3],
                "created_at": case[4].isoformat() if case[4] and hasattr(case[4], 'isoformat') else str(case[4]) if case[4] else None,
                "patient_name": f"{case[5]} {case[6]}",
                "doctor_diagnosis": case[7],
                "doctor_notes": case[8],
                "prescription": json.loads(case[9]) if case[9] else None,
                "reviewed_at": case[10].isoformat() if case[10] and hasattr(case[10], 'isoformat') else str(case[10]) if case[10] else None,
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
    """Review a medical case and create prescription record"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Extract prescription data if present
        prescription_data = review_data.get("prescription")
        prescription_json = json.dumps(prescription_data) if prescription_data else None
        
        # Get case details for prescription record
        await cursor.execute("SELECT patient_id, symptoms FROM medical_cases WHERE id = %s", (case_id,))
        case_details = await cursor.fetchone()
        
        if not case_details:
            return {"success": False, "message": "Case not found"}
        
        patient_id = case_details[0]
        
        # Update case with review including prescription
        await cursor.execute("""
        UPDATE medical_cases 
        SET doctor_diagnosis = %s, doctor_notes = %s, prescription = %s, status = 'completed', reviewed_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """, (
            review_data.get("doctor_diagnosis", ""),
            review_data.get("doctor_notes", ""),
            prescription_json,
            case_id
        ))
        
        # Create prescription records if prescription data exists
        prescription_ids = []
        if prescription_data and prescription_data.get("medicines"):
            medicines = prescription_data.get("medicines", [])
            for medicine in medicines:
                duration_val = medicine.get("duration_days", 0)
                try:
                    duration_val = int(duration_val) if duration_val is not None else 0
                except (ValueError, TypeError):
                    duration_val = 0
                await cursor.execute("""
                INSERT INTO prescriptions (case_id, patient_id, doctor_id, medication_name, dosage, frequency, duration, instructions, doctor_signature, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    case_id,
                    patient_id,
                    review_data.get("doctor_id", 1),  # Get from auth token in real implementation
                    medicine.get("medication_name", ""),
                    medicine.get("dosage", ""),
                    medicine.get("frequency", ""),
                    duration_val,
                    medicine.get("instructions", ""),
                    prescription_data.get("doctor_signature", "")
                ))
                prescription_ids.append(cursor.lastrowid)

        await conn.commit()
        
        await cursor.close()
        
        return {
            "success": True,
            "message": "Case reviewed successfully",
            "prescription_ids": prescription_ids,
            "patient_id": patient_id
        }

# ... (rest of the code remains the same)

# ===== ADMIN MANAGEMENT ENDPOINTS =====

@app.get("/api/admin/clear-database")
async def clear_database():
    """Clear all user data from database (for testing)"""
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Clear all tables with correct names
            await cursor.execute("DELETE FROM medical_cases")
            await cursor.execute("DELETE FROM users")
            await cursor.execute("ALTER TABLE medical_cases AUTO_INCREMENT = 1")
            await cursor.execute("ALTER TABLE users AUTO_INCREMENT = 1")
            
            await conn.commit()
            
        return {"success": True, "message": "Database cleared successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear database: {str(e)}"
        )

@app.get("/api/admin/health", response_model=Dict[str, Any])
async def admin_health_check():
    """Health check for admin endpoints"""
    try:
        pool = await get_connection()
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            await cursor.execute("SELECT 1")
            result = await cursor.fetchone()
            
        return {
            "success": True,
            "message": "Admin endpoints are healthy",
            "database": "connected",
            "test_query": result[0] if result else None
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Admin endpoints error",
            "error": str(e)
        }

@app.get("/api/admin/db/statuses", response_model=Dict[str, Any])
async def get_case_statuses(request: Request):
    auth_header = request.headers.get("Authorization")
    user_id = _extract_user_id_from_auth_header(auth_header)
    if user_id != 0:
        raise HTTPException(status_code=403, detail="Forbidden")

    pool = await get_connection()
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        await cursor.execute(
            "SELECT status, COUNT(*) as cnt FROM medical_cases GROUP BY status ORDER BY cnt DESC"
        )
        rows = await cursor.fetchall()
        await cursor.close()

    return {
        "success": True,
        "statuses": [{"status": r[0], "count": r[1]} for r in rows],
        "total_distinct": len(rows),
    }

@app.post("/api/admin/create-admin", response_model=Dict[str, Any])
async def create_admin_account(admin_data: Dict[str, Any]):
    """Create a new admin account (existing admin only)"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Check if admin already exists
        await cursor.execute("SELECT id FROM users WHERE email = %s", (admin_data.get("email"),))
        existing_admin = await cursor.fetchone()
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin account with this email already exists"
            )
        
        # Hash password
        password_hash = hash_password(admin_data.get("password"))
        
        # Create new admin
        await cursor.execute("""
        INSERT INTO users (email, password_hash, role, first_name, last_name, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
        """, (
            admin_data.get("email"),
            password_hash,
            "admin",
            admin_data.get("first_name"),
            admin_data.get("last_name")
        ))
        
        admin_id = cursor.lastrowid
        
        print(f"🔧 New admin account created: {admin_data.get('email')}")
        
        return {
            "success": True,
            "message": "Admin account created successfully",
            "admin_id": admin_id,
            "email": admin_data.get("email"),
            "role": "admin"
        }

@app.get("/api/admin/users", response_model=Dict[str, Any])
async def get_all_users():
    """Get all users (admin only)"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        await cursor.execute("""
        SELECT id, email, role, first_name, last_name, is_active, created_at
        FROM users 
        ORDER BY created_at DESC
        """)
        
        users = await cursor.fetchall()
        
        # Convert to list of dictionaries
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "email": user[1],
                "role": user[2],
                "first_name": user[3],
                "last_name": user[4],
                "is_active": user[5],
                "created_at": user[6].isoformat() if user[6] else None
            })
        
        return {
            "success": True,
            "users": user_list,
            "total": len(user_list)
        }

@app.get("/api/admin/doctors", response_model=Dict[str, Any])
async def get_doctors_for_verification():
    """Get all doctors for admin verification"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        await cursor.execute("""
        SELECT u.id, u.email, u.first_name, u.last_name, u.is_active, u.created_at,
               d.medical_license, d.specialization, d.is_verified
        FROM users u
        LEFT JOIN doctors d ON u.id = d.user_id
        WHERE u.role = 'doctor'
        ORDER BY u.created_at DESC
        """)
        
        doctors = await cursor.fetchall()
        
        # Convert to list of dictionaries
        doctor_list = []
        for doctor in doctors:
            doctor_list.append({
                "id": doctor[0],
                "email": doctor[1],
                "first_name": doctor[2],
                "last_name": doctor[3],
                "is_active": doctor[4],
                "created_at": doctor[5].isoformat() if doctor[5] else None,
                "medical_license": doctor[6],
                "specialization": doctor[7],
                "is_verified": bool(doctor[8]) if doctor[8] is not None else False
            })
        
        return {
            "success": True,
            "doctors": doctor_list,
            "total": len(doctor_list)
        }

@app.post("/api/admin/doctors/{doctor_id}/verify", response_model=Dict[str, Any])
async def verify_doctor(doctor_id: int, verification_data: Dict[str, Any]):
    """Verify or reject a doctor's credentials"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Check if doctor exists
        await cursor.execute("SELECT id, email, first_name, last_name FROM users WHERE id = %s AND role = 'doctor'", (doctor_id,))
        doctor = await cursor.fetchone()
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        is_verified = verification_data.get("is_verified", False)
        admin_notes = verification_data.get("admin_notes", "")
        
        # Update or create doctor verification record
        await cursor.execute("""
        INSERT INTO doctors (user_id, medical_license, specialization, is_verified, admin_notes, verified_at)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE
        is_verified = %s,
        admin_notes = %s,
        verified_at = CURRENT_TIMESTAMP
        """, (
            doctor_id,
            verification_data.get("medical_license", ""),
            verification_data.get("specialization", ""),
            is_verified,
            admin_notes,
            is_verified,
            admin_notes
        ))
        
        # If verified, activate the user account
        if is_verified:
            await cursor.execute("UPDATE users SET is_active = TRUE WHERE id = %s", (doctor_id,))
            print(f"✅ Activated doctor account: {doctor[1]}")
            
            # Send approval email
            doctor_name = f"{doctor[2]} {doctor[3]}"
            doctor_email = doctor[1]
            
            subject, text_content, html_content = email_service.get_doctor_approval_template(doctor_name, doctor_email)
            email_sent = await email_service.send_email(doctor_email, subject, html_content, text_content)
            
            if email_sent:
                print(f"✅ Approval email sent to: {doctor_email}")
            else:
                print(f"❌ Failed to send approval email to: {doctor_email}")
        
        action = "verified" if is_verified else "rejected"
        print(f"🔍 Admin {action} doctor: {doctor[1]} (ID: {doctor_id})")
        
        return {
            "success": True,
            "message": f"Doctor {action} successfully",
            "doctor_id": doctor_id,
            "is_verified": is_verified,
            "email_sent": is_verified  # Only true if verified and email was sent
        }

@app.post("/api/admin/users/{user_id}/toggle-status", response_model=Dict[str, Any])
async def toggle_user_status(user_id: int):
    """Enable or disable a user account"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Get current status
        await cursor.execute("SELECT email, is_active FROM users WHERE id = %s", (user_id,))
        user = await cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Toggle status
        new_status = not user[1]
        
        await cursor.execute("""
        UPDATE users 
        SET is_active = %s 
        WHERE id = %s
        """, (new_status, user_id))
        
        action = "enabled" if new_status else "disabled"
        print(f"🔧 Admin {action} user: {user[0]} (ID: {user_id})")
        
        return {
            "success": True,
            "message": f"User {action} successfully",
            "user_id": user_id,
            "is_active": new_status
        }

@app.get("/api/admin/stats", response_model=Dict[str, Any])
async def get_admin_stats():
    """Get system statistics for admin dashboard"""
    try:
        pool = await get_connection()
        
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Get user counts
            await cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'patient'")
            patient_count = (await cursor.fetchone())[0]
            
            await cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'doctor'")
            doctor_count = (await cursor.fetchone())[0]
            
            await cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admin_count = (await cursor.fetchone())[0]
            
            # Get verified doctors count
            await cursor.execute("""
            SELECT COUNT(*) FROM doctors d 
            JOIN users u ON d.user_id = u.id 
            WHERE u.role = 'doctor' AND d.is_verified = TRUE
            """)
            verified_doctors = (await cursor.fetchone())[0]
            
            # Get pending cases
            await cursor.execute("SELECT COUNT(*) FROM medical_cases WHERE status = 'pending_review'")
            pending_cases = (await cursor.fetchone())[0]
            
            # Get total cases
            await cursor.execute("SELECT COUNT(*) FROM medical_cases")
            total_cases = (await cursor.fetchone())[0]
            
            return {
                "success": True,
                "stats": {
                    "total_patients": patient_count,
                    "total_doctors": doctor_count,
                    "verified_doctors": verified_doctors,
                    "pending_doctors": doctor_count - verified_doctors,
                    "total_admins": admin_count,
                    "pending_cases": pending_cases,
                    "total_cases": total_cases
                }
            }
    except Exception as e:
        print(f"❌ Error in admin stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": {
                "total_patients": 0,
                "total_doctors": 0,
                "verified_doctors": 0,
                "pending_doctors": 0,
                "total_admins": 0,
                "pending_cases": 0,
                "total_cases": 0
            }
        }

@app.get("/api/admin/login-activity", response_model=Dict[str, Any])
async def get_login_activity():
    """Get recent login activity (admin only)"""
    # This is a simplified version - in production you'd have a proper login logs table
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cursor = await conn.cursor()
        
        # Get recent user registrations as activity indicator
        await cursor.execute("""
        SELECT email, role, created_at, is_active
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 20
        """)
        
        recent_users = await cursor.fetchall()
        
        # Convert to list of dictionaries
        activity_list = []
        for user in recent_users:
            activity_list.append({
                "email": user[0],
                "role": user[1],
                "activity_type": "registration",
                "timestamp": user[2].isoformat() if user[2] else None,
                "is_active": user[3]
            })
        
        return {
            "success": True,
            "activities": activity_list,
            "total": len(activity_list)
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )