#!/bin/bash
# Quick setup script for macOS/Linux

echo "================================"
echo "  Signalement - Python Setup"
echo "================================"

# Create virtual environment
echo -e "\n► Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "► Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "► Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "► Installing dependencies..."
pip install -r requirements.txt

# Copy .env file
if [ ! -f .env ]; then
    echo "► Creating .env file..."
    cp .env.example .env
fi

# Create upload directories
echo "► Creating upload directories..."
mkdir -p uploads/audio
mkdir -p uploads/media

# Initialize database
echo "► Initializing database..."
python3 << 'EOF'
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('✓ Database initialized successfully!')
EOF

echo -e "\n================================"
echo "   SETUP COMPLETE! ✓"
echo "================================"

echo -e "\n📋 Next Steps:"
echo "1. Virtual environment is active"
echo "2. Review .env file with your settings"
echo "3. Run: python app.py"
echo "4. Access: http://localhost:5000"

echo ""
