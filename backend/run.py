# backend/run.py
import subprocess
import sys
import os

def setup_backend():
    print("🚀 Setting up Medical Center Backend")
    print("=" * 40)
    
    # Install requirements
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "asyncpg", "python-dotenv"])
    
    # Check PostgreSQL
    print("🐘 Checking PostgreSQL...")
    try:
        import asyncpg
        print("✅ asyncpg installed")
    except ImportError:
        print("❌ asyncpg not installed")
    
    print("\n✅ Setup complete!")
    print("\n📋 To start:")
    print("1. Start PostgreSQL service")
    print("2. Run: python main.py")
    print("3. Visit: http://localhost:8000")
    
    print("\n👤 Demo Users:")
    print("  Email: patient.demo@medical.com, Password: patient123")
    print("  Email: dr.smith@medical.com, Password: doctor123")

if __name__ == "__main__":
    setup_backend()