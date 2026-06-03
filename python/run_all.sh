#!/bin/bash
# Run both Flask backend and Streamlit frontend

echo "================================"
echo "  Signalement - Full Stack"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting Flask backend on http://localhost:5000..."
echo "Starting Streamlit frontend on http://localhost:8501..."
echo ""

# Start Flask backend in background
python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start Streamlit frontend
streamlit run streamlit_app.py

# Cleanup
trap "kill $FLASK_PID" EXIT
