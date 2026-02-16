#!/usr/bin/env python3
"""
Script to create additional admin accounts for Medical Center Pro
"""

import asyncio
import aiomysql
import hashlib
from datetime import datetime

async def create_admin_account():
    """Create a new admin account"""
    
    # Database configuration
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DATABASE = "medical_center"
    
    # Admin account details
    ADMIN_EMAIL = "new.admin@medical.com"
    ADMIN_PASSWORD = "NewAdmin@123"
    ADMIN_FIRST_NAME = "New"
    ADMIN_LAST_NAME = "Admin"
    
    pool = await aiomysql.create_pool(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DATABASE,
        autocommit=True
    )
    
    try:
        async with pool.acquire() as conn:
            cursor = await conn.cursor()
            
            # Check if admin already exists
            await cursor.execute("SELECT id FROM users WHERE email = %s", (ADMIN_EMAIL,))
            existing_admin = await cursor.fetchone()
            
            if existing_admin:
                print(f"❌ Admin account {ADMIN_EMAIL} already exists!")
                return
            
            # Hash password
            password_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
            
            # Insert new admin
            await cursor.execute("""
            INSERT INTO users (email, password_hash, role, first_name, last_name, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
            """, (
                ADMIN_EMAIL,
                password_hash,
                "admin",
                ADMIN_FIRST_NAME,
                ADMIN_LAST_NAME
            ))
            
            print(f"✅ Admin account created successfully!")
            print(f"📧 Email: {ADMIN_EMAIL}")
            print(f"🔐 Password: {ADMIN_PASSWORD}")
            print(f"👤 Role: admin")
            print(f"🏠 Dashboard: /admin/dashboard")
            
    except Exception as e:
        print(f"❌ Error creating admin account: {e}")
    finally:
        pool.close()

if __name__ == "__main__":
    print("🔧 Creating additional admin account...")
    asyncio.run(create_admin_account())
