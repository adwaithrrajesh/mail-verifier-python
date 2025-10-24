#!/usr/bin/env python3
"""
Email Finder Application Runner
Simple script to start the Flask application on port 9080
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting Email Finder Application...")
    print("📍 Port: 9080")
    print("🌐 Access: http://localhost:9080")
    print()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Check if virtual environment exists
    venv_path = script_dir / "venv"
    if not venv_path.exists():
        print("❌ Virtual environment not found.")
        print("Please create one with: python -m venv venv")
        sys.exit(1)
    
    # Determine the Python executable in the virtual environment
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix-like systems
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print("❌ Python executable not found in virtual environment.")
        sys.exit(1)
    
    print("🔧 Using virtual environment Python:", python_exe)
    print("🎯 Starting Flask application...")
    print("Press CTRL+C to stop the application")
    print()
    
    try:
        # Change to the script directory and run the application
        os.chdir(script_dir)
        subprocess.run([str(python_exe), "-m", "mailscout"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
