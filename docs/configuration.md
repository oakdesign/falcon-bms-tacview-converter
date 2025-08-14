# Configuration

The Falcon BMS Tacview Airbase Converter uses an intelligent, unified configuration system that automatically discovers theater configurations from your Falcon BMS installation. **No manual configuration is required for most users!**

## How Configuration Works

The system uses a **smart fallback approach**:

1. **Primary**: Automatically reads theater configuration from your BMS installation files
   - `Data/TerrData/TheaterDefinition/Theater.lst` - Lists available theaters
   - Individual `.tdf` (Theater Definition Files) - Theater metadata and paths
   - `Theater.txt` files - Coordinate system parameters

2. **Fallback**: Uses built-in static configuration when BMS files are unavailable

## Automatic Theater Discovery

The system automatically discovers theaters by:

1. **Reading Theater.lst**: Scans your BMS installation's theater list
2. **Parsing .tdf Files**: Extracts theater names, directories, and settings
3. **Loading Theater.txt**: Gets coordinate system and projection data
4. **Smart Merging**: Combines all sources into complete configuration

### Example Discovered Theaters

When you run the tool, it might discover theaters like:
- `korea_kto` - Korea KTO (from Korea KTO.tdf)
- `balkans` - Balkans (from Balkans.tdf) 
- `israel` - Israel (static fallback)
- `falcon` - Falcon (static fallback)

## Manual Configuration (Advanced)

### Setting BMS Installation Path

If the tool can't find your BMS installation automatically, you can specify it:

```python
from theater_config import set_falcon_bms_root
set_falcon_bms_root("/path/to/your/falcon/bms")
```

### Checking Available Theaters

```python
from theater_config import get_available_theaters, get_theater_config

# List all discovered theaters
theaters = get_available_theaters()
print("Available theaters:", theaters)

# Get configuration for a specific theater
config = get_theater_config('korea_kto')
print("Theater name:", config['name'])
print("Campaign dir:", config['campaign_subdir'])
```

### Static Configuration Override

For advanced users who need to override or add theaters, you can modify `theater_data.py`:

```python
# In theater_data.py
STATIC_THEATER_CONFIGS = {
    'my_custom_theater': {
        'name': 'My Custom Theater',
        'projection_string': "+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs",
        'center_lat': 50.0,
        'center_lon': 10.0,
        'utm_zone': 33,
        'utm_hemisphere': 'north',
        'campaign_subdir': 'My Custom Campaign',
        'terrain_subdir': 'My Custom Theater/TerrData',
        'heightmap_file': 'HeightMaps/HeightMap.raw',
        'heightmap_size': (1024, 1024),
        'heightmap_bounds': {
            'min_x': 0, 'max_x': 2097152,
            'min_y': 0, 'max_y': 2097152
        }
    }
}
```

## Configuration File Structure

### Theater Definition Files (.tdf)

The system reads these BMS files to discover theaters:

```
# Example Balkans.tdf content
name Balkans
desc Balkans Theater BMS 4.38.0
campaigndir Add-On Balkans\Campaign
terraindir Add-On Balkans\Terrdata\Balkans
artdir Add-On Balkans
objectdir Add-On Balkans\Terrdata\objects
sounddir Add-On Balkans\Sounds
```

### Theater.txt Files

Coordinate system parameters:

```
# Example Theater.txt content
CenterLat 41.8327
CenterLong 16.4191
TheaterSizeMeters 1024000
HeightmapSize 32768
```

## Migration from Old config.py

If you were using the old `config.py` system:

- ✅ **No action required** - The new system includes all previous theaters as fallbacks
- ✅ **Automatic discovery** - New theaters are found automatically
- ✅ **Better accuracy** - Uses actual BMS configuration files
- ✅ **Future-proof** - Works with new theater add-ons automatically

## Troubleshooting

### Theater Not Found
```bash
# List available theaters
python falcon_toolset.py theaters

# Check if BMS installation is detected
python -c "from theater_config import is_bms_installation_available; print('BMS detected:', is_bms_installation_available())"
```

### Custom BMS Path
```python
# Set custom BMS installation path
from theater_config import set_falcon_bms_root
set_falcon_bms_root("C:/Games/Falcon BMS 4.38")
```

The new configuration system makes the tool much more robust and user-friendly by automatically adapting to your BMS installation!