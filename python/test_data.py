"""
Test data and utilities for development and testing
"""

import json
from app import create_app
from models import db, Report
from datetime import datetime

def seed_database():
    """Populate database with sample reports for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        
        # Sample reports
        reports = [
            Report(
                title="Mesures de sécurité insuffisantes",
                description="Les installations de sécurité dans le bâtiment sont obsolètes et non conformes aux normes actuelles.",
                category="Sécurité",
                severity="Critique",
                is_anonymous=True,
                latitude=48.8566,
                longitude=2.3522,
                location_address="Paris, France",
                status="Nouveau"
            ),
            Report(
                title="Pollution environnementale",
                description="Émissions polluantes anormales provenant de l'usine locale.",
                category="Environnement",
                severity="Élevé",
                is_anonymous=False,
                reporter_name="Jean Dupont",
                reporter_email="jean@example.com",
                reporter_phone="06 12 34 56 78",
                latitude=48.9500,
                longitude=2.4500,
                location_address="Banlieue nord",
                status="En cours"
            ),
            Report(
                title="Soupçons de corruption",
                description="Marché public attribué sans appel d'offres transparent.",
                category="Corruption",
                severity="Élevé",
                is_anonymous=True,
                latitude=43.2965,
                longitude=5.3698,
                location_address="Marseille, France",
                status="Nouveau"
            ),
            Report(
                title="Conditions de santé publique",
                description="Hygiène défaillante dans l'établissement de santé.",
                category="Santé publique",
                severity="Moyen",
                is_anonymous=True,
                latitude=49.2827,
                longitude=4.0460,
                location_address="Reims, France",
                status="Traité"
            ),
            Report(
                title="Autre problème signalé",
                description="Problème divers à signaler.",
                category="Autre",
                severity="Faible",
                is_anonymous=False,
                reporter_name="Marie Martin",
                reporter_email="marie@example.com",
                latitude=47.2184,
                longitude=-1.5536,
                location_address="Nantes, France",
                status="Rejeté"
            ),
        ]
        
        for report in reports:
            db.session.add(report)
        
        db.session.commit()
        print(f"✓ Seeded database with {len(reports)} sample reports")

def get_sample_report():
    """Get a sample report data for testing"""
    return {
        "title": "Test Report",
        "description": "This is a test report for the API",
        "category": "Sécurité",
        "severity": "Moyen",
        "is_anonymous": True,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "location_address": "Paris, France"
    }

def get_sample_anonymous_report():
    """Get a sample anonymous report"""
    return {
        "title": "Anonymous Whistleblower Report",
        "description": "This is an anonymous report",
        "category": "Corruption",
        "severity": "Élevé",
        "is_anonymous": True
    }

def get_sample_identified_report():
    """Get a sample identified report"""
    return {
        "title": "Identified Report",
        "description": "This is an identified report",
        "category": "Environnement",
        "severity": "Moyen",
        "is_anonymous": False,
        "reporter_name": "John Doe",
        "reporter_email": "john@example.com",
        "reporter_phone": "06 12 34 56 78"
    }

if __name__ == "__main__":
    seed_database()
