"""Test script to verify backend can start"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.main import app
    print("✓ Backend app loaded successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ App version: {app.version}")
    print("✓ Backend is ready to start")
except Exception as e:
    print(f"✗ Error loading backend: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
