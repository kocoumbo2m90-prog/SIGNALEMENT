"""
Unit tests for the Signalement API
Run with: pytest tests/
"""

import pytest
import json
from app import create_app
from models import db, Report

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

class TestHealthCheck:
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['status'] == 'API is running'

class TestReports:
    def test_get_empty_reports(self, client):
        """Test getting reports when none exist"""
        response = client.get('/api/reports')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['reports']) == 0
    
    def test_create_report(self, client):
        """Test creating a report"""
        report_data = {
            "title": "Test Report",
            "description": "This is a test",
            "category": "Sécurité",
            "severity": "Moyen",
            "is_anonymous": True
        }
        
        response = client.post('/api/reports',
                              data=json.dumps(report_data),
                              content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['report']['title'] == report_data['title']
    
    def test_get_report(self, client):
        """Test getting a specific report"""
        # Create a report first
        report_data = {
            "title": "Test Report",
            "description": "This is a test",
            "category": "Sécurité",
            "severity": "Moyen"
        }
        
        create_response = client.post('/api/reports',
                                     data=json.dumps(report_data),
                                     content_type='application/json')
        report_id = json.loads(create_response.data)['report']['id']
        
        # Get the report
        response = client.get(f'/api/reports/{report_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['report']['id'] == report_id

class TestCategories:
    def test_get_categories(self, client):
        """Test getting available categories"""
        response = client.get('/api/categories')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['categories']) > 0

class TestSeverities:
    def test_get_severities(self, client):
        """Test getting severity levels"""
        response = client.get('/api/severities')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['severities']) > 0

class TestStatuses:
    def test_get_statuses(self, client):
        """Test getting available statuses"""
        response = client.get('/api/statuses')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert len(data['statuses']) > 0
