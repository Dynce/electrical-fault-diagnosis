"""
WSGI application entry point for production deployment.
Used by Gunicorn, Waitress, and other WSGI servers.
"""
import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

if __name__ == "__main__":
    app.run()
