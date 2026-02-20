#!/usr/bin/env python3
"""
Fix patient ID mismatch in database
Update all cases from patient_id 2 to patient_id 3
"""

import os
import sys
import aiomysql
import asyncio

# Database configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "medical_center")

async def fix_patient_ids():
    """Update all cases from patient_id 2 to patient_id 3"""
    
    try:
        # Connect to database
        conn = await aiomysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            autocommit=True
        )
        
        cursor = await conn.cursor()
        
        print("🔧 Fixing patient ID mismatch...")
        
        # Check current cases
        await cursor.execute("SELECT id, patient_id FROM medical_cases ORDER BY id")
        cases = await cursor.fetchall()
        print(f"📊 Found {len(cases)} cases:")
        for case_id, patient_id in cases:
            print(f"  - Case {case_id}: Patient {patient_id}")
        
        # Update cases from patient_id 2 to patient_id 3
        await cursor.execute("UPDATE medical_cases SET patient_id = 3 WHERE patient_id = 2")
        affected_rows = cursor.rowcount
        
        print(f"✅ Updated {affected_rows} cases from patient_id 2 to patient_id 3")
        
        # Verify the update
        await cursor.execute("SELECT id, patient_id FROM medical_cases ORDER BY id")
        updated_cases = await cursor.fetchall()
        print("📊 Updated cases:")
        for case_id, patient_id in updated_cases:
            print(f"  - Case {case_id}: Patient {patient_id}")
        
        await cursor.close()
        conn.close()
        
        print("🎯 Patient ID fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing patient IDs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(fix_patient_ids())
