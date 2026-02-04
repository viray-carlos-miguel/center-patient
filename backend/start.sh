#!/bin/bash
echo "🚀 Starting Medical Center Backend..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432; then
    echo "❌ PostgreSQL is not running. Please start PostgreSQL first."
    echo "💡 On Windows: net start postgresql-x64-16"
    echo "💡 On macOS: brew services start postgresql"
    echo "💡 On Linux: sudo systemctl start postgresql"
    exit 1
fi

# Install requirements
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload