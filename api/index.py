"""
Vercel serverless function wrapper for FastAPI app.
This file is required for Vercel to properly route requests to the FastAPI application.
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app

# Export the app for Vercel
# Vercel expects the handler to be named 'handler' or 'app'
handler = app
