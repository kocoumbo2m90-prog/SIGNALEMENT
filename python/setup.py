#!/usr/bin/env python
"""
Setup and initialization script for Signalement Python API
Run this script to set up the development environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"► {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"✗ Error running: {description}")
        return False
    print(f"✓ {description} completed successfully")
    return True

def main():
    print("\n" + "="*60)
    print("   SIGNALEMENT - Python API Setup")
    print("="*60)
    
    # Check Python version
    print(f"\n► Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        sys.exit(1)
    
    # Create virtual environment
    venv_path = "venv"
    if not os.path.exists(venv_path):
        if not run_command(f"{sys.executable} -m venv {venv_path}", "Creating virtual environment"):
            sys.exit(1)
    else:
        print(f"\n✓ Virtual environment already exists at {venv_path}")
    
    # Determine pip command
    if sys.platform == "win32":
        pip_cmd = f"{venv_path}\\Scripts\\pip"
        python_cmd = f"{venv_path}\\Scripts\\python"
    else:
        pip_cmd = f"{venv_path}/bin/pip"
        python_cmd = f"{venv_path}/bin/python"
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        sys.exit(1)
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("\n► Creating .env file from template")
        with open(".env.example", "r") as src:
            with open(".env", "w") as dst:
                dst.write(src.read())
        print("✓ .env file created (please review and configure)")
    else:
        print("\n✓ .env file already exists")
    
    # Create directories
    print("\n► Creating upload directories")
    Path("uploads/audio").mkdir(parents=True, exist_ok=True)
    Path("uploads/media").mkdir(parents=True, exist_ok=True)
    print("✓ Upload directories created")
    
    # Initialize database
    print("\n► Initializing database")
    init_script = """
from app import create_app
from models import db

app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')
"""
    
    with open("_init_db.py", "w") as f:
        f.write(init_script)
    
    if run_command(f"{python_cmd} _init_db.py", "Initializing database"):
        os.remove("_init_db.py")
    
    print("\n" + "="*60)
    print("   SETUP COMPLETE! ✓")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("="*60)
    
    if sys.platform == "win32":
        print(f"1. Activate virtual environment:")
        print(f"   .\\{venv_path}\\Scripts\\activate")
    else:
        print(f"1. Activate virtual environment:")
        print(f"   source {venv_path}/bin/activate")
    
    print(f"\n2. Review configuration:")
    print(f"   Edit .env file with your settings")
    
    print(f"\n3. Run the development server:")
    print(f"   python app.py")
    
    print(f"\n4. Access the API:")
    print(f"   http://localhost:5000")
    
    print(f"\n5. View API documentation:")
    print(f"   Open http://localhost:5000 in your browser")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
