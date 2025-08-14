"""
Theater configuration loader for Falcon BMS
Reads configuration from Falcon BMS theater.txt and related files,
with fallback to static configuration.
"""
import os
import re
from typing import Dict, Optional, List, Tuple

# Try to import from parent config module
try:
    from ..config import THEATER_CONFIGS, FALCON_BMS_ROOT
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config import THEATER_CONFIGS, FALCON_BMS_ROOT


class TheaterConfigLoader:
    """Loads theater configuration from Falcon BMS files with static fallback."""
    
    def __init__(self, falcon_bms_root: str = None):
        """Initialize with Falcon BMS root directory."""
        self.falcon_bms_root = falcon_bms_root or FALCON_BMS_ROOT
        self._theater_cache = {}
    
    def get_available_theaters(self) -> List[str]:
        """Get list of available theaters from theater.lst and static config."""
        theaters = set()
        
        # Try to read from theater.lst
        try:
            theater_lst_path = os.path.join(
                self.falcon_bms_root, 
                'Data', 'TerrData', 'TheaterDefinition', 'Theater.lst'
            )
            if os.path.exists(theater_lst_path):
                with open(theater_lst_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract theater name from path like "TerrData\TheaterDefinition\Korea KTO.tdf"
                            theater_name = self._extract_theater_name_from_tdf_path(line)
                            if theater_name:
                                theaters.add(theater_name.lower())
        except Exception as e:
            print(f"Warning: Could not read theater.lst: {e}")
        
        # Add theaters from static config
        theaters.update(THEATER_CONFIGS.keys())
        
        return sorted(list(theaters))
    
    def _extract_theater_name_from_tdf_path(self, tdf_path: str) -> Optional[str]:
        """Extract theater name from TDF file path."""
        # Examples:
        # "TerrData\TheaterDefinition\Korea KTO.tdf" -> "korea"
        # "Add-On Balkans\Terrdata\theaterdefinition\Balkans.tdf" -> "balkans"
        
        if 'korea' in tdf_path.lower():
            return 'korea'
        elif 'balkan' in tdf_path.lower():
            return 'balkans'
        elif 'israel' in tdf_path.lower():
            return 'israel'
        elif 'falcon' in tdf_path.lower():
            return 'falcon'
        
        return None
    
    def get_theater_config(self, theater_name: str) -> Dict:
        """Get complete theater configuration, preferring dynamic loading."""
        theater_name = theater_name.lower()
        
        # Return cached config if available
        if theater_name in self._theater_cache:
            return self._theater_cache[theater_name]
        
        # Try to load from Falcon BMS files
        try:
            config = self._load_theater_from_files(theater_name)
            if config:
                self._theater_cache[theater_name] = config
                return config
        except Exception as e:
            print(f"Warning: Could not load {theater_name} from files: {e}")
        
        # Fallback to static configuration
        if theater_name in THEATER_CONFIGS:
            config = THEATER_CONFIGS[theater_name].copy()
            self._theater_cache[theater_name] = config
            return config
        
        raise ValueError(f"Theater '{theater_name}' not found in files or static config")
    
    def _load_theater_from_files(self, theater_name: str) -> Optional[Dict]:
        """Load theater configuration from Falcon BMS files."""
        theater_txt_path = self._find_theater_txt_path(theater_name)
        if not theater_txt_path:
            return None
        
        # Parse theater.txt
        theater_data = self._parse_theater_txt(theater_txt_path)
        if not theater_data:
            return None
        
        # Build configuration
        config = {
            'name': theater_data.get('theater_name', theater_name.title()),
            'center_lat': theater_data.get('center_latitude'),
            'center_lon': theater_data.get('center_longitude'),
            'theater_size_km': theater_data.get('theater_size_km'),
            'heightmap_size': (
                theater_data.get('map_size_pixels', 32768),
                theater_data.get('map_size_pixels', 32768)
            ),
            'min_height': theater_data.get('min_height', -1500),
            'max_height': theater_data.get('max_height', 10000),
        }
        
        # Add projection string if available from theater.txt
        if 'projection_string' in theater_data:
            config['projection_string'] = theater_data['projection_string']
        
        # Calculate derived values
        config.update(self._calculate_derived_config(config))
        
        # Add paths for compatibility
        config.update(self._get_theater_paths(theater_name))
        
        return config
    
    def _find_theater_txt_path(self, theater_name: str) -> Optional[str]:
        """Find the theater.txt file path for a given theater."""
        possible_paths = []
        
        if theater_name == 'korea':
            possible_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'TerrData', 'Korea', 'NewTerrain', 'Theater.txt')
            ]
        elif theater_name == 'balkans':
            possible_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Balkans', 'Terrdata', 'Balkans', 'NewTerrain', 'Theater.txt')
            ]
        elif theater_name == 'israel':
            possible_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Israel', 'TerrData', 'Israel', 'NewTerrain', 'Theater.txt')
            ]
        elif theater_name == 'falcon':
            possible_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Falcon', 'TerrData', 'Falcon', 'NewTerrain', 'Theater.txt')
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _parse_theater_txt(self, theater_txt_path: str) -> Optional[Dict]:
        """Parse theater.txt file."""
        try:
            data = {}
            with open(theater_txt_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip().lower().replace(' ', '_')
                        value = value.strip()
                        
                        # Handle projection string specially (don't convert to lowercase)
                        if key == 'projection_string':
                            data[key] = value
                        # Convert numeric values
                        elif key in ['center_latitude', 'center_longitude']:
                            data[key] = float(value)
                        elif key in ['theater_size_km', 'theater_size_in_km', 'map_size_in_pixels', 'min_height_in_theater', 'max_height_in_theater']:
                            data[key] = int(value)
                        else:
                            data[key] = value
                        
                        # Normalize key names
                        if key == 'map_size_in_pixels':
                            data['map_size_pixels'] = data[key]
                        elif key == 'theater_size_in_km':
                            data['theater_size_km'] = int(value)  # Ensure it's an int
                        elif key == 'min_height_in_theater':
                            data['min_height'] = data[key]
                        elif key == 'max_height_in_theater':
                            data['max_height'] = data[key]
                        elif key == 'projection_string':
                            # Keep the projection string as-is
                            data['projection_string'] = value
            
            return data
        except Exception as e:
            print(f"Error parsing {theater_txt_path}: {e}")
            return None
    
    def _calculate_derived_config(self, config: Dict) -> Dict:
        """Calculate derived configuration values."""
        center_lat = config['center_lat']
        center_lon = config['center_lon']
        theater_size_km = config['theater_size_km']
        map_size_pixels = config['heightmap_size'][0]
        
        # Calculate theater bounds and projection
        derived = {}
        
        # Use projection string from theater.txt if available, otherwise build one
        if 'projection_string' in config and config['projection_string']:
            derived['projection_string'] = config['projection_string']
            # Try to extract UTM zone from projection string
            if '+zone=' in config['projection_string']:
                zone_part = config['projection_string'].split('+zone=')[1].split()[0]
                derived['utm_zone'] = int(zone_part)
            else:
                # Fallback calculation
                derived['utm_zone'] = int((center_lon + 180) / 6) + 1
        else:
            # Build projection string based on center coordinates
            if theater_size_km == 1024:  # Standard large theater
                if abs(center_lon - 127.5) < 1:  # Korea
                    derived['projection_string'] = "+proj=tmerc +lon_0=127.5 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-3.74929e+06"
                    derived['utm_zone'] = 52
                elif abs(center_lon - 16.4191) < 1:  # Balkans
                    derived['projection_string'] = "+proj=tmerc +lon_0=16.4191 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-4.1192e+06"
                    derived['utm_zone'] = 34
                else:
                    # Generic UTM projection
                    utm_zone = int((center_lon + 180) / 6) + 1
                    derived['utm_zone'] = utm_zone
                    derived['projection_string'] = f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs"
            else:
                # Smaller theater, use UTM
                utm_zone = int((center_lon + 180) / 6) + 1
                derived['utm_zone'] = utm_zone
                derived['projection_string'] = f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs"
        
        derived['utm_hemisphere'] = 'north' if center_lat >= 0 else 'south'
        
        # Calculate theater bounds in feet (game coordinates)
        theater_size_meters = theater_size_km * 1000
        theater_size_feet = theater_size_meters * 3.28084
        
        derived['heightmap_bounds'] = {
            'min_x': 0,
            'max_x': theater_size_feet,
            'min_y': 0,
            'max_y': theater_size_feet
        }
        
        # Add constants needed for coordinate conversion
        derived['theater_size_meters'] = theater_size_meters
        derived['meter_res'] = theater_size_meters / map_size_pixels  # meters per pixel
        derived['grid_to_ft'] = derived['meter_res'] * 3.28084  # METER_RES * METERS_TO_FT
        derived['ft_to_grid'] = 1.0 / derived['grid_to_ft']  # conversion factor
        
        return derived
    
    def _get_theater_paths(self, theater_name: str) -> Dict:
        """Get file paths for theater (for backward compatibility)."""
        # Use the same logic as the original config.py
        if theater_name == 'korea':
            subdir_info = {
                'campaign_subdir': 'Campaign',
                'terrain_subdir': 'TerrData/Korea/NewTerrain',
                'heightmap_file': 'HeightMaps/HeightMap.raw'
            }
        elif theater_name == 'balkans':
            subdir_info = {
                'campaign_subdir': 'Add-On Balkans/Campaign',
                'terrain_subdir': 'Add-On Balkans/TerrData/Balkans',
                'heightmap_file': 'HeightMaps/HeightMap.raw'
            }
        elif theater_name == 'israel':
            subdir_info = {
                'campaign_subdir': 'Add-On Israel/Campaign',
                'terrain_subdir': 'Add-On Israel/TerrData/Israel',
                'heightmap_file': 'HeightMaps/HeightMap.raw'
            }
        elif theater_name == 'falcon':
            subdir_info = {
                'campaign_subdir': 'Add-On Falcon/Campaign',
                'terrain_subdir': 'Add-On Falcon/TerrData/Falcon',
                'heightmap_file': 'HeightMaps/HeightMap.raw'
            }
        else:
            # Default values
            subdir_info = {
                'campaign_subdir': 'Campaign',
                'terrain_subdir': f'TerrData/{theater_name.title()}',
                'heightmap_file': 'HeightMaps/HeightMap.raw'
            }
        
        return subdir_info


# Global instance for backward compatibility
_default_loader = None

def get_theater_config(theater_name: str, falcon_bms_root: str = None) -> Dict:
    """Get theater configuration, preferring dynamic loading from files."""
    global _default_loader
    if _default_loader is None or (falcon_bms_root and falcon_bms_root != _default_loader.falcon_bms_root):
        _default_loader = TheaterConfigLoader(falcon_bms_root)
    return _default_loader.get_theater_config(theater_name)

def get_available_theaters(falcon_bms_root: str = None) -> List[str]:
    """Get list of available theaters."""
    global _default_loader
    if _default_loader is None or (falcon_bms_root and falcon_bms_root != _default_loader.falcon_bms_root):
        _default_loader = TheaterConfigLoader(falcon_bms_root)
    return _default_loader.get_available_theaters()
