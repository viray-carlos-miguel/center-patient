import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/medical_center"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Insert initial data
        await seed_initial_data()

async def seed_initial_data():
    from sqlalchemy import text
    
    async with AsyncSessionLocal() as session:
        # Check if we already have demo data
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        
        if count == 0:
            print("🌱 Seeding initial data...")
            
            # Create demo users with hashed passwords
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            demo_users = [
                {
                    "email": "admin@medical.com",
                    "password": pwd_context.hash("Admin@123"),
                    "role": "admin",
                    "first_name": "System",
                    "last_name": "Admin"
                },
                {
                    "email": "dr.smith@medical.com",
                    "password": pwd_context.hash("Doctor@2024"),
                    "role": "doctor",
                    "first_name": "John",
                    "last_name": "Smith",
                    "medical_license": "MD-123456",
                    "specialization": "Cardiology"
                },
                {
                    "email": "dr.jones@medical.com",
                    "password": pwd_context.hash("Neurology@2024"),
                    "role": "doctor",
                    "first_name": "Sarah",
                    "last_name": "Jones",
                    "medical_license": "MD-789012",
                    "specialization": "Neurology"
                },
                {
                    "email": "patient.demo@medical.com",
                    "password": pwd_context.hash("Patient@123"),
                    "role": "patient",
                    "first_name": "Demo",
                    "last_name": "Patient",
                    "blood_type": "O+",
                    "allergies": "Penicillin, Peanuts"
                },
                {
                    "email": "john.doe@example.com",
                    "password": pwd_context.hash("Password123"),
                    "role": "patient",
                    "first_name": "John",
                    "last_name": "Doe",
                    "blood_type": "A-"
                }
            ]
            
            for user_data in demo_users:
                # Insert into users table
                role = user_data.pop("role")
                medical_license = user_data.pop("medical_license", None)
                specialization = user_data.pop("specialization", None)
                blood_type = user_data.pop("blood_type", None)
                allergies = user_data.pop("allergies", None)
                
                user_result = await session.execute(
                    text("""
                    INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
                    VALUES (:email, :password, :role, :first_name, :last_name, true)
                    RETURNING id
                    """),
                    {
                        "email": user_data["email"],
                        "password": user_data["password"],
                        "role": role,
                        "first_name": user_data["first_name"],
                        "last_name": user_data["last_name"]
                    }
                )
                user_id = user_result.scalar()
                
                # Insert role-specific data
                if role == "doctor" and medical_license:
                    await session.execute(
                        text("""
                        INSERT INTO doctors (user_id, medical_license, specialization, is_verified)
                        VALUES (:user_id, :license, :specialization, true)
                        """),
                        {
                            "user_id": user_id,
                            "license": medical_license,
                            "specialization": specialization
                        }
                    )
                elif role == "patient":
                    await session.execute(
                        text("""
                        INSERT INTO patients (user_id, blood_type, allergies)
                        VALUES (:user_id, :blood_type, :allergies)
                        """),
                        {
                            "user_id": user_id,
                            "blood_type": blood_type,
                            "allergies": allergies
                        }
                    )
            
            # Create some demo medical cases
            await session.execute(
                text("""
                INSERT INTO medical_cases 
                (patient_id, doctor_id, title, symptoms, severity, status, priority)
                VALUES 
                ((SELECT id FROM users WHERE email = 'patient.demo@medical.com'),
                 (SELECT id FROM users WHERE email = 'dr.smith@medical.com'),
                 'Persistent Headache with Fever',
                 'Headache lasting 3 days, fever of 38.5°C, fatigue, mild photophobia',
                 'medium', 'under_review', 3),
                 
                ((SELECT id FROM users WHERE email = 'john.doe@example.com'),
                 NULL,
                 'Seasonal Allergy Symptoms',
                 'Sneezing, runny nose, itchy eyes, nasal congestion for 2 weeks',
                 'low', 'pending', 7),
                 
                ((SELECT id FROM users WHERE email = 'patient.demo@medical.com'),
                 NULL,
                 'Lower Back Pain',
                 'Acute lower back pain after lifting heavy objects, difficulty bending',
                 'high', 'pending', 2)
                """)
            )
            
            await session.commit()
            print("✅ Initial data seeded successfully!")