from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Report(db.Model):
    """Report model representing a whistleblower report"""
    __tablename__ = 'reports'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Report content
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)  
    # Categories: Sécurité, Environnement, Corruption, Santé publique, Autre
    severity = db.Column(db.String(50), nullable=False)  
    # Severity levels: Faible, Moyen, Élevé, Critique
    
    # Timestamps
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Geolocation info
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_address = db.Column(db.String(500), nullable=True)
    
    # Attachments
    media_uri = db.Column(db.String(500), nullable=True)  # Path to photo/video
    media_type = db.Column(db.String(50), nullable=True)  # "image", "video", or null
    audio_uri = db.Column(db.String(500), nullable=True)  # Path to voice recording
    audio_duration_sec = db.Column(db.Integer, default=0)
    
    # Administration fields
    status = db.Column(db.String(50), default='Nouveau')  
    # Status: Nouveau, En cours, Traité, Rejeté
    admin_notes = db.Column(db.Text, default='')
    is_anonymous = db.Column(db.Boolean, default=True)
    
    # Additional metadata
    reporter_email = db.Column(db.String(255), nullable=True)  # Only if not anonymous
    reporter_phone = db.Column(db.String(20), nullable=True)  # Only if not anonymous
    reporter_name = db.Column(db.String(255), nullable=True)  # Only if not anonymous
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_address': self.location_address,
            'media_uri': self.media_uri,
            'media_type': self.media_type,
            'audio_uri': self.audio_uri,
            'audio_duration_sec': self.audio_duration_sec,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'is_anonymous': self.is_anonymous,
            'reporter_email': self.reporter_email if not self.is_anonymous else None,
            'reporter_phone': self.reporter_phone if not self.is_anonymous else None,
            'reporter_name': self.reporter_name if not self.is_anonymous else None,
        }
    
    def __repr__(self):
        return f'<Report {self.id}: {self.title}>'


class AuditLog(db.Model):
    """Audit log for tracking report changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  # created, updated, status_changed, etc.
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    changes = db.Column(db.Text)  # JSON string of what changed
    performed_by = db.Column(db.String(255), nullable=True)  # Admin user or 'system'
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'changes': json.loads(self.changes) if self.changes else None,
            'performed_by': self.performed_by,
        }
