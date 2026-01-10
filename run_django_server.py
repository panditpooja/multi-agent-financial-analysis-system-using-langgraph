#!/usr/bin/env python
"""
Helper script to run the Django development server.
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # Check if Django is installed
    try:
        import django
    except ImportError:
        print("❌ Django is not installed. Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check if migrations need to be run
    if not os.path.exists('db.sqlite3'):
        print("📦 Setting up database...")
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=False)
    
    # Run the server
    print("🚀 Starting Django development server...")
    print("📊 Open http://127.0.0.1:8000/ in your browser")
    print("Press Ctrl+C to stop the server\n")
    
    subprocess.run([sys.executable, 'manage.py', 'runserver'])

