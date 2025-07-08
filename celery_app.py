"""
Celery App Configuration
Separate module to avoid circular imports
"""
from celery import Celery
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Celery
celery_app = Celery('voice_call_api')

# Configuration
celery_app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('result_backend', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    include=['tasks']  # This tells Celery to include tasks from tasks.py
)

# Add current directory to Python path to ensure modules can be imported
import sys
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

# Create minimal Flask app for Celery tasks
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask app instance for Celery tasks
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://postgres:password@localhost:5432/voicecall_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db
db.init_app(app)

# Import tasks to register them
try:
    import tasks
except ImportError as e:
    print(f"Warning: Could not import tasks: {e}")
