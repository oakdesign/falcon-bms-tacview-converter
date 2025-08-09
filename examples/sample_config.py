# Sample configuration for Falcon BMS Tacview Airbase Converter

# This is an example configuration file for the Falcon BMS Tacview Airbase Converter.
# Modify the values below to match your Falcon BMS installation and desired settings.

THEATER_CONFIGS = {
    'korea': {
        'name': "Korea Theater",
        'folder_path': "",  # Empty string for default Korea
        'projection_string': "+proj=utm +zone=52 +datum=WGS84 +units=m +no_defs",
        'camp_w': 3358699.5,  # Campaign width
        'camp_h': 3358699.5,  # Campaign height
        'heightmap_subpath': "Korea/NewTerrain/HeightMaps/HeightMap.raw"
    },
    'balkans': {
        'name': "Balkans Theater",
        'folder_path': "Add-On Balkans",
        'projection_string': "+proj=utm +zone=34 +datum=WGS84 +units=m +no_defs",
        'camp_w': 3000000.0,  # Adjust as necessary
        'camp_h': 3000000.0,  # Adjust as necessary
        'heightmap_subpath': "Balkans/NewTerrain/HeightMaps/HeightMap.raw"
    },
    # Add additional theaters as needed
}