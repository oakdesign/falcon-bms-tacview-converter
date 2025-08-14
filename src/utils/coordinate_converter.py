"""
Coordinate conversion utilities for Falcon BMS
"""
import os
import struct
import math
import numpy as np
import pyproj
from pyproj import Proj

# Import unified theater config
try:
    from ..theater_config import get_theater_config
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from theater_config import get_theater_config

# Custom exceptions for elevation data
class ElevationError(Exception):
    """Base exception for elevation-related errors."""
    pass

class HeightmapNotFoundError(ElevationError):
    """Raised when heightmap file is not found or cannot be loaded."""
    pass

class CoordinatesOutOfBoundsError(ElevationError):
    """Raised when coordinates are outside the valid heightmap bounds."""
    pass

class HeightmapReadError(ElevationError):
    """Raised when there's an error reading from the heightmap file."""
    pass

# Try to import KTransverseMercator from pygeodesy (Karney implementation - closest to C# GeographicLib)
try:
    from pygeodesy.ktm import KTransverseMercator
    from pygeodesy import Ellipsoids
    KARNEY_AVAILABLE = True
    print("Using PyGeodesy KTransverseMercator (Karney implementation - high precision)")
except ImportError:
    KARNEY_AVAILABLE = False
    print("PyGeodesy not available, using pyproj fallback")

class CoordinateConverter:
    """Handles coordinate conversions between game coordinates and lat/lon."""
    
    def __init__(self, theater_name=None, theater_config=None, heightmap_path=None, falcon_bms_root=None):
        """Initialize converter with theater configuration.
        
        Args:
            theater_name: Name of theater to load (e.g., 'korea', 'balkans')
            theater_config: Pre-loaded theater configuration dict (legacy support)
            heightmap_path: Path to heightmap file
            falcon_bms_root: Root directory of Falcon BMS installation
        """
        if theater_config:
            # Legacy mode: use provided config
            self.theater_config = theater_config
        elif theater_name:
            # New mode: load from unified config system
            if falcon_bms_root:
                from ..theater_config import set_falcon_bms_root
                set_falcon_bms_root(falcon_bms_root)
            self.theater_config = get_theater_config(theater_name)
        else:
            raise ValueError("Either theater_name or theater_config must be provided")
        
        self.heightmap_path = heightmap_path
        
        # Use the projection string from config
        self.proj = Proj(self.theater_config['projection_string'])
        
        # Heightmap cache
        self._heightmap_data = None
        
    def feet_to_meters(self, feet):
        """Convert feet to meters."""
        FEET_PER_METER = 0.30488
        return feet * FEET_PER_METER

    def meters_to_feet(self, meters):
        """Convert meters to feet."""
        FT_TO_METERS = 0.30488
        return meters / FT_TO_METERS
    
    def parse_proj_str(self, proj_str: str) -> dict:
        """
        Parse a PROJ.4 projection string into a dictionary of {param: value}.
        """
        params = {}
        for token in proj_str.strip().split():
            if token.startswith("+"):
                key_val = token[1:].split("=", 1)
                key = key_val[0]
                val = key_val[1] if len(key_val) > 1 else None
                params[key] = val
        return params

    def game_to_latlon(self, game_x, game_y, from_feet=True):
        """Convert game coordinates to latitude/longitude."""
        if from_feet:
            # Convert feet to meters first
            game_x_m = self.feet_to_meters(np.float32(game_x))
            game_y_m = self.feet_to_meters(np.float32(game_y))
        else:
            game_x_m = game_x
            game_y_m = game_y
            
        # Convert using the projection string
        lon, lat = self.proj(game_x_m, game_y_m, inverse=True)
        
        return lat, lon
    
    def game_to_latlon_grid_karney(self, game_x, game_y, from_feet=True):
        """
        Grid-based coordinate conversion (matching BMS C++ logic) but using PyGeodesy KTransverseMercator
        for the final projection instead of pyproj. No empirical correction applied.
        """
        if not KARNEY_AVAILABLE:
            # Fallback to regular grid-based method
            return self.game_to_latlon_grid_based(game_x, game_y, from_feet)
        
        # Step 1: Calculate grid-based constants from theater config
        heightmap_size = self.theater_config['heightmap_size']
        heightmap_samples = heightmap_size[0]  # e.g., 32768
        heightmap_size_minus_one = heightmap_samples - 1  # e.g., 32767
        
        # Get configuration values
        theater_size_meters = self.theater_config.get('theater_size_meters')
        meter_res = self.theater_config.get('meter_res')
        grid_to_ft = self.theater_config.get('grid_to_ft')
        ft_to_grid = self.theater_config.get('ft_to_grid')
        
        # Calculate if not in config (fallback)
        if not all([theater_size_meters, meter_res, grid_to_ft, ft_to_grid]):
            theater_size_km = self.theater_config.get('theater_size_km', 1024)
            theater_size_meters = theater_size_km * 1000.0
            meter_res = theater_size_meters / heightmap_samples
            grid_to_ft = meter_res * 3.28084  # METER_RES * METERS_TO_FT
            ft_to_grid = 1.0 / grid_to_ft
        
        grid_offset = heightmap_size_minus_one / 2.0  # e.g., 16383.5
        
        # Step 2: Convert feet to grid coordinates (like C# ConvertSimXYToLatLon)
        if from_feet:
            sim_x = float(game_x)
            sim_y = float(game_y)
        else:
            # Convert meters to feet first
            sim_x = self.meters_to_feet(game_x)
            sim_y = self.meters_to_feet(game_y)
        
        # C#: num = 0f - GRID_OFFSET + simY * FT_TO_GRID
        # C#: num2 = 0f - GRID_OFFSET + simX * FT_TO_GRID
        grid_y = -grid_offset + sim_y * ft_to_grid
        grid_x = -grid_offset + sim_x * ft_to_grid
        
        # Step 3: Convert grid to lat/lon (like C# ConvertXZToLatLon)
        x = grid_x
        z = grid_y
        
        # C#: x += (double)(0.5f * m_TransverseMercatorMeta.HEIGHTMAP_SIZE);
        x += 0.5 * heightmap_size_minus_one
        
        # C#: z = 0.0 - (z - (double)(0.5f * m_TransverseMercatorMeta.HEIGHTMAP_SIZE));
        z = 0.0 - (z - 0.5 * heightmap_size_minus_one)
        
        # C#: x *= (double)m_TransverseMercatorMeta.METER_RES;
        # C#: z *= (double)m_TransverseMercatorMeta.METER_RES;
        x *= meter_res
        z *= meter_res
        
        # C#: z = (double)m_TransverseMercatorMeta.theaterSizeInMeters - z;
        z = theater_size_meters - z
        
        # Step 4: Apply projection offsets using PyGeodesy KTransverseMercator
        center_lat = self.theater_config.get('center_lat', 38.5)
        center_lon = self.theater_config.get('center_lon', 127.5)
        
        # Extract projection parameters from theater config
        proj_str = self.theater_config['projection_string']
        params = self.parse_proj_str(proj_str)
        
        lon0 = float(params.get("lon_0", center_lon))
        k0 = float(params.get("k", params.get("k_0", 0.9996)))
        
        # Create KTransverseMercator instance for offset calculation
        ktm = KTransverseMercator(a_earth=Ellipsoids.WGS84, lon0=lon0, k0=k0)
        
        # Calculate center projection coordinates using KTransverseMercator
        center_result = ktm.forward(center_lat, center_lon, center_lon)
        
        center_x_proj = center_result.easting
        center_y_proj = center_result.northing

        # Calculate offsets like C# should be -512000
        offset_x = center_x_proj - theater_size_meters / 2.0
        #need check
        offset_y = center_y_proj - theater_size_meters / 2.0
        
        # Apply offsets
        #final_x=-79613.372802734375
        final_x = x + offset_x
        #final_y=3973765.83902122
        final_y = z + offset_y
        
        # Step 5: Reverse project to get lat/lon using KTransverseMercator
        result = ktm.reverse(final_x, final_y,center_lon)
        lat = result.lat
        lon = result.lon
        
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
        """Get elevation at game coordinates from heightmap.
        
        Args:
            game_x: X coordinate in game units
            game_y: Y coordinate in game units
            from_feet: Whether input coordinates are in feet (True) or meters (False)
            
        Returns:
            float: Elevation in feet
            
        Raises:
            HeightmapNotFoundError: If heightmap file is not available
            CoordinatesOutOfBoundsError: If coordinates are outside valid bounds
            HeightmapReadError: If there's an error reading the heightmap file
        """
        if not self._load_heightmap():
            raise HeightmapNotFoundError("Heightmap file not found or cannot be accessed")
            
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
                raise CoordinatesOutOfBoundsError(
                    f"Coordinates ({x_pos:.1f}, {y_pos:.1f}) are outside valid bounds "
                    f"({bounds['min_x']:.1f}-{bounds['max_x']:.1f}, {bounds['min_y']:.1f}-{bounds['max_y']:.1f})"
                )
                
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
            try:
                with open(self.heightmap_path, 'rb') as f:
                    f.seek(file_offset)
                    raw_bytes = f.read(2)
                    
                    if len(raw_bytes) != 2:
                        raise HeightmapReadError(f"Expected 2 bytes, got {len(raw_bytes)} bytes")
                    
                    # Unpack single 16-bit unsigned integer (little endian)
                    raw_elevation = struct.unpack('<H', raw_bytes)[0]
            except (IOError, OSError) as e:
                raise HeightmapReadError(f"Error reading heightmap file: {e}")
            
            # Elevation values in heightmap are already in feet
            elevation_feet = raw_elevation
            
            return elevation_feet
            
        except (KeyError, ValueError) as e:
            raise HeightmapReadError(f"Error processing heightmap data: {e}")
            
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

def create_proj_string(center_lat, center_lon, desired_y=512000):
    """
    Create a Transverse Mercator projection string based on center coordinates.
    
    Args:
        center_lat (float): Center latitude in decimal degrees.
        center_lon (float): Center longitude in decimal degrees.
        desired_y (float): Desired Y position (in meters) in projected space. Default is 512000.
        
    Returns:
        float: The required false northing (y_0) value.
    """
    # Use temporary projection with y_0 = 0
    proj = Proj(f"+proj=tmerc +lon_0={center_lon} +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=0")
    
    # Project the geographic center point
    _, raw_y = proj(center_lon, center_lat)

    # Calculate required false northing
    y_0 = desired_y - raw_y
    
    return y_0