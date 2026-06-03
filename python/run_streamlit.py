#!/usr/bin/env python
"""
Streamlit App Runner
Starts the Streamlit interface for Signalement
"""

import subprocess
import time
import os
import sys
import signal

def run_streamlit():
    """Run Streamlit application"""
    print("\n" + "="*60)
    print("  SIGNALEMENT - Interface Streamlit")
    print("="*60)
    
    print("\n✓ Vérification de l'environnement...")
    
    # Check if Flask is running
    print("\n⚠️  Note: Assurez-vous que le backend Flask est en cours d'exécution!")
    print("   Lancez dans un autre terminal: python app.py")
    
    input("\nAppuyez sur Entrée pour continuer...")
    
    # Launch Streamlit
    print("\n► Lancement de Streamlit...")
    print("   Interface: http://localhost:8501")
    print("   Backend: http://localhost:5000\n")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--logger.level=info"
        ])
    except KeyboardInterrupt:
        print("\n\n► Arrêt de Streamlit...")
    except Exception as e:
        print(f"\n✗ Erreur: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_streamlit()
