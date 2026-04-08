#!/bin/bash

# Federated Learning CKD System - Startup Script

echo "🏥 Starting Federated Learning CKD System..."

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.11 -m venv venv"
    echo "Then run: source venv/bin/activate && cd App && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

# Initialize database
echo "📊 Initializing database..."
python -c "from App.backend.core.database import init_database; init_database()"

# Start the server
echo "🚀 Starting FastAPI server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "👑 Admin Dashboard: http://localhost:8000/admin"
echo "🏥 Client Dashboard: http://localhost:8000/client"
echo ""

python -m uvicorn App.backend.main:app --host 0.0.0.0 --port 8000 --reload

# Made with Bob
