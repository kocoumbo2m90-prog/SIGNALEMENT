@echo off
REM Run both Flask backend and Streamlit frontend

echo ================================
echo   Signalement - Full Stack
echo ================================

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting Flask backend on http://localhost:5000...
echo Starting Streamlit frontend on http://localhost:8501...
echo.

REM Start Flask backend in new window
start "Flask Backend" cmd /k "python app.py"

REM Wait for Flask to start
timeout /t 3 /nobreak

REM Start Streamlit frontend
streamlit run streamlit_app.py

pause
