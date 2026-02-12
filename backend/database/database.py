# backend/database/database.py
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL XAMPP Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "medical_center")

# Common XAMPP MySQL passwords to try
PASSWORD_OPTIONS = ["", "root", "admin", "password"]

async def get_db_connection():
    """Get a MySQL database connection - try different passwords"""
    for password in PASSWORD_OPTIONS:
        try:
            conn = await aiomysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=password,
                db=MYSQL_DATABASE,
                autocommit=True
            )
            print(f"✅ Connected to MySQL XAMPP with password: {'[empty]' if password == '' else password}")
            return conn
        except Exception as e:
            print(f"❌ Failed with password '{'empty' if password == '' else password}': {e}")
            continue
    
    # If none work, try creating database first
    print("🔄 Attempting to create database...")
    try:
        conn = await aiomysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password="",
            autocommit=True
        )
        cursor = await conn.cursor()
        await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        await cursor.execute(f"USE {MYSQL_DATABASE}")
        print(f"✅ Created and connected to MySQL database: {MYSQL_DATABASE}")
        return conn
    except Exception as e:
        print(f"❌ All connection attempts failed. Last error: {e}")
        raise Exception(f"Cannot connect to MySQL XAMPP. Please check: 1) XAMPP is running, 2) MySQL service is started, 3) Credentials are correct. Error: {e}")

async def init_database():
    """Initialize MySQL database with tables and demo data"""
    conn = None
    try:
        print("🔧 Initializing MySQL XAMPP database...")
        
        # First connect without specifying database to create it
        try:
            conn = await aiomysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password="",
                autocommit=True
            )
            cursor = await conn.cursor()
            
            # Create database if it doesn't exist
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
            print(f"✅ Database '{MYSQL_DATABASE}' created/verified")
            
            # Switch to our database
            await cursor.execute(f"USE {MYSQL_DATABASE}")
            
            # Create tables
            print("📋 Creating tables...")
            
            # Users table
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
                last_login TIMESTAMP NULL
            )
            """)
            
            # Medical cases table
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_cases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NULL,
                title VARCHAR(200) NOT NULL,
                symptoms TEXT NOT NULL,
                severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
                status ENUM('pending', 'under_review', 'diagnosed', 'treated', 'closed') DEFAULT 'pending',
                ai_assessment JSON NULL,
                doctor_diagnosis TEXT NULL,
                doctor_notes TEXT NULL,
                prescription JSON NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP NULL,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """)
            
            # Prescriptions table
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                case_id INT NOT NULL,
                doctor_id INT NOT NULL,
                patient_id INT NOT NULL,
                medication_name VARCHAR(200) NOT NULL,
                dosage VARCHAR(100) NOT NULL,
                frequency VARCHAR(200) NOT NULL,
                duration_days INT NOT NULL,
                instructions TEXT NOT NULL,
                doctor_signature VARCHAR(255) NULL,
                is_educational BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES medical_cases(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            # Check if we have demo data
            await cursor.execute("SELECT COUNT(*) FROM users")
            user_count = (await cursor.fetchone())[0]
            
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
                    await cursor.execute("""
                    INSERT IGNORE INTO users (email, password_hash, role, first_name, last_name, is_active)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                    """, email, password, role, first_name, last_name)
                
                # Get user IDs for demo cases
                await cursor.execute("SELECT id FROM users WHERE email = %s", ("patient.demo@medical.com",))
                patient_demo_id = (await cursor.fetchone())[0]
                
                await cursor.execute("SELECT id FROM users WHERE email = %s", ("john.doe@example.com",))
                patient_john_id = (await cursor.fetchone())[0]
                
                # Insert demo cases
                await cursor.execute("""
                INSERT IGNORE INTO medical_cases 
                (patient_id, title, symptoms, severity, status, ai_assessment)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    patient_demo_id,
                    'Persistent Headache with Fever',
                    'Headache for 3 days, fever 38.5°C, fatigue, mild dizziness',
                    'medium',
                    'pending',
                    '{"possible_conditions": ["Tension Headache", "Viral Infection"], "confidence_score": 0.75, "recommended_tests": ["Physical Examination", "Temperature Check"], "urgency_level": "medium", "educational_note": "Educational AI assessment based on symptoms"}'
                ))
                
                await cursor.execute("""
                INSERT IGNORE INTO medical_cases 
                (patient_id, title, symptoms, severity, status, ai_assessment)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    patient_john_id,
                    'Seasonal Allergy Symptoms',
                    'Sneezing, runny nose, itchy eyes, congestion for 2 weeks',
                    'low',
                    'pending',
                    '{"possible_conditions": ["Allergic Rhinitis", "Seasonal Allergies"], "confidence_score": 0.85, "recommended_tests": ["Allergy Test", "Physical Examination"], "urgency_level": "low", "educational_note": "Educational AI assessment based on symptoms"}'
                ))
                
                print("✅ Demo data added!")
            
            # Show database status
            await cursor.execute("SELECT COUNT(*) FROM users")
            users_count = (await cursor.fetchone())[0]
            await cursor.execute("SELECT COUNT(*) FROM medical_cases")
            cases_count = (await cursor.fetchone())[0]
            
            print(f"✅ Database initialized successfully!")
            print(f"📊 Database stats: {users_count} users, {cases_count} cases")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n💡 Try these fixes:")
        print("1. Make sure XAMPP is installed and running")
        print("2. Start MySQL service in XAMPP Control Panel")
        print("3. Check if MySQL is running on port 3306")
        print("4. Verify MySQL credentials (usually root with no password)")
        print("5. Try accessing phpMyAdmin to verify MySQL is working")
        raise
    finally:
        if conn:
            await conn.close()