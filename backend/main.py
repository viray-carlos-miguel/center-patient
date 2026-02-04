# backend/main.py
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uvicorn
import asyncpg
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
import hashlib

load_dotenv()

# Import AI Predictor
try:
    from ai_system.core.predictor import ClinicalPredictor
    predictor = ClinicalPredictor()
    AI_ENABLED = True
except ImportError:
    print("⚠️ AI module not found, using fallback")
    AI_ENABLED = False
    class ClinicalPredictor:
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
                "confidence_score": 0.65
            }
    predictor = ClinicalPredictor()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medical_center")

# Pydantic Models
class UserBase(BaseModel):
    email: str
    role: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class PatientRegistration(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    date_of_birth: str
    phone: Optional[str] = None
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

# CORS Configuration - UPDATED with comprehensive settings
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
        # First, try to drop tables if they exist with wrong structure
        try:
            await conn.execute("DROP TABLE IF EXISTS medical_cases CASCADE")
            await conn.execute("DROP TABLE IF EXISTS patients CASCADE")
            await conn.execute("DROP TABLE IF EXISTS users CASCADE")
        except:
            pass  # Ignore errors if tables don't exist
        
        # Create users table with SERIAL (integer) id
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
        
        # Create medical_cases table first (simpler, without patients table for now)
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
        
        # Check if demo data exists
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        if user_count == 0:
            print("🌱 Adding demo users to PostgreSQL...")
            
            # Create demo users with hashed passwords
            demo_users = [
                ("patient.demo@medical.com", "patient123", "patient", "Demo", "Patient"),
                ("dr.smith@medical.com", "doctor123", "doctor", "John", "Smith"),
                ("dr.jones@medical.com", "neurology123", "doctor", "Sarah", "Jones"),
                ("admin@medical.com", "admin123", "admin", "System", "Admin"),
                ("john.doe@example.com", "password123", "patient", "John", "Doe")
            ]
            
            for email, password, role, first_name, last_name in demo_users:
                # Simple password hash for demo
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                await conn.execute("""
                INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
                VALUES ($1, $2, $3, $4, $5, true)
                ON CONFLICT (email) DO NOTHING
                """, email, password_hash, role, first_name, last_name)
            
            print("✅ Demo users added")
            
            # Create demo cases
            patient = await conn.fetchrow("SELECT id FROM users WHERE email = 'patient.demo@medical.com'")
            if patient:
                demo_symptoms = {
                    "description": "Headache for 3 days, fever 38.5°C, fatigue, mild dizziness",
                    "duration_hours": 72,
                    "severity": 7,
                    "temperature": 38.5,
                    "has_fever": True,
                    "has_headache": True,
                    "has_fatigue": True,
                    "additional_notes": "Symptoms started suddenly"
                }
                
                demo_ai = {
                    "possible_conditions": ["Migraine", "Viral Infection", "Tension Headache"],
                    "confidence_score": 0.75,
                    "recommended_tests": ["Physical Exam", "Temperature Monitoring"],
                    "urgency_level": "medium",
                    "educational_note": "AI assessment for educational purposes only"
                }
                
                await conn.execute("""
                INSERT INTO medical_cases (patient_id, symptoms, ai_assessment, status)
                VALUES ($1, $2::jsonb, $3::jsonb, 'pending_review')
                """, patient['id'], json.dumps(demo_symptoms), json.dumps(demo_ai))
                
                print("✅ Demo case added")
        
        # Now create patients table if it doesn't exist (without foreign key for now)
        try:
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                date_of_birth DATE,
                phone VARCHAR(50),
                emergency_contact VARCHAR(100),
                blood_type VARCHAR(10),
                allergies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Add foreign key constraint separately
            try:
                await conn.execute("""
                ALTER TABLE patients 
                ADD CONSTRAINT fk_patient_user 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                """)
            except:
                print("⚠️ Could not add foreign key constraint - continuing anyway")
                
        except Exception as e:
            print(f"⚠️ Patients table creation warning: {e}")
        
        await conn.close()
        print("🎯 PostgreSQL database ready!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Try a simpler approach
        try:
            print("🔄 Trying simpler database setup...")
            conn = await asyncpg.connect(DATABASE_URL)
            
            # Just create basic tables without foreign keys
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_cases (
                id SERIAL PRIMARY KEY,
                patient_id INTEGER,
                symptoms JSONB NOT NULL,
                ai_assessment JSONB,
                status VARCHAR(50) DEFAULT 'pending_review',
                doctor_diagnosis TEXT,
                doctor_notes TEXT,
                prescription JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            await conn.close()
            print("✅ Created basic tables without foreign keys")
        except Exception as e2:
            print(f"❌ Even simple setup failed: {e2}")
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
async def register_patient(registration: PatientRegistration):
    """Register a new patient account"""
    if not registration.agree_to_terms or not registration.acknowledge_educational:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must agree to terms and acknowledge educational purpose"
        )
    
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
        password_hash = hashlib.sha256(registration.password.encode()).hexdigest()
        
        # Insert new patient
        try:
            result = await conn.fetchrow("""
            INSERT INTO users (
                email, password_hash, role, first_name, last_name, 
                is_active, created_at
            ) VALUES ($1, $2, 'patient', $3, $4, true, CURRENT_TIMESTAMP)
            RETURNING id, email, role, first_name, last_name, created_at
            """, 
            registration.email, password_hash, 
            registration.first_name, registration.last_name)
            
            # Try to create patient profile (optional)
            try:
                await conn.execute("""
                INSERT INTO patients (user_id, date_of_birth, phone)
                VALUES ($1, $2, $3)
                """, result['id'], registration.date_of_birth, registration.phone)
            except Exception as e:
                print(f"Note: Could not create patient profile: {e}")
                # Continue without patient profile - it's optional
        
        except asyncpg.exceptions.UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            print(f"Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again."
            )
        
        # Prepare response
        user_response = {
            "id": result['id'],
            "email": result['email'],
            "role": result['role'],
            "first_name": result['first_name'],
            "last_name": result['last_name'],
            "full_name": f"{result['first_name']} {result['last_name']}",
            "is_active": True,
            "created_at": result['created_at'].isoformat() if result['created_at'] else None
        }
        
        return {
            "success": True,
            "user": user_response,
            "message": "Patient account created successfully",
            "token": f"patient_token_{result['id']}_{datetime.now().timestamp()}",
            "educational_note": "Educational account created - not for real medical use"
        }

@app.post("/api/auth/login", response_model=Dict[str, Any])
async def login(login_data: UserLogin):
    """Authenticate user with PostgreSQL"""
    print("=" * 50)
    print(f"🔐 LOGIN ATTEMPT DEBUG")
    print(f"📧 Email: '{login_data.email}'")
    print(f"🔑 Password: '{login_data.password}'")
    
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        # Find user
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1 AND is_active = true",
            login_data.email.strip()
        )
        
        if not user:
            print(f"❌ USER NOT FOUND: {login_data.email}")
            # Show all users for debugging
            all_users = await conn.fetch("SELECT email, password_hash FROM users")
            print(f"📋 Available users in database:")
            for u in all_users:
                print(f"  - {u['email']}: {u['password_hash'][:20]}...")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"✅ User found in DB: {user['email']}")
        print(f"📦 Stored password hash: {user['password_hash']}")
        print(f"📦 Stored hash length: {len(user['password_hash'])}")
        
        # Calculate hash of input password
        input_hash = hashlib.sha256(login_data.password.strip().encode()).hexdigest()
        print(f"🔢 Input password hash: {input_hash}")
        print(f"🔢 Input hash length: {len(input_hash)}")
        print(f"🔍 Hash match: {input_hash == user['password_hash']}")
        
        if input_hash != user['password_hash']:
            print(f"❌ PASSWORD MISMATCH!")
            print(f"   Expected: {user['password_hash']}")
            print(f"   Got:      {input_hash}")
            
            # Also show what password would produce the stored hash
            # Try common passwords
            common_passwords = ["patient123", "doctor123", "neurology123", "admin123", "password123"]
            for pwd in common_passwords:
                test_hash = hashlib.sha256(pwd.encode()).hexdigest()
                if test_hash == user['password_hash']:
                    print(f"💡 Hint: Stored hash matches password: '{pwd}'")
                    break
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        print(f"🎉 LOGIN SUCCESSFUL for {user['email']}!")
        print("=" * 50)
        
        # Prepare user response
        user_response = {
            "id": user['id'],
            "email": user['email'],
            "role": user['role'],
            "first_name": user['first_name'],
            "last_name": user['last_name'],
            "full_name": f"{user['first_name']} {user['last_name']}",
            "is_active": user['is_active'],
            "created_at": user['created_at'].isoformat() if user['created_at'] else None
        }
        
        return {
            "success": True,
            "user": user_response,
            "message": "Login successful",
            "token": f"postgres-token-{user['id']}-{datetime.now().timestamp()}"
        }

@app.post("/api/cases/submit", response_model=Dict[str, Any])
async def submit_case(
    symptoms: SymptomSubmission,
    request: Request
):
    """Submit new medical case with AI assessment"""
    # Get patient ID from auth (simplified for demo)
    patient_id = 1  # Default for demo
    
    pool = await get_connection()
    
    # Convert symptoms to dict
    symptoms_dict = symptoms.dict()
    
    # Generate AI assessment
    try:
        ai_result = predictor.analyze_symptoms(
            symptoms=symptoms_dict,
            patient_info={"age": 30, "has_chronic_conditions": False}
        )
        
        ai_assessment = {
            "possible_conditions": [p["disease"] for p in ai_result.get("disease_predictions", [])[:3]],
            "confidence_score": ai_result.get("confidence_score", 0.5),
            "recommended_tests": ai_result.get("recommendations", {}).get("medical_tests", []),
            "urgency_level": ai_result.get("risk_assessment", {}).get("urgency_level", "low"),
            "educational_note": "AI assessment for educational purposes only"
        }
    except Exception as e:
        print(f"AI assessment error: {e}")
        ai_assessment = {
            "possible_conditions": ["General Assessment Needed"],
            "confidence_score": 0.5,
            "recommended_tests": ["Physical Examination"],
            "urgency_level": "low",
            "educational_note": "Fallback assessment - AI unavailable"
        }
    
    async with pool.acquire() as conn:
        # Insert case
        result = await conn.fetchrow("""
        INSERT INTO medical_cases (patient_id, symptoms, ai_assessment, status)
        VALUES ($1, $2::jsonb, $3::jsonb, 'pending_review')
        RETURNING id, created_at
        """, patient_id, json.dumps(symptoms_dict), json.dumps(ai_assessment))
        
        # Get patient name
        patient = await conn.fetchrow("SELECT first_name, last_name FROM users WHERE id = $1", patient_id)
        patient_name = f"{patient['first_name']} {patient['last_name']}" if patient else "Unknown Patient"
        
        return {
            "success": True,
            "case_id": result['id'],
            "message": "Case submitted successfully",
            "ai_assessment": ai_assessment,
            "patient_name": patient_name
        }

@app.get("/api/patient/cases", response_model=Dict[str, Any])
async def get_patient_cases():
    """Get all cases for current patient"""
    patient_id = 1  # Default for demo
    
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cases = await conn.fetch("""
        SELECT 
            c.*,
            u.first_name,
            u.last_name
        FROM medical_cases c
        LEFT JOIN users u ON c.patient_id = u.id
        WHERE c.patient_id = $1
        ORDER BY c.created_at DESC
        """, patient_id)
        
        formatted_cases = []
        for case in cases:
            # Parse JSON fields
            symptoms = json.loads(case['symptoms']) if case['symptoms'] else {}
            ai_assessment = json.loads(case['ai_assessment']) if case['ai_assessment'] else {}
            prescription = json.loads(case['prescription']) if case['prescription'] else None
            
            formatted_cases.append({
                "id": case['id'],
                "patient_id": case['patient_id'],
                "patient_name": f"{case['first_name']} {case['last_name']}" if case['first_name'] else "Unknown",
                "symptoms": symptoms,
                "ai_assessment": ai_assessment,
                "status": case['status'],
                "doctor_diagnosis": case['doctor_diagnosis'],
                "doctor_notes": case['doctor_notes'],
                "prescription": prescription,
                "created_at": case['created_at'].isoformat() if case['created_at'] else None,
                "reviewed_at": case['reviewed_at'].isoformat() if case['reviewed_at'] else None
            })
        
        return {
            "success": True,
            "cases": formatted_cases,
            "total": len(formatted_cases),
            "notice": "Educational data from PostgreSQL"
        }

@app.get("/api/doctor/cases", response_model=Dict[str, Any])
async def get_doctor_cases():
    """Get all cases for doctor review"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        cases = await conn.fetch("""
        SELECT 
            c.*,
            u.first_name as patient_first_name,
            u.last_name as patient_last_name
        FROM medical_cases c
        LEFT JOIN users u ON c.patient_id = u.id
        WHERE c.status IN ('pending_review', 'in_review')
        ORDER BY 
            CASE 
                WHEN c.status = 'pending_review' THEN 1
                WHEN c.status = 'in_review' THEN 2
                ELSE 3
            END,
            c.created_at DESC
        """)
        
        formatted_cases = []
        for case in cases:
            # Parse JSON fields
            symptoms = json.loads(case['symptoms']) if case['symptoms'] else {}
            ai_assessment = json.loads(case['ai_assessment']) if case['ai_assessment'] else {}
            prescription = json.loads(case['prescription']) if case['prescription'] else None
            
            formatted_cases.append({
                "id": case['id'],
                "patient_id": case['patient_id'],
                "patient_name": f"{case['patient_first_name']} {case['patient_last_name']}" if case['patient_first_name'] else "Unknown Patient",
                "symptoms": symptoms,
                "ai_assessment": ai_assessment,
                "status": case['status'],
                "doctor_diagnosis": case['doctor_diagnosis'],
                "doctor_notes": case['doctor_notes'],
                "prescription": prescription,
                "created_at": case['created_at'].isoformat() if case['created_at'] else None,
                "reviewed_at": case['reviewed_at'].isoformat() if case['reviewed_at'] else None
            })
        
        return {
            "success": True,
            "cases": formatted_cases,
            "total": len(formatted_cases),
            "reminder": "PostgreSQL database - Educational review only"
        }

@app.post("/api/cases/{case_id}/review", response_model=Dict[str, Any])
async def review_case(case_id: int, review: CaseReview):
    """Doctor reviews and diagnoses a case"""
    doctor_id = 2  # Default doctor for demo
    
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        # Update case with review
        prescription_json = json.dumps(review.prescription) if review.prescription else None
        
        await conn.execute("""
        UPDATE medical_cases 
        SET 
            doctor_id = $1,
            doctor_diagnosis = $2,
            doctor_notes = $3,
            prescription = $4::jsonb,
            status = 'completed',
            reviewed_at = CURRENT_TIMESTAMP,
            follow_up_required = $5,
            follow_up_days = $6,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $7
        """, 
        doctor_id, 
        review.doctor_diagnosis,
        review.doctor_notes,
        prescription_json,
        review.follow_up_required,
        review.follow_up_days,
        case_id)
        
        return {
            "success": True,
            "message": "Case reviewed successfully",
            "case_id": case_id,
            "educational_note": "Review saved to PostgreSQL for educational purposes"
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        pool = await get_connection()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "ai_enabled": AI_ENABLED,
        "version": "2.0.0"
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    pool = await get_connection()
    
    async with pool.acquire() as conn:
        total_cases = await conn.fetchval("SELECT COUNT(*) FROM medical_cases")
        pending_cases = await conn.fetchval("SELECT COUNT(*) FROM medical_cases WHERE status = 'pending_review'")
        completed_cases = await conn.fetchval("SELECT COUNT(*) FROM medical_cases WHERE status = 'completed'")
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        
        return {
            "total_cases": total_cases,
            "pending_review": pending_cases,
            "completed": completed_cases,
            "total_users": total_users,
            "database": "PostgreSQL",
            "timestamp": datetime.now().isoformat()
        }

# Add OPTIONS handler for preflight requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    response = JSONResponse(content={"message": "CORS preflight"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Add middleware to handle CORS headers
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )   