#!/bin/bash

# FL-DP Healthcare Web Application Startup Script

echo "=========================================="
echo "FL-DP Healthcare Web Application"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo "📦 Installing dependencies..."
pip install -r App/requirements.txt --quiet

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p App/database
mkdir -p App/uploads
mkdir -p FL-DP-Healthcare/server
mkdir -p FL-DP-Healthcare/client1/dataset
mkdir -p FL-DP-Healthcare/client2/dataset
mkdir -p FL-DP-Healthcare/client3/dataset

echo "✅ Directories created"
echo ""

# Check if .env exists, if not copy from example
if [ ! -f "App/.env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp App/.env.example App/.env
    echo "✅ .env file created. Please update it with your settings."
fi

echo ""
echo "=========================================="
echo "🚀 Starting Application..."
echo "=========================================="
echo ""
echo "📍 Frontend: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/api/docs"
echo "📍 Alternative Docs: http://localhost:8000/api/redoc"
echo ""
echo "🔐 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Run the application
python -m uvicorn App.backend.main:app --reload --host 0.0.0.0 --port 8000

# Made with Bob
