"""
Static theater configuration data for Falcon BMS theaters.
This file contains fallback configuration data used when BMS installation
files are not available or cannot be read.
"""

# Default Falcon BMS installation path (can be overridden)
DEFAULT_FALCON_BMS_ROOT = r"F:\Falcon BMS 4.38 (Internal)"

# Static theater configurations (fallback data)
STATIC_THEATER_CONFIGS = {
    'korea': {
        'name': 'Korea',
        'projection_string': "+proj=tmerc +lon_0=127.5 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-3.74929e+06",
        'center_lat': 38.5,
        'center_lon': 127.5,
        'utm_zone': 52,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Campaign',
        'terrain_subdir': 'TerrData/Korea/NewTerrain',
        'object_subdir': 'TerrData/Objects',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (32768, 32768),  # width, height in pixels
        'heightmap_bounds': {  # in game coordinates (feet)
            'min_x': 0, 'max_x': 3358699.5,
            'min_y': 0, 'max_y': 3358699.5
        }
    },
    'balkans': {
        'name': 'Balkans',
        'projection_string': "+proj=tmerc +lon_0=16.4191 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-4.1192e+06",
        'center_lat': 41.8327,
        'center_lon': 16.4191,
        'utm_zone': 34,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Add-On Balkans/Campaign',
        'terrain_subdir': 'Add-On Balkans/TerrData/Balkans',
        'object_subdir': 'Add-On Balkans/TerrData/objects',
        'heightmap_file': 'NewTerrain/Heightmaps/Heightmap.raw',
        'heightmap_size': (32768, 32768),
        'heightmap_bounds': {
            'min_x': 0, 'max_x': 3358699.5,
            'min_y': 0, 'max_y': 3358699.5
        }
    },
    'israel': {
        'name': 'Israel',
        'projection_string': "+proj=utm +zone=36 +datum=WGS84 +units=m +no_defs",
        'center_lat': 31.5,
        'center_lon': 35.0,
        'utm_zone': 36,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Add-On Israel/Campaign',
        'terrain_subdir': 'Add-On Israel/TerrData/Israel',
        'object_subdir': 'Add-On Israel/TerrData/objects',
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
        'center_lat': 41.0,
        'center_lon': 15.0,
        'utm_zone': 33,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'Add-On Falcon/Campaign',
        'terrain_subdir': 'Add-On Falcon/TerrData/Falcon',
        'object_subdir': 'Add-On Falcon/TerrData/objects',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (1024, 1024),
        'heightmap_bounds': {
            'min_x': 0, 'max_x': 2097152,
            'min_y': 0, 'max_y': 2097152
        }
    }
}
