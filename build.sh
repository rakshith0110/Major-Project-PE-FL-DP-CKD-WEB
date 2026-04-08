#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
cd App
python -c "from backend.core.database import init_database; init_database()"
cd ..

echo "✅ Build completed successfully!"

# Made with Bob
