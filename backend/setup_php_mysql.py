#!/usr/bin/env python3
"""
Medical Center PHP MySQL Database Setup
For PHP/MySQL hosting environments
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import init_database, get_db_connection

async def test_php_mysql_connection():
    """Test PHP MySQL connection"""
    print("🔍 Testing PHP MySQL connection...")
    print("📍 Connection details:")
    print(f"   Host: localhost")
    print(f"   Port: 3306")
    print(f"   Database: medical_center")
    print(f"   User: root")
    print(f"   Password: ")
    
    try:
        conn = await get_db_connection()
        print("✅ PHP MySQL connection successful!")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ PHP MySQL connection failed: {e}")
        return False

async def setup_php_mysql_database():
    """Setup PHP MySQL database"""
    print("=" * 60)
    print("🏥 Medical Center Pro - PHP MySQL Setup")
    print("🗄️ PHP/MySQL Database Configuration")
    print("=" * 60)
    
    print("\n📋 Checking PHP MySQL connection...")
    
    # Test connection
    if not await test_php_mysql_connection():
        print("\n❌ Cannot connect to PHP MySQL!")
        print("\n💡 Please check your PHP MySQL setup:")
        print("1. MySQL server is running")
        print("2. Database 'medical_center' exists")
        print("3. User 'root' has permissions")
        print("4. MySQL port 3306 is accessible")
        print("5. Try your hosting control panel (cPanel, Plesk, etc.)")
        return False
    
    print("\n🔧 Initializing PHP MySQL database...")
    try:
        await init_database()
        print("\n🎉 PHP MySQL database setup completed!")
        return True
    except Exception as e:
        print(f"\n❌ Database setup failed: {e}")
        return False

async def show_database_status():
    """Show database status"""
    print("\n📊 Database Status:")
    print("-" * 40)
    
    try:
        conn = await get_db_connection()
        cursor = await conn.cursor()
        
        # Show tables
        await cursor.execute("SHOW TABLES")
        tables = await cursor.fetchall()
        print(f"📋 Tables: {len(tables)}")
        for table in tables:
            print(f"   ✓ {table[0]}")
        
        # Show records
        await cursor.execute("SELECT COUNT(*) FROM users")
        users = (await cursor.fetchone())[0]
        await cursor.execute("SELECT COUNT(*) FROM medical_cases")
        cases = (await cursor.fetchone())[0]
        await cursor.execute("SELECT COUNT(*) FROM prescriptions")
        prescriptions = (await cursor.fetchone())[0]
        
        print(f"\n📈 Records:")
        print(f"   👥 Users: {users}")
        print(f"   📁 Cases: {cases}")
        print(f"   💊 Prescriptions: {prescriptions}")
        
        await cursor.close()
        await conn.close()
        
    except Exception as e:
        print(f"❌ Could not fetch status: {e}")

def print_next_steps():
    """Print next steps"""
    print("\n" + "=" * 60)
    print("🚀 Next Steps:")
    print("=" * 60)
    print("\n1. Start the backend server:")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    print("\n2. Start the frontend:")
    print("   cd frontend")
    print("   npm run dev")
    print("\n3. Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n4. Demo Accounts:")
    print("   Admin: admin@medical.com / admin123")
    print("   Doctor: dr.smith@medical.com / doctor123")
    print("   Patient: patient.demo@medical.com / patient123")
    print("\n5. Database Access:")
    print("   Use your PHP MySQL admin panel")
    print("   Database: medical_center")
    print("   Tables: users, medical_cases, prescriptions")

async def main():
    """Main setup function"""
    try:
        print("🚀 Starting PHP MySQL Database Setup...")
        
        # Setup database
        success = await setup_php_mysql_database()
        
        if success:
            # Show status
            await show_database_status()
            
            # Print next steps
            print_next_steps()
            
            print("\n✅ PHP MySQL setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the error messages above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
