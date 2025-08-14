"""
Unified theater configuration module for Falcon BMS.

This module provides a single interface for theater configuration that:
1. First tries to load configuration from BMS installation files (theater.txt, .tdf files)
2. Falls back to static configuration data if BMS files are not available
3. Provides consistent API regardless of data source

Usage:
    from theater_config import get_theater_config, get_available_theaters, get_theater_paths
    
    config = get_theater_config('korea')
    theaters = get_available_theaters()
    paths = get_theater_paths('korea')
"""

import os
import re
from typing import Dict, Optional, List, Tuple, Union

from theater_data import STATIC_THEATER_CONFIGS, DEFAULT_FALCON_BMS_ROOT


class TheaterConfigManager:
    """Unified theater configuration manager."""
    
    def __init__(self, falcon_bms_root: str = None):
        """Initialize with optional Falcon BMS root directory."""
        self.falcon_bms_root = falcon_bms_root or DEFAULT_FALCON_BMS_ROOT
        self._theater_cache = {}
        self._bms_available = None
    
    def is_bms_installation_available(self) -> bool:
        """Check if a valid BMS installation is available."""
        if self._bms_available is None:
            self._bms_available = (
                os.path.exists(self.falcon_bms_root) and
                os.path.exists(os.path.join(self.falcon_bms_root, 'Data'))
            )
        return self._bms_available
    
    def get_available_theaters(self) -> List[str]:
        """Get list of available theaters from BMS files and static config."""
        theaters = set()
        
        # Try to read from BMS theater.lst if available
        if self.is_bms_installation_available():
            try:
                theater_lst_path = os.path.join(
                    self.falcon_bms_root, 
                    'Data', 'TerrData', 'TheaterDefinition', 'Theater.lst'
                )
                if os.path.exists(theater_lst_path):
                    with open(theater_lst_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                theater_info = self._parse_tdf_reference(line)
                                if theater_info:
                                    theaters.add(theater_info['key'])
            except Exception:
                pass  # Silent fallback to static config
        
        # Add theaters from static config
        theaters.update(STATIC_THEATER_CONFIGS.keys())
        
        return sorted(list(theaters))
    
    def get_theater_config(self, theater_name: str) -> Dict:
        """Get complete theater configuration, preferring BMS files over static."""
        theater_name = theater_name.lower()
        
        # Return cached config if available
        if theater_name in self._theater_cache:
            return self._theater_cache[theater_name]
        
        # Try to load from BMS files first
        if self.is_bms_installation_available():
            try:
                config = self._load_theater_from_bms_files(theater_name)
                if config:
                    self._theater_cache[theater_name] = config
                    return config
            except Exception:
                pass  # Fall through to static config
        
        # Fallback to static configuration
        if theater_name in STATIC_THEATER_CONFIGS:
            config = STATIC_THEATER_CONFIGS[theater_name].copy()
            self._theater_cache[theater_name] = config
            return config
        
        raise ValueError(f"Theater '{theater_name}' not found in BMS files or static config")
    
    def get_theater_paths(self, theater_name: str) -> Dict[str, str]:
        """Get file paths for a specific theater."""
        config = self.get_theater_config(theater_name)
        base_path = self.falcon_bms_root
        
        paths = {
            'campaign_data': os.path.join(base_path, 'Data', config['campaign_subdir'], 'CampObjData.XML'),
            'stations_data': os.path.join(base_path, 'Data', config['campaign_subdir'], 'Stations+Ils.dat'),
            'falcon_ct': os.path.join(base_path, 'Data', 'TerrData', 'Objects', 'Falcon4_CT.xml'),
            'objective_data': os.path.join(base_path, 'Data', 'TerrData', 'Objects', 'ObjectiveRelatedData'),
            'heightmap': os.path.join(base_path, 'Data', config['terrain_subdir'], config['heightmap_file'])
        }
        
        return paths
    
    def _parse_tdf_reference(self, tdf_path: str) -> Optional[Dict]:
        """Parse TDF file reference from theater.lst and extract theater info."""
        try:
            # Build full path to TDF file
            full_tdf_path = os.path.join(self.falcon_bms_root, 'Data', tdf_path.replace('\\', os.sep))
            
            if not os.path.exists(full_tdf_path):
                return None
            
            # Parse the TDF file
            tdf_config = self._parse_tdf_file(full_tdf_path)
            if not tdf_config:
                return None
            
            # Generate a key from the theater name
            theater_name = tdf_config.get('name', '')
            if theater_name:
                # Create a normalized key from the theater name
                theater_key = re.sub(r'[^a-z0-9]+', '_', theater_name.lower()).strip('_')
            else:
                # Fallback: extract from filename
                filename = os.path.basename(full_tdf_path)
                theater_key = os.path.splitext(filename)[0].lower().replace(' ', '_')
            
            return {
                'key': theater_key,
                'config': tdf_config,
                'tdf_path': full_tdf_path
            }
            
        except Exception:
            return None
    
    def _parse_tdf_file(self, tdf_file_path: str) -> Optional[Dict]:
        """Parse a .tdf theater definition file."""
        try:
            with open(tdf_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            config = {}
            
            # Parse key-value pairs from TDF file
            patterns = {
                'name': r'^name\s+(.+)$',
                'desc': r'^desc\s+(.+)$',
                'bitmap': r'^bitmap\s+(.+)$',
                'campaigndir': r'^campaigndir\s+(.+)$',
                'terraindir': r'^terraindir\s+(.+)$',
                'tileset': r'^tileset\s+(.+)$',
                'artdir': r'^artdir\s+(.+)$',
                'cockpitdir': r'^cockpitdir\s+(.+)$',
                'moviedir': r'^moviedir\s+(.+)$',
                'objectdir': r'^objectdir\s+(.+)$',
                '3ddatadir': r'^3ddatadir\s+(.+)$',
                'sounddir': r'^sounddir\s+(.+)$',
                'tacrefdir': r'^tacrefdir\s+(.+)$',
                'simdatadir': r'^simdatadir\s+(.+)$',
                'subtitlesdir': r'^subtitlesdir\s+(.+)$',
                'splashdir': r'^splashdir\s+(.+)$',
                'doubleres2dmap': r'^doubleres2dmap\s+(\d+)$',
                'magneticdeclination': r'^magneticdeclination\s+([+-]?\d+\.?\d*)$'
            }
            
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                for key, pattern in patterns.items():
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if key in ['doubleres2dmap']:
                            config[key] = int(value)
                        elif key in ['magneticdeclination']:
                            config[key] = float(value)
                        else:
                            config[key] = value
                        break
            
            return config if config else None
            
        except Exception:
            return None
    
    def _load_theater_from_bms_files(self, theater_name: str) -> Optional[Dict]:
        """Load theater configuration from BMS installation files."""
        # First, try to find TDF file for this theater
        tdf_config = self._find_tdf_config_for_theater(theater_name)
        if not tdf_config:
            return None
        
        # Try to find and parse theater.txt file
        theater_txt_config = None
        theater_txt_path = self._find_theater_txt_path_from_tdf(tdf_config)
        if theater_txt_path:
            theater_txt_config = self._parse_theater_txt(theater_txt_path)
        
        # Combine TDF and theater.txt configs
        config = tdf_config.copy()
        if theater_txt_config:
            config.update(theater_txt_config)
        
        # Add additional fields from static config if needed
        self._enhance_config_from_static(config, theater_name)
        
        return config
    
    def _find_tdf_config_for_theater(self, theater_name: str) -> Optional[Dict]:
        """Find TDF configuration for the given theater name."""
        if not self.is_bms_installation_available():
            return None
        
        try:
            theater_lst_path = os.path.join(
                self.falcon_bms_root, 
                'Data', 'TerrData', 'TheaterDefinition', 'Theater.lst'
            )
            
            if not os.path.exists(theater_lst_path):
                return None
            
            with open(theater_lst_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        theater_info = self._parse_tdf_reference(line)
                        if theater_info and theater_info['key'] == theater_name:
                            return theater_info['config']
            
        except Exception:
            pass
        
        return None
    
    def _find_theater_txt_path_from_tdf(self, tdf_config: Dict) -> Optional[str]:
        """Find theater.txt path using TDF configuration."""
        terrain_dir = tdf_config.get('terraindir')
        if not terrain_dir:
            return None
        
        # Try common theater.txt locations within the terrain directory
        search_paths = [
            os.path.join(self.falcon_bms_root, 'Data', terrain_dir, 'Theater.txt'),
            os.path.join(self.falcon_bms_root, 'Data', terrain_dir, 'NewTerrain', 'Theater.txt')
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _find_theater_txt_path(self, theater_name: str) -> Optional[str]:
        """Find theater.txt file for the given theater."""
        # Common theater.txt locations based on theater name
        search_paths = []
        
        if theater_name == 'korea':
            search_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'TerrData', 'Korea', 'NewTerrain', 'Theater.txt'),
                os.path.join(self.falcon_bms_root, 'Data', 'TerrData', 'Korea', 'Theater.txt')
            ]
        elif theater_name == 'balkans':
            search_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Balkans', 'TerrData', 'Balkans', 'Theater.txt'),
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Balkans', 'TerrData', 'Balkans', 'NewTerrain', 'Theater.txt')
            ]
        elif theater_name == 'israel':
            search_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Israel', 'TerrData', 'Israel', 'Theater.txt'),
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Israel', 'TerrData', 'Israel', 'NewTerrain', 'Theater.txt')
            ]
        elif theater_name == 'falcon':
            search_paths = [
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Falcon', 'TerrData', 'Falcon', 'Theater.txt'),
                os.path.join(self.falcon_bms_root, 'Data', 'Add-On Falcon', 'TerrData', 'Falcon', 'NewTerrain', 'Theater.txt')
            ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _parse_theater_txt(self, theater_txt_path: str) -> Optional[Dict]:
        """Parse theater.txt file and extract configuration."""
        try:
            with open(theater_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            config = {}
            
            # Extract key-value pairs
            patterns = {
                'center_lat': r'CenterLat\s+([+-]?\d+\.?\d*)',
                'center_lon': r'CenterLong\s+([+-]?\d+\.?\d*)',
                'theater_size_meters': r'TheaterSizeMeters\s+(\d+)',
                'heightmap_size': r'HeightmapSize\s+(\d+)',
                'meter_res': r'MeterRes\s+([+-]?\d+\.?\d*)',
                'grid_to_ft': r'GridToFt\s+([+-]?\d+\.?\d*)',
                'ft_to_grid': r'FtToGrid\s+([+-]?\d+\.?\d*)',
                'grid_offset': r'GridOffset\s+([+-]?\d+\.?\d*)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    if key in ['center_lat', 'center_lon', 'meter_res', 'grid_to_ft', 'ft_to_grid', 'grid_offset']:
                        config[key] = float(value)
                    else:
                        config[key] = int(value)
            
            # Create projection string if we have center coordinates
            if 'center_lat' in config and 'center_lon' in config:
                config['projection_string'] = self._create_projection_string(
                    config['center_lat'], config['center_lon']
                )
            
            return config if config else None
            
        except Exception:
            return None
    
    def _create_projection_string(self, center_lat: float, center_lon: float) -> str:
        """Create projection string for given center coordinates."""
        # This is a simplified version - you may want to use the more sophisticated
        # logic from your coordinate_converter.py if needed
        from utils.coordinate_converter import create_proj_string
        
        try:
            y_0 = create_proj_string(center_lat, center_lon, 512000)
            return f"+proj=tmerc +lon_0={center_lon} +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0={y_0:.5e}"
        except Exception:
            # Fallback to simple UTM projection
            utm_zone = int((center_lon + 180) / 6) + 1
            hemisphere = 'north' if center_lat >= 0 else 'south'
            return f"+proj=utm +zone={utm_zone} +datum=WGS84 +units=m +no_defs"
    
    def _enhance_config_from_static(self, config: Dict, theater_name: str) -> None:
        """Enhance dynamic config with additional data from static config."""
        if theater_name in STATIC_THEATER_CONFIGS:
            static_config = STATIC_THEATER_CONFIGS[theater_name]
            
            # Add missing fields from static config
            for key, value in static_config.items():
                if key not in config:
                    config[key] = value
        
        # Convert TDF paths to standard config format
        if 'campaigndir' in config and 'campaign_subdir' not in config:
            config['campaign_subdir'] = config['campaigndir']
        
        if 'terraindir' in config and 'terrain_subdir' not in config:
            config['terrain_subdir'] = config['terraindir']
        
        # Ensure we have required paths for heightmap
        if 'terrain_subdir' in config and 'heightmap_file' not in config:
            config['heightmap_file'] = 'HeightMaps/HeightMap.raw'
        
        # Ensure we have a name
        if 'name' not in config:
            config['name'] = theater_name.title()
        
        # Set default heightmap properties if not present
        if 'heightmap_size' not in config:
            config['heightmap_size'] = (32768, 32768)  # Default size
        
        if 'heightmap_bounds' not in config:
            config['heightmap_bounds'] = {
                'min_x': 0, 'max_x': 3358699.5,
                'min_y': 0, 'max_y': 3358699.5
            }
        
        # Ensure we have coordinate system data - use static fallback for known theaters
        if 'projection_string' not in config or 'center_lat' not in config or 'center_lon' not in config:
            # Try to match with known static theaters
            for static_key, static_config in STATIC_THEATER_CONFIGS.items():
                if (theater_name == static_key or 
                    config.get('name', '').lower() in static_config.get('name', '').lower() or
                    static_config.get('name', '').lower() in config.get('name', '').lower()):
                    
                    # Copy missing coordinate data from static config
                    for coord_key in ['projection_string', 'center_lat', 'center_lon', 'utm_zone', 'utm_hemisphere']:
                        if coord_key not in config and coord_key in static_config:
                            config[coord_key] = static_config[coord_key]
                    break


# Global instance
_config_manager = TheaterConfigManager()

# Public API functions
def get_theater_config(theater_name: str) -> Dict:
    """Get theater configuration for the specified theater."""
    return _config_manager.get_theater_config(theater_name)

def get_available_theaters() -> List[str]:
    """Get list of available theaters."""
    return _config_manager.get_available_theaters()

def get_theater_paths(theater_name: str) -> Dict[str, str]:
    """Get file paths for the specified theater."""
    return _config_manager.get_theater_paths(theater_name)

def set_falcon_bms_root(path: str) -> None:
    """Set the Falcon BMS root directory and clear cache."""
    global _config_manager
    _config_manager = TheaterConfigManager(path)

def is_bms_installation_available() -> bool:
    """Check if BMS installation is available."""
    return _config_manager.is_bms_installation_available()

# Legacy compatibility - expose static configs if needed
THEATER_CONFIGS = STATIC_THEATER_CONFIGS
FALCON_BMS_ROOT = DEFAULT_FALCON_BMS_ROOT
