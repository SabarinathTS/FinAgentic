#!/usr/bin/env python3
"""
Launcher script for FinAgentic - Autonomous Agentic AI Agent System.
Handles environment configuration and launches the Streamlit Web Application.

Usage:
    python run.py
"""

import sys
import os
import subprocess

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    """Run the Streamlit application with proper paths"""

    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    env['PYTHONPATH'] = current_dir + os.pathsep + env.get('PYTHONPATH', '')

    print("🚀 Starting FinAgentic AI Agent System...")
    print(f"📁 Working directory: {current_dir}")
    print("-" * 50)

    # Run streamlit with proper environment
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "src/main.py"],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
