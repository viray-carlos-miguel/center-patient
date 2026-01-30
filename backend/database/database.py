# backend/database/database.py
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# Try different connection strings
# backend/database/database.py
DATABASE_URL = "postgresql://postgres:carlosviray91@localhost:5432/medical_center"

# Common password options to try
PASSWORD_OPTIONS = ["postgres", "admin", "password", ""]

async def get_db_connection():
    """Get a database connection - try different passwords"""
    for password in PASSWORD_OPTIONS:
        try:
            # Try with current password option
            test_url = f"postgresql://postgres:{password}@localhost:5432/medical_center"
            conn = await asyncpg.connect(test_url)
            print(f"✅ Connected to PostgreSQL with password: {'[empty]' if password == '' else password}")
            return conn
        except Exception:
            continue
    
    # If none work, try without password
    try:
        conn = await asyncpg.connect("postgresql://postgres@localhost:5432/medical_center")
        print("✅ Connected to PostgreSQL without password")
        return conn
    except Exception as e:
        print(f"❌ All connection attempts failed. Last error: {e}")
        print("\n💡 Try setting PostgreSQL password:")
        print("1. Open pgAdmin or psql")
        print("2. Run: ALTER USER postgres WITH PASSWORD 'postgres';")
        print("3. Or create new database: CREATE DATABASE medical_center;")
        raise

async def init_database():
    """Initialize database with tables and demo data"""
    conn = None
    try:
        print("🔧 Initializing database...")
        conn = await get_db_connection()
        
        # Check if database exists, if not create it
        try:
            await conn.fetchval("SELECT 1")
        except:
            print("Database doesn't exist. Creating...")
            # Close connection to create database
            await conn.close()
            
            # Connect to default postgres database to create our database
            admin_conn = await asyncpg.connect("postgresql://postgres@localhost:5432/postgres")
            await admin_conn.execute("CREATE DATABASE medical_center;")
            await admin_conn.close()
            
            # Reconnect to new database
            conn = await get_db_connection()
        
        # Create users table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('patient', 'doctor', 'admin')),
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """)
        
        # Create medical_cases table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS medical_cases (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            patient_id UUID REFERENCES users(id),
            doctor_id UUID REFERENCES users(id),
            title VARCHAR(200) NOT NULL,
            symptoms TEXT NOT NULL,
            severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'under_review', 'diagnosed', 'treated', 'closed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Check if we have demo data
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        if user_count == 0:
            print("🌱 Adding demo data...")
            
            # Insert demo users
            demo_users = [
                ("admin@medical.com", "admin123", "admin", "System", "Admin"),
                ("dr.smith@medical.com", "doctor123", "doctor", "John", "Smith"),
                ("dr.jones@medical.com", "neurology123", "doctor", "Sarah", "Jones"),
                ("patient.demo@medical.com", "patient123", "patient", "Demo", "Patient"),
                ("john.doe@example.com", "password123", "patient", "John", "Doe")
            ]
            
            for email, password, role, first_name, last_name in demo_users:
                await conn.execute("""
                INSERT INTO users (email, password_hash, role, first_name, last_name, is_active)
                VALUES ($1, $2, $3, $4, $5, true)
                ON CONFLICT (email) DO NOTHING
                """, email, password, role, first_name, last_name)
            
            # Insert demo cases
            await conn.execute("""
            INSERT INTO medical_cases (patient_id, title, symptoms, severity, status)
            SELECT 
                u.id,
                'Persistent Headache with Fever',
                'Headache for 3 days, fever 38.5°C, fatigue, mild dizziness',
                'medium',
                'pending'
            FROM users u WHERE u.email = 'patient.demo@medical.com'
            ON CONFLICT DO NOTHING
            """)
            
            await conn.execute("""
            INSERT INTO medical_cases (patient_id, title, symptoms, severity, status)
            SELECT 
                u.id,
                'Seasonal Allergy Symptoms',
                'Sneezing, runny nose, itchy eyes, congestion for 2 weeks',
                'low',
                'pending'
            FROM users u WHERE u.email = 'john.doe@example.com'
            ON CONFLICT DO NOTHING
            """)
            
            print("✅ Demo data added!")
        
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("\n💡 Try these fixes:")
        print("1. Make sure PostgreSQL is running: net start postgresql-x64-16")
        print("2. Check password in pg_hba.conf file")
        print("3. Try: ALTER USER postgres WITH PASSWORD 'postgres';")
        raise
    finally:
        if conn:
            await conn.close()