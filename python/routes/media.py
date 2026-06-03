from flask import Blueprint, request, jsonify, current_app, send_file
from models import db, Report
from utils.audio_helper import AudioHelper
from utils.media_helper import MediaHelper
from utils.location_helper import LocationHelper
import logging
import os

logger = logging.getLogger(__name__)

media_bp = Blueprint('media', __name__, url_prefix='/api/media')

# ==================== Audio Routes ====================

@media_bp.route('/audio/upload', methods=['POST'])
def upload_audio():
    """Upload and save audio file"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        report_id = request.form.get('report_id')
        
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save audio file
        audio_helper = AudioHelper(current_app.config['AUDIO_FOLDER'])
        result = audio_helper.save_audio_from_bytes(audio_file.read(), 
                                                     os.path.join(current_app.config['AUDIO_FOLDER'], audio_file.filename))
        
        if result['success']:
            # Update report with audio info
            if report_id:
                report = Report.query.get(report_id)
                if report:
                    report.audio_uri = result['file_path']
                    report.audio_duration_sec = result['duration_sec']
                    db.session.commit()
            
            return jsonify({
                'success': True,
                'audio_uri': result['file_path'],
                'duration_sec': result['duration_sec'],
                'filename': result['filename']
            }), 200
        else:
            return jsonify({'success': False, 'error': result.get('error')}), 400
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@media_bp.route('/audio/<int:report_id>', methods=['GET'])
def get_audio(report_id):
    """Get audio file for a report"""
    try:
        report = Report.query.get(report_id)
        if not report or not report.audio_uri:
            return jsonify({'success': False, 'error': 'Audio not found'}), 404
        
        if not os.path.exists(report.audio_uri):
            return jsonify({'success': False, 'error': 'Audio file not found'}), 404
        
        return send_file(report.audio_uri, mimetype='audio/wav')
    except Exception as e:
        logger.error(f"Error getting audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Media (Image/Video) Routes ====================

@media_bp.route('/image/upload', methods=['POST'])
def upload_image():
    """Upload and save image file"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        report_id = request.form.get('report_id')
        
        if image_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save image file
        media_helper = MediaHelper(current_app.config['MEDIA_FOLDER'])
        result = media_helper.save_media(image_file, image_file.filename, media_type='image')
        
        if result['success']:
            # Update report with media info
            if report_id:
                report = Report.query.get(report_id)
                if report:
                    report.media_uri = result['file_path']
                    report.media_type = 'image'
                    db.session.commit()
            
            return jsonify({
                'success': True,
                'media_uri': result['file_path'],
                'filename': result['filename'],
                'file_size': result['file_size']
            }), 200
        else:
            return jsonify({'success': False, 'error': result.get('error')}), 400
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@media_bp.route('/video/upload', methods=['POST'])
def upload_video():
    """Upload and save video file"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        report_id = request.form.get('report_id')
        
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save video file
        media_helper = MediaHelper(current_app.config['MEDIA_FOLDER'])
        result = media_helper.save_media(video_file, video_file.filename, media_type='video')
        
        if result['success']:
            # Update report with media info
            if report_id:
                report = Report.query.get(report_id)
                if report:
                    report.media_uri = result['file_path']
                    report.media_type = 'video'
                    db.session.commit()
            
            return jsonify({
                'success': True,
                'media_uri': result['file_path'],
                'filename': result['filename'],
                'file_size': result['file_size']
            }), 200
        else:
            return jsonify({'success': False, 'error': result.get('error')}), 400
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@media_bp.route('/image/<int:report_id>', methods=['GET'])
def get_image(report_id):
    """Get image file for a report"""
    try:
        report = Report.query.get(report_id)
        if not report or not report.media_uri or report.media_type != 'image':
            return jsonify({'success': False, 'error': 'Image not found'}), 404
        
        if not os.path.exists(report.media_uri):
            return jsonify({'success': False, 'error': 'Image file not found'}), 404
        
        return send_file(report.media_uri, mimetype='image/jpeg')
    except Exception as e:
        logger.error(f"Error getting image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Location Routes ====================

@media_bp.route('/location/address', methods=['POST'])
def get_address_from_coords():
    """Get address from coordinates"""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'success': False, 'error': 'Missing coordinates'}), 400
        
        location_helper = LocationHelper()
        result = location_helper.get_address_from_coords(latitude, longitude)
        
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Error getting address: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@media_bp.route('/location/coordinates', methods=['POST'])
def get_coords_from_address():
    """Get coordinates from address"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({'success': False, 'error': 'Missing address'}), 400
        
        location_helper = LocationHelper()
        result = location_helper.get_coords_from_address(address)
        
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        logger.error(f"Error getting coordinates: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
