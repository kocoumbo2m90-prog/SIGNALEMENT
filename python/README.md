# Signalement - Python Backend API

A Python web application for whistleblower reporting, converted from the original Android Kotlin app. This is a REST API built with Flask that provides comprehensive report management, audio recording, media uploads, and geolocation features.

## Features

✅ **Report Management**
- Create, read, update, and delete whistleblower reports
- Categorize reports (Sécurité, Environnement, Corruption, Santé publique, Autre)
- Track report severity (Faible, Moyen, Élevé, Critique)
- Monitor report status (Nouveau, En cours, Traité, Rejeté)
- Anonymous and identified reporting options

✅ **Audio Support**
- Record and upload voice reports
- Audio file management
- Automatic audio duration tracking

✅ **Media Handling**
- Photo uploads (JPEG, PNG, GIF, WebP)
- Video uploads (MP4, AVI, MOV, MKV, WebM)
- File size validation
- Secure file storage

✅ **Geolocation**
- Store report location (latitude/longitude)
- Reverse geocoding (coordinates → address)
- Forward geocoding (address → coordinates)
- Location validation

✅ **Database**
- SQLite/PostgreSQL support
- SQLAlchemy ORM
- Audit logging for all changes
- Automated timestamps

✅ **API Features**
- RESTful API design
- JSON responses
- Pagination support
- CORS enabled
- Comprehensive error handling
- Request logging

## Tech Stack

- **Framework**: Flask 2.3
- **Database**: SQLAlchemy ORM with SQLite (or PostgreSQL)
- **Audio**: librosa, soundfile
- **Geolocation**: geopy
- **Media Processing**: Pillow
- **API**: Flask-CORS
- **Python**: 3.8+

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### 2. Clone and Setup

```bash
# Navigate to the python directory
cd python

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional for development)
# Default settings work for local development
```

### 4. Initialize Database

```bash
# The database is created automatically on first run
# No manual initialization needed!
```

## Running the Application

### Development Server

```bash
# From the python directory (with venv activated)
python app.py
```

The API will be available at `http://localhost:5000`

### Production Deployment

```bash
# Install production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## API Endpoints

### Health & Status
- `GET /` - API welcome and endpoint list
- `GET /health` - Health check

### Reports
- `GET /api/reports` - List all reports (with pagination and filtering)
- `GET /api/reports/<id>` - Get specific report
- `POST /api/reports` - Create new report
- `PUT /api/reports/<id>` - Update report
- `DELETE /api/reports/<id>` - Delete report

### Reports Statistics
- `GET /api/reports/stats/summary` - Get summary statistics

### Categories & Options
- `GET /api/categories` - Get available categories
- `GET /api/severities` - Get severity levels
- `GET /api/statuses` - Get report statuses

### Media (Audio/Video/Images)
- `POST /api/media/audio/upload` - Upload audio file
- `GET /api/media/audio/<report_id>` - Download audio
- `POST /api/media/image/upload` - Upload image
- `GET /api/media/image/<report_id>` - Download image
- `POST /api/media/video/upload` - Upload video

### Geolocation
- `POST /api/media/location/address` - Get address from coordinates
- `POST /api/media/location/coordinates` - Get coordinates from address

## Usage Examples

### Create a Report

```bash
curl -X POST http://localhost:5000/api/reports \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sécurité insuffisante",
    "description": "Les mesures de sécurité sont insuffisantes...",
    "category": "Sécurité",
    "severity": "Élevé",
    "is_anonymous": true,
    "latitude": 48.8566,
    "longitude": 2.3522,
    "location_address": "Paris, France"
  }'
```

### Get All Reports

```bash
curl http://localhost:5000/api/reports?page=1&per_page=20
```

### Filter Reports

```bash
curl "http://localhost:5000/api/reports?status=Nouveau&category=Sécurité"
```

### Upload Audio

```bash
curl -X POST http://localhost:5000/api/media/audio/upload \
  -F "audio=@recording.wav" \
  -F "report_id=1"
```

### Get Address from Coordinates

```bash
curl -X POST http://localhost:5000/api/media/location/address \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 48.8566,
    "longitude": 2.3522
  }'
```

## Database Models

### Report
- `id` - Primary key
- `title` - Report title
- `description` - Detailed description
- `category` - Report category
- `severity` - Severity level
- `timestamp` - Creation date
- `updated_at` - Last update date
- `latitude` - Latitude coordinate
- `longitude` - Longitude coordinate
- `location_address` - Address string
- `media_uri` - Path to photo/video
- `media_type` - Media type (image/video)
- `audio_uri` - Path to audio recording
- `audio_duration_sec` - Audio duration in seconds
- `status` - Report status
- `admin_notes` - Admin comments
- `is_anonymous` - Anonymous flag
- `reporter_name` - Reporter name (if not anonymous)
- `reporter_email` - Reporter email (if not anonymous)
- `reporter_phone` - Reporter phone (if not anonymous)

### AuditLog
- `id` - Primary key
- `report_id` - Associated report
- `action` - Action performed
- `timestamp` - Action timestamp
- `changes` - JSON of what changed
- `performed_by` - User who performed action

## File Structure

```
python/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── routes/
│   ├── __init__.py
│   ├── reports.py        # Report endpoints
│   └── media.py          # Media endpoints
└── utils/
    ├── __init__.py
    ├── audio_helper.py   # Audio processing
    ├── media_helper.py   # Media file handling
    └── location_helper.py # Geolocation
```

## Configuration

Edit `.env` file to customize:

```env
# Flask
FLASK_ENV=development
DEBUG=True

# Database
DATABASE_URL=sqlite:///signalement.db

# Security
SECRET_KEY=your-secret-key

# CORS (for web frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# File uploads
MAX_UPLOAD_SIZE=500000000
```

## Testing

```bash
# Run tests (implement pytest tests as needed)
pytest
```

## Deployment

### Docker
A Dockerfile can be added for containerization

### Cloud Platforms
- Heroku: `pip install python-dotenv` and set environment variables
- AWS: Deploy with Elastic Beanstalk or Lambda
- GCP: Deploy to App Engine or Cloud Run
- Azure: Deploy to App Service

## Security Notes

1. Change `SECRET_KEY` in production
2. Use `HTTPS` in production
3. Set `SESSION_COOKIE_SECURE=True` in production
4. Configure `CORS_ORIGINS` properly
5. Use environment variables for sensitive data
6. Validate and sanitize all inputs
7. Implement rate limiting
8. Use a proper production database

## Common Issues

**Port Already in Use**
```bash
# Change port in app.py or use:
python app.py --port 8000
```

**Database Locked**
```bash
# Remove old database and restart
rm signalement.db
python app.py
```

**Module Not Found**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

## Comparison with Android App

| Feature | Android | Python |
|---------|---------|--------|
| UI | Jetpack Compose | REST API |
| Database | Room (SQLite) | SQLAlchemy (SQLite/PostgreSQL) |
| Audio | MediaRecorder | librosa/soundfile |
| Maps | Google Maps | geopy |
| Storage | Internal/External | File system |
| Deployment | APK | Web server |

## Development

### Adding New Endpoints

1. Create a route in `routes/`
2. Import in `app.py`
3. Register with `app.register_blueprint()`

### Adding Database Fields

1. Update model in `models.py`
2. Database schema updates automatically
3. Add migration if needed (optional)

## License

Same as the original Android project

## Support

For issues or questions:
1. Check existing issues
2. Review API documentation
3. Check `.env.example` for configuration
4. Verify Python version (3.8+)

## Next Steps

1. ✅ Create Python backend API
2. Create web frontend (React/Vue.js)
3. Add authentication (JWT)
4. Add email notifications
5. Add advanced search and filtering
6. Add analytics dashboard
7. Add automated testing
8. Add Swagger/OpenAPI documentation

---

**Converted from**: Android Kotlin App (Signalement)
**Conversion Date**: May 2026
**Python Version**: 3.8+
