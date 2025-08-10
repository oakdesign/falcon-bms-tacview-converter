"""
Configuration settings for Falcon BMS Tacview Converter
"""
import os

# Path to your Falcon BMS installation
# Path to your Falcon BMS installation
FALCON_BMS_ROOT = r"F:\Falcon BMS 4.38 (Internal)"

# Theater configuration with coordinate systems and heightmap info
THEATER_CONFIGS = {
    'korea': {
        'name': 'Korea',
        'projection_string': "+proj=tmerc +lon_0=127.5 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-3.74929e+06",
        'utm_zone': 52,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Campaign',
        'terrain_subdir': 'TerrData/Korea/NewTerrain',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (32768, 32768),  # width, height in pixels
        'heightmap_bounds': {  # in game coordinates (feet)
            'min_x': 0, 'max_x': 3358699.5,
            'min_y': 0, 'max_y': 3358699.5
        }
    },
    'balkans': {
        'name': 'Balkans',
        'projection_string': "Projection string=+proj=tmerc +lon_0=16.4191 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-4.1192e+06",
        'utm_zone': 34,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Add-On Balkans/Campaign',
        'terrain_subdir': 'Add-On Balkans/TerrData/Balkans',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (32768, 32768),
        'heightmap_bounds': {
            'min_x': 0, 'max_x': 3358699.5,
            'min_y': 0, 'max_y': 3358699.5
        }
    },
    'israel': {
        'name': 'Israel',
        'projection_string': "+proj=utm +zone=36 +datum=WGS84 +units=m +no_defs",
        'utm_zone': 36,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Add-On Israel/Campaign',
        'terrain_subdir': 'Add-On Israel/TerrData/Israel',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (1024, 1024),
        'heightmap_bounds': {
            'min_x': 0, 'max_x': 2097152,
            'min_y': 0, 'max_y': 2097152
        }
    },
    'falcon': {
        'name': 'Falcon',
        'projection_string': "+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs",
        'utm_zone': 33,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Add-On Falcon/Campaign',
        'terrain_subdir': 'Add-On Falcon/TerrData/Falcon',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (1024, 1024),
        'heightmap_bounds': {
            'min_x': 0, 'max_x': 2097152,
            'min_y': 0, 'max_y': 2097152
        }
    }
}

def get_theater_paths(theater_name):
    """Get file paths for a specific theater."""
    if theater_name not in THEATER_CONFIGS:
        raise ValueError(f"Unknown theater: {theater_name}")
    
    config = THEATER_CONFIGS[theater_name]
    base_path = FALCON_BMS_ROOT
    
    paths = {
        'campaign_data': os.path.join(base_path, 'Data', config['campaign_subdir'], 'CampObjData.XML'),
        'stations_data': os.path.join(base_path, 'Data', config['campaign_subdir'], 'Stations+Ils.dat'),
        'falcon_ct': os.path.join(base_path, 'Data', 'TerrData', 'Objects', 'Falcon4_CT.xml'),
        'objective_data': os.path.join(base_path, 'Data', 'TerrData', 'Objects', 'ObjectiveRelatedData'),
        'heightmap': os.path.join(base_path, 'Data', config['terrain_subdir'], config['heightmap_file'])
    }
    
    return paths

def get_available_theaters():
    """Get list of available theaters (those with existing campaign data)."""
    available = []
    for theater_name in THEATER_CONFIGS:
        try:
            paths = get_theater_paths(theater_name)
            if os.path.exists(paths['campaign_data']):
                available.append(theater_name)
        except Exception:
            continue
    return available