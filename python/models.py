from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Report(db.Model):
    """Report model representing a whistleblower report"""
    __tablename__ = 'registre_signalement'
    
    # Clé primaire unique mappée sur votre nouvelle colonne physique
    id = db.Column('id_signalement', db.Integer, primary_key=True, autoincrement=True)
    
    # Mapping avec les colonnes réelles en français
    title = db.Column('titre', db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column('categorie', db.String(100), nullable=False)  
    severity = db.Column('gravite', db.String(50), nullable=False)  
    
    # Timestamps
    timestamp = db.Column('date_signalement', db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Géolocalisation
    latitude = db.Column(db.Numeric(9, 6), nullable=True)
    longitude = db.Column(db.Numeric(9, 6), nullable=True)
    location_address = db.Column('adresse', db.Text, nullable=True)
    
    # Pièces jointes
    media_uri = db.Column('medias_photos', db.String(255), nullable=True)  
    audio_uri = db.Column('audio_lien', db.String(255), nullable=True)  
    
    # Administration
    status = db.Column('statut', db.String(50), default='Nouveau')  
    admin_notes = db.Column('notes_admin', db.Text, default='')
    is_anonymous = db.Column('anonyme', db.String(3), default='Oui')
    
    # Métadonnées du déclarant
    reporter_email = db.Column('email', db.String(100), nullable=True)  
    reporter_phone = db.Column('telephone', db.String(50), nullable=True)  
    reporter_name = db.Column('nom_declarant', db.String(100), nullable=True)  
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'location_address': self.location_address,
            'media_uri': self.media_uri,
            'audio_uri': self.audio_uri,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'is_anonymous': self.is_anonymous,
            'reporter_email': self.reporter_email,
            'reporter_phone': self.reporter_phone,
            'reporter_name': self.reporter_name,
        }
    
    def __repr__(self):
        return f'<Report {self.id}: {self.title}>'


class AuditLog(db.Model):
    """Audit log for tracking report changes"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Pointage correct vers la nouvelle clé primaire de la table cible
    report_id = db.Column(db.Integer, db.ForeignKey('registre_signalement.id_signalement'), nullable=False)
    action = db.Column(db.String(100), nullable=False)  
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    changes = db.Column(db.Text)  
    performed_by = db.Column(db.String(255), nullable=True)  
    
    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'changes': json.loads(self.changes) if self.changes else None,
            'performed_by': self.performed_by,
        }