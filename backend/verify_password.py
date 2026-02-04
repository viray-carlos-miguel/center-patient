# backend/set_all_passwords.py
import asyncpg
import asyncio
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medical_center")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

async def set_all_passwords():
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Set all passwords to be EASY TO REMEMBER
        # You can change these to whatever you want
        user_passwords = [
            ('patient.demo@medical.com', 'patient123'),
            ('john.doe@example.com', 'patient123'),  # Same as patient for simplicity
            ('dr.smith@medical.com', 'doctor123'),
            ('dr.jones@medical.com', 'doctor123'),   # Same as other doctor for simplicity
            ('admin@medical.com', 'admin123')
        ]
        
        print("🔐 Setting passwords (use these for login):")
        for email, password in user_passwords:
            password_hash = hash_password(password)
            await conn.execute("""
            UPDATE users 
            SET password_hash = $1
            WHERE email = $2
            """, password_hash, email)
            
            print(f"  ✅ {email}: {password}")
        
        # Verify
        print("\n📋 Verification:")
        users = await conn.fetch("SELECT email, password_hash FROM users ORDER BY id")
        
        for user in users:
            # Show first 20 chars of hash for verification
            print(f"  {user['email']}: {user['password_hash'][:20]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(set_all_passwords())