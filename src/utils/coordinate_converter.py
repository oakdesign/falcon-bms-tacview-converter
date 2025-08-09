"""
Coordinate conversion utilities for Falcon BMS
"""
import os
import struct
import math
from pyproj import Proj

class CoordinateConverter:
    """Handles coordinate conversions between game coordinates and lat/lon."""
    
    def __init__(self, theater_config, heightmap_path=None):
        """Initialize converter with theater configuration."""
        self.theater_config = theater_config
        self.heightmap_path = heightmap_path
        
        # Use the original projection string from config
        self.proj = Proj(theater_config['projection_string'])
        
        # Heightmap cache
        self._heightmap_data = None
        
    def feet_to_meters(self, feet):
        """Convert feet to meters."""
        return feet * 0.3048799096
        
    def meters_to_feet(self, meters):
        """Convert meters to feet."""
        return meters / 0.3048799096
        
    def game_to_latlon(self, game_x, game_y, from_feet=True):
        """Convert game coordinates to latitude/longitude."""
        if from_feet:
            # Convert feet to meters first
            game_x_m = self.feet_to_meters(game_x)
            game_y_m = self.feet_to_meters(game_y)
        else:
            game_x_m = game_x
            game_y_m = game_y
            
        # Convert using the projection string
        lon, lat = self.proj(game_x_m, game_y_m, inverse=True)
        
        return lat, lon
        
    def latlon_to_game(self, lat, lon, to_feet=True):
        """Convert latitude/longitude to game coordinates."""
        # Convert lat/lon to projected coordinates
        game_x_m, game_y_m = self.proj(lon, lat)
        
        if to_feet:
            return self.meters_to_feet(game_x_m), self.meters_to_feet(game_y_m)
        else:
            return game_x_m, game_y_m
        
    def get_map_corners(self, in_feet=True):
        """Get the lat/lon coordinates of map corners."""
        bounds = self.theater_config['heightmap_bounds']
        
        # Get corner coordinates
        corners = {
            'sw': (bounds['min_x'], bounds['min_y']),  # Southwest
            'se': (bounds['max_x'], bounds['min_y']),  # Southeast  
            'nw': (bounds['min_x'], bounds['max_y']),  # Northwest
            'ne': (bounds['max_x'], bounds['max_y'])   # Northeast
        }
        
        # Convert to lat/lon
        corner_coords = {}
        for corner_name, (x, y) in corners.items():
            lat, lon = self.game_to_latlon(x, y, from_feet=in_feet)
            corner_coords[corner_name] = {
                'game': (x, y),
                'latlon': (lat, lon)
            }
            
        return corner_coords
        
    def _load_heightmap(self):
        """Check if heightmap file exists - don't load into memory."""
        if not self.heightmap_path or not os.path.exists(self.heightmap_path):
            return False
        return True
        
    def get_elevation(self, game_x, game_y, from_feet=True):
        """Get elevation at game coordinates from heightmap."""
        if not self._load_heightmap():
            return -999  # Heightmap not available
            
        try:
            bounds = self.theater_config['heightmap_bounds']
            width, height = self.theater_config['heightmap_size']
            
            # Convert coordinates if needed
            if from_feet:
                x_pos = game_x
                y_pos = game_y
            else:
                x_pos = self.meters_to_feet(game_x)
                y_pos = self.meters_to_feet(game_y)
            
            # Check bounds
            if (x_pos < bounds['min_x'] or x_pos > bounds['max_x'] or
                y_pos < bounds['min_y'] or y_pos > bounds['max_y']):
                return -997  # Out of bounds
                
            # Calculate grid position
            x_ratio = (x_pos - bounds['min_x']) / (bounds['max_x'] - bounds['min_x'])
            y_ratio = (y_pos - bounds['min_y']) / (bounds['max_y'] - bounds['min_y'])
            
            # Convert to pixel coordinates
            pixel_x = int(x_ratio * (width - 1))
            pixel_y = int((1.0 - y_ratio) * (height - 1))  # Flip Y coordinate
            
            # Clamp to valid range
            pixel_x = max(0, min(width - 1, pixel_x))
            pixel_y = max(0, min(height - 1, pixel_y))
            
            # Calculate file offset for this specific pixel
            index = pixel_y * width + pixel_x
            file_offset = index * 2  # 2 bytes per 16-bit value
            
            # Read only the specific 2 bytes we need
            with open(self.heightmap_path, 'rb') as f:
                f.seek(file_offset)
                raw_bytes = f.read(2)
                
                if len(raw_bytes) != 2:
                    return -996  # Read error
                
                # Unpack single 16-bit unsigned integer (little endian)
                raw_elevation = struct.unpack('<H', raw_bytes)[0]
            
            # Elevation values in heightmap are already in feet
            elevation_feet = raw_elevation
            
            return elevation_feet
            
        except Exception as e:
            print(f"Error reading elevation: {e}")
            return -996  # Read error
            
    def format_coordinates(self, lat, lon, include_dms=False):
        """Format coordinates in various formats."""
        result = {
            'decimal': (lat, lon),
            'decimal_str': f"{lat:.6f}°, {lon:.6f}°"
        }
        
        if include_dms:
            # Convert to degrees, minutes, seconds
            def dd_to_dms(dd):
                degrees = int(dd)
                minutes_float = abs(dd - degrees) * 60
                minutes = int(minutes_float)
                seconds = (minutes_float - minutes) * 60
                return degrees, minutes, seconds
                
            lat_d, lat_m, lat_s = dd_to_dms(lat)
            lon_d, lon_m, lon_s = dd_to_dms(lon)
            
            result['dms'] = {
                'lat': (lat_d, lat_m, lat_s),
                'lon': (lon_d, lon_m, lon_s)
            }
            result['dms_str'] = f"{lat_d}° {lat_m}' {lat_s:.2f}\", {lon_d}° {lon_m}' {lon_s:.2f}\""
            
        return result


# Legacy functions for backwards compatibility
def convert_coordinates(lat, lon, projection_string):
    from pyproj import Proj, transform

    # Create a projection object based on the provided projection string
    proj = Proj(projection_string)

    # Convert latitude and longitude to the specified projection
    x, y = proj(lon, lat)

    return x, y

def reverse_convert_coordinates(x, y, projection_string):
    from pyproj import Proj, transform

    # Create a projection object based on the provided projection string
    proj = Proj(projection_string)

    # Reverse convert the projected coordinates back to latitude and longitude
    lon, lat = proj(x, y, inverse=True)

    return lat, lon