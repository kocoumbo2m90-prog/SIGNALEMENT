from geopy.geocoders import Nominatim
import logging

logger = logging.getLogger(__name__)

class LocationHelper:
    """Helper class for geolocation operations"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="signalement_app")
    
    def get_address_from_coords(self, latitude, longitude):
        """
        Get address from latitude and longitude
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            dict: Address information
        """
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            return {
                'success': True,
                'address': location.address,
                'latitude': latitude,
                'longitude': longitude
            }
        except Exception as e:
            logger.error(f"Error getting address: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'latitude': latitude,
                'longitude': longitude
            }
    
    def get_coords_from_address(self, address):
        """
        Get coordinates from address
        
        Args:
            address: Address string
            
        Returns:
            dict: Coordinates
        """
        try:
            location = self.geolocator.geocode(address)
            if location:
                return {
                    'success': True,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address
                }
            else:
                return {
                    'success': False,
                    'error': 'Address not found'
                }
        except Exception as e:
            logger.error(f"Error getting coordinates: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_coords(self, latitude, longitude):
        """
        Validate latitude and longitude
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            bool: True if valid
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except:
            return False
