from vercel_python_serverless import VercelApp
import sys
import os

# Make sure Python can find your src/ folder
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app  # import your Flask app from src/app.py

handler = VercelApp(app)
