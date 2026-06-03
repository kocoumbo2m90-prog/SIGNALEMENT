@echo off
REM Quick setup script for Windows

echo ================================
echo   Signalement - Python Setup
echo ================================

REM Create virtual environment
echo.
echo ^> Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ^> Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ^> Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo ^> Installing dependencies...
pip install -r requirements.txt

REM Copy .env file
if not exist .env (
    echo ^> Creating .env file...
    copy .env.example .env
)

REM Create upload directories
echo ^> Creating upload directories...
if not exist uploads\audio mkdir uploads\audio
if not exist uploads\media mkdir uploads\media

REM Initialize database
echo ^> Initializing database...
python << 'EOF'
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('✓ Database initialized successfully!')
EOF

echo.
echo ================================
echo    SETUP COMPLETE! ✓
echo ================================

echo.
echo ^174 Next Steps:
echo 1. Virtual environment is active
echo 2. Review .env file with your settings
echo 3. Run: python app.py
echo 4. Access: http://localhost:5000

echo.
