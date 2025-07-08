"""
Database models for SESPCLSwitch
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Call(db.Model):
    __tablename__ = 'calls'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    to_number = db.Column(db.String(20), nullable=False)
    from_number = db.Column(db.String(20), nullable=False)
    text = db.Column(db.Text, nullable=True)
    audio_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    audio_file_path = db.Column(db.String(500), nullable=True)
    task_id = db.Column(db.String(36), nullable=True)  # Celery task ID
    duration = db.Column(db.Integer, nullable=True)  # Call duration in seconds
    
    def __repr__(self):
        return f'<Call {self.id}: {self.from_number} -> {self.to_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'to_number': self.to_number,
            'from_number': self.from_number,
            'text': self.text,
            'audio_url': self.audio_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'duration': self.duration
        }

class CallQueue(db.Model):
    __tablename__ = 'call_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.String(36), db.ForeignKey('calls.id'), nullable=False)
    priority = db.Column(db.Integer, default=1)  # 1 = high, 2 = medium, 3 = low
    queued_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_started = db.Column(db.DateTime, nullable=True)
    worker_id = db.Column(db.String(50), nullable=True)
    
    call = db.relationship('Call', backref='queue_entry')
    
    def __repr__(self):
        return f'<CallQueue {self.id}: Call {self.call_id}>'

class SystemMetrics(db.Model):
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_calls = db.Column(db.Integer, default=0)
    active_calls = db.Column(db.Integer, default=0)
    completed_calls = db.Column(db.Integer, default=0)
    failed_calls = db.Column(db.Integer, default=0)
    avg_processing_time = db.Column(db.Float, default=0.0)
    memory_usage = db.Column(db.Float, default=0.0)
    cpu_usage = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<SystemMetrics {self.timestamp}: {self.total_calls} calls>'
