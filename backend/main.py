# backend/main.py - WORKING VERSION (FIXED)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import asyncpg
import uuid
from jose import JWTError, jwt
from passlib.context import CryptContext
# In main.py, make sure you're importing PostgreSQL version:
from database.database import get_db_connection, init_database  # PostgreSQL version
# NOT: from sqlite_database import ...  # Remove SQLite import if present
# Import database connection


# Initialize FastAPI
app = FastAPI(
    title="Medical Center API",
    description="Healthcare management system with PostgreSQL",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "medical-center-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic Models - REMOVED EmailStr
class UserLogin(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str

class UserRegister(BaseModel):
    email: str  # Changed from EmailStr to str
    password: str
    role: str
    first_name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class CaseCreate(BaseModel):
    title: str
    symptoms: str
    severity: str = "medium"

# Password functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Startup event - FIXED for newer FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Medical Center API...")
    try:
        await init_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database warning: {e}")
    
    yield  # App runs here

# Update FastAPI initialization
app = FastAPI(
    title="Medical Center API",
    description="Healthcare management system with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

# Routes
@app.get("/")
async def root():
    return {
        "message": "Medical Center API",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "status": "running"
    }

@app.get("/health")
async def health():
    try:
        conn = await get_db_connection()
        await conn.fetchval("SELECT 1")
        await conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """Login endpoint"""
    try:
        conn = await get_db_connection()
        
        # Find user (normalize email to lowercase)
        user = await conn.fetchrow("""
            SELECT id, email, password_hash, role, first_name, last_name 
            FROM users 
            WHERE LOWER(email) = LOWER($1) AND is_active = true
        """, user_data.email.strip())
        
        if not user:
            await conn.close()
            return {
                "success": False,
                "message": "Invalid credentials. Try: patient.demo@medical.com / patient123"
            }
        
        # For demo, accept any password (in production, use hashed passwords)
        # Simple password check - compare with stored password_hash
        if user_data.password != user["password_hash"]:
            await conn.close()
            return {
                "success": False,
                "message": f"Invalid password. Use: {user['password_hash']}"
            }
        
        # Update last login
        await conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1",
            user["id"]
        )
        
        await conn.close()
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user["id"])})
        
        user_dict = {
            "id": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "name": f"{user['first_name']} {user['last_name']}"
        }
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_dict,
            "message": "Login successful"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Login error: {str(e)}"
        }

@app.post("/api/auth/register")
async def register(user_data: UserRegister):
    """Register new user"""
    try:
        conn = await get_db_connection()
        
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE LOWER(email) = LOWER($1)",
            user_data.email.strip()
        )
        
        if existing:
            await conn.close()
            return {"success": False, "message": "Email already registered"}
        
        # Create user
        user_id = uuid.uuid4()
        password_hash = get_password_hash(user_data.password)
        
        await conn.execute("""
            INSERT INTO users (id, email, password_hash, role, first_name, last_name, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, true)
        """, user_id, user_data.email, password_hash, user_data.role, 
           user_data.first_name, user_data.last_name)
        
        await conn.close()
        
        # Create token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        user_dict = {
            "id": str(user_id),
            "email": user_data.email,
            "role": user_data.role,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "name": f"{user_data.first_name} {user_data.last_name}"
        }
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_dict,
            "message": "Registration successful"
        }
        
    except Exception as e:
        return {"success": False, "message": f"Registration error: {str(e)}"}

@app.get("/api/patient/cases")
async def get_patient_cases(patient_email: str = "patient.demo@medical.com"):
    """Get cases for a patient"""
    try:
        conn = await get_db_connection()
        
        # Get patient and their cases
        cases = await conn.fetch("""
            SELECT 
                c.id, c.title, c.symptoms, c.severity, c.status, c.created_at,
                u.first_name || ' ' || u.last_name as patient_name,
                d.first_name || ' ' || d.last_name as doctor_name
            FROM medical_cases c
            JOIN users u ON c.patient_id = u.id
            LEFT JOIN users d ON c.doctor_id = d.id
            WHERE u.email = $1
            ORDER BY c.created_at DESC
        """, patient_email)
        
        await conn.close()
        
        return {
            "cases": [
                {
                    "id": str(case["id"]),
                    "title": case["title"],
                    "symptoms": case["symptoms"],
                    "severity": case["severity"],
                    "status": case["status"],
                    "created_at": case["created_at"].isoformat(),
                    "patient_name": case["patient_name"],
                    "doctor_name": case["doctor_name"]
                }
                for case in cases
            ]
        }
        
    except Exception as e:
        return {"cases": [], "error": str(e)}

@app.get("/api/doctor/case-queue")
async def get_case_queue():
    """Get pending cases for doctors"""
    try:
        conn = await get_db_connection()
        
        cases = await conn.fetch("""
            SELECT 
                c.id, c.title, c.symptoms, c.severity, c.status, c.created_at,
                u.first_name || ' ' || u.last_name as patient_name
            FROM medical_cases c
            JOIN users u ON c.patient_id = u.id
            WHERE c.status = 'pending'
            ORDER BY 
                CASE c.severity 
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                c.created_at
        """)
        
        await conn.close()
        
        return {
            "cases": [
                {
                    "id": str(case["id"]),
                    "title": case["title"],
                    "symptoms": case["symptoms"],
                    "severity": case["severity"],
                    "status": case["status"],
                    "created_at": case["created_at"].isoformat(),
                    "patient_name": case["patient_name"]
                }
                for case in cases
            ]
        }
        
    except Exception as e:
        return {"cases": [], "error": str(e)}

@app.post("/api/doctor/cases/{case_id}/assign")
async def assign_case(case_id: str, doctor_email: str = "dr.smith@medical.com"):
    """Assign case to doctor"""
    try:
        conn = await get_db_connection()
        
        # Get doctor
        doctor = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND role = 'doctor'",
            doctor_email
        )
        
        if not doctor:
            await conn.close()
            return {"success": False, "message": "Doctor not found"}
        
        # Update case
        result = await conn.execute("""
            UPDATE medical_cases 
            SET doctor_id = $1, status = 'under_review'
            WHERE id = $2
        """, doctor["id"], uuid.UUID(case_id))
        
        await conn.close()
        
        if "UPDATE 1" in result:
            return {"success": True, "message": "Case assigned successfully"}
        else:
            return {"success": False, "message": "Case not found"}
            
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/dashboard/stats")
async def get_stats():
    """Get dashboard statistics"""
    try:
        conn = await get_db_connection()
        
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT c.id) as total_cases,
                COUNT(DISTINCT CASE WHEN c.status = 'pending' THEN c.id END) as pending_cases,
                COUNT(DISTINCT CASE WHEN u.role = 'doctor' THEN u.id END) as doctors_count
            FROM users u
            LEFT JOIN medical_cases c ON u.id = c.patient_id
            WHERE u.is_active = true
        """)
        
        await conn.close()
        
        return {
            "total_users": stats["total_users"] or 0,
            "total_cases": stats["total_cases"] or 0,
            "pending_cases": stats["pending_cases"] or 0,
            "doctors_count": stats["doctors_count"] or 0
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/patient/cases")
async def create_case(data: CaseCreate, patient_email: str = "patient.demo@medical.com"):
    """Create new case"""
    try:
        conn = await get_db_connection()
        
        # Get patient
        patient = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1 AND role = 'patient'",
            patient_email
        )
        
        if not patient:
            await conn.close()
            return {"success": False, "message": "Patient not found"}
        
        # Create case
        case_id = uuid.uuid4()
        await conn.execute("""
            INSERT INTO medical_cases (id, patient_id, title, symptoms, severity, status)
            VALUES ($1, $2, $3, $4, $5, 'pending')
        """, case_id, patient["id"], data.title, data.symptoms, data.severity)
        
        await conn.close()
        
        return {
            "success": True,
            "case": {
                "id": str(case_id),
                "title": data.title,
                "symptoms": data.symptoms,
                "severity": data.severity,
                "status": "pending"
            }
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🏥 Medical Center API with PostgreSQL")
    print("=" * 50)
    print("🌐 API URL: http://localhost:8000")
    print("📊 Database: PostgreSQL (medical_center)")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n👤 Demo Credentials:")
    print("  Patient: patient.demo@medical.com / patient123")
    print("  Doctor: dr.smith@medical.com / doctor123")
    print("  Admin: admin@medical.com / admin123")
    print("=" * 50)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)