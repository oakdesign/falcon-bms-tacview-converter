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
                                theater_name = self._extract_theater_name_from_tdf_path(line)
                                if theater_name:
                                    theaters.add(theater_name.lower())
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
    
    def _extract_theater_name_from_tdf_path(self, tdf_path: str) -> Optional[str]:
        """Extract theater name from TDF file path."""
        tdf_path_lower = tdf_path.lower()
        
        if 'korea' in tdf_path_lower:
            return 'korea'
        elif 'balkan' in tdf_path_lower:
            return 'balkans'
        elif 'israel' in tdf_path_lower:
            return 'israel'
        elif 'falcon' in tdf_path_lower:
            return 'falcon'
        
        return None
    
    def _load_theater_from_bms_files(self, theater_name: str) -> Optional[Dict]:
        """Load theater configuration from BMS installation files."""
        theater_txt_path = self._find_theater_txt_path(theater_name)
        if not theater_txt_path:
            return None
        
        config = self._parse_theater_txt(theater_txt_path)
        if not config:
            return None
        
        # Add additional fields from static config or derived values
        self._enhance_config_from_static(config, theater_name)
        
        return config
    
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
            
            # Ensure we have a name
            if 'name' not in config:
                config['name'] = static_config.get('name', theater_name.title())


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
