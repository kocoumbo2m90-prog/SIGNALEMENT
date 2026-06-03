import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
import logging
from PIL import Image

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

class MediaHelper:
    """Helper class for handling media files (photos, videos)"""
    
    def __init__(self, media_folder):
        self.media_folder = media_folder
        Path(self.media_folder).mkdir(parents=True, exist_ok=True)
    
    def save_media(self, file_stream, original_filename, media_type='image'):
        """
        Save media file to disk
        
        Args:
            file_stream: File stream/bytes
            original_filename: Original filename
            media_type: 'image' or 'video'
            
        Returns:
            dict: Success status and file info
        """
        try:
            # Get file extension
            filename = secure_filename(original_filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Validate extension
            if media_type == 'image':
                if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
                    return {'success': False, 'error': f'Invalid image format. Allowed: {ALLOWED_IMAGE_EXTENSIONS}'}
            elif media_type == 'video':
                if file_ext not in ALLOWED_VIDEO_EXTENSIONS:
                    return {'success': False, 'error': f'Invalid video format. Allowed: {ALLOWED_VIDEO_EXTENSIONS}'}
            
            # Generate unique filename
            unique_filename = f"{media_type}_{uuid.uuid4().hex}_{datetime.now().timestamp()}.{file_ext}"
            file_path = os.path.join(self.media_folder, unique_filename)
            
            # Save file
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Get file size before saving
            file_size = len(file_stream.getvalue()) if hasattr(file_stream, 'getvalue') else len(file_stream)
            
            # Check file size
            max_size = MAX_VIDEO_SIZE if media_type == 'video' else MAX_IMAGE_SIZE
            if file_size > max_size:
                return {'success': False, 'error': f'File too large. Max size: {max_size / (1024*1024):.0f}MB'}
            
            # Write file
            if hasattr(file_stream, 'read'):
                with open(file_path, 'wb') as f:
                    f.write(file_stream.read())
            else:
                with open(file_path, 'wb') as f:
                    f.write(file_stream)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': unique_filename,
                'file_size': file_size,
                'media_type': media_type
            }
        except Exception as e:
            logger.error(f"Error saving media: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_media(self, file_path):
        """
        Delete a media file
        
        Args:
            file_path: Path to media file
            
        Returns:
            dict: Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {'success': True}
            return {'success': False, 'error': 'File not found'}
        except Exception as e:
            logger.error(f"Error deleting media: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_media_info(self, file_path):
        """
        Get information about a media file
        
        Args:
            file_path: Path to media file
            
        Returns:
            dict: File information
        """
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            file_size = os.path.getsize(file_path)
            filename = os.path.basename(file_path)
            
            return {
                'success': True,
                'filename': filename,
                'file_path': file_path,
                'file_size': file_size
            }
        except Exception as e:
            logger.error(f"Error getting media info: {str(e)}")
            return {'success': False, 'error': str(e)}

from datetime import datetime
