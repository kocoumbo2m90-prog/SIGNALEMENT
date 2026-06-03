import os
import uuid
from datetime import datetime
from pathlib import Path
import librosa
import soundfile as sf
import logging

logger = logging.getLogger(__name__)

class AudioHelper:
    """Helper class for audio recording and playback"""
    
    def __init__(self, audio_folder):
        self.audio_folder = audio_folder
        # Create audio folder if it doesn't exist
        Path(self.audio_folder).mkdir(parents=True, exist_ok=True)
    
    def start_recording(self):
        """
        Initialize recording file path. 
        Note: Actual recording happens on client side in web app.
        This method generates a path for the audio file to be saved.
        
        Returns:
            dict: Contains recording_id and file_path
        """
        recording_id = f"audio_rec_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        file_path = os.path.join(self.audio_folder, f"{recording_id}.wav")
        
        return {
            'recording_id': recording_id,
            'file_path': file_path,
            'filename': os.path.basename(file_path)
        }
    
    def save_audio_from_bytes(self, audio_data, file_path, sample_rate=16000):
        """
        Save audio data from bytes to file
        
        Args:
            audio_data: Audio data as bytes or numpy array
            file_path: Path where to save the file
            sample_rate: Sample rate of audio
            
        Returns:
            dict: Success status and file info
        """
        try:
            # Create directory if it doesn't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio file
            sf.write(file_path, audio_data, sample_rate)
            
            # Get duration
            duration = len(audio_data) / sample_rate
            
            return {
                'success': True,
                'file_path': file_path,
                'duration_sec': int(duration),
                'filename': os.path.basename(file_path)
            }
        except Exception as e:
            logger.error(f"Error saving audio: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_audio_duration(self, file_path):
        """
        Get duration of an audio file in seconds
        
        Args:
            file_path: Path to audio file
            
        Returns:
            float: Duration in seconds, or 0 if error
        """
        try:
            y, sr = librosa.load(file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            return int(duration)
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 0
    
    def play_audio(self, file_path):
        """
        For web application, audio playback happens in browser.
        This method validates that the audio file exists and is accessible.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            dict: File info if successful
        """
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            file_size = os.path.getsize(file_path)
            duration = self.get_audio_duration(file_path)
            
            return {
                'success': True,
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'duration_sec': duration,
                'file_size': file_size
            }
        except Exception as e:
            logger.error(f"Error accessing audio: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_audio(self, file_path):
        """
        Delete an audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            dict: Success status
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {'success': True}
            return {'success': False, 'error': 'File not found'}
        except Exception as e:
            logger.error(f"Error deleting audio: {str(e)}")
            return {'success': False, 'error': str(e)}
