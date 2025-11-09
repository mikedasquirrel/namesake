"""
WSGI Configuration for PythonAnywhere Deployment
Flask Nominative Determinism Research Platform

This file is used by PythonAnywhere to run the Flask application.

Setup Instructions for PythonAnywhere:
1. Upload/clone this repository to your PythonAnywhere account
2. Create a new Web App (Python 3.10 or later)
3. Set the source code directory to: /home/yourusername/FlaskProject
4. Set the WSGI configuration file to: /home/yourusername/FlaskProject/wsgi.py
5. Set up virtualenv if needed: /home/yourusername/.virtualenvs/flask-project
6. Install requirements: pip install -r requirements.txt
7. Initialize database: flask db upgrade
8. Reload the web app
"""

import sys
import os
from pathlib import Path

# Add your project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables for production
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import the Flask app
from app import app as application

# Optional: Configure logging for production
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(project_home, 'logs', 'app.log')),
        logging.StreamHandler()
    ]
)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(project_home, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Initialize database if needed (for first run)
with application.app_context():
    from core.models import db
    try:
        # Check if database is accessible
        db.engine.connect()
        logging.info("Database connection successful")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        logging.warning("You may need to run 'flask db upgrade' to initialize the database")

# Log startup
logging.info("Flask application started successfully")
logging.info(f"Project home: {project_home}")
logging.info(f"Python version: {sys.version}")

# For debugging: print routes
if os.environ.get('DEBUG_ROUTES') == '1':
    logging.info("Available routes:")
    for rule in application.url_map.iter_rules():
        logging.info(f"  {rule.endpoint}: {rule.rule}")

