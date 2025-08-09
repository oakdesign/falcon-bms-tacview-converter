# Falcon BMS Tacview Converter

A comprehensive toolset for extracting airbase and runway data from Falcon BMS and converting coordinates between game coordinates and real-world latitude/longitude. Includes elevation lookup from terrain heightmaps and Tacview XML generation for multiple theaters.

## Features

- **Multi-theater support** - Korea, Balkans, Israel, Falcon add-on theaters
- **Coordinate conversion** - Game coordinates ↔ Lat/Lon with UTM projection
- **Elevation lookup** - Extract elevation data from terrain heightmaps  
- **Tacview XML export** - Generate Tacview-compatible airbase and runway data
- **Command-line interface** - Easy-to-use CLI for coordinate conversion
- **Modular design** - Extensible codebase with clear separation of concerns

## Installation

1. Install Python 3.7 or later
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your Falcon BMS path in `src/config.py`

## Usage

### Coordinate Conversion Toolset

The `falcon_toolset.py` script provides comprehensive coordinate conversion capabilities:

```bash
# Basic coordinate conversion
python src/falcon_toolset.py convert <x> <y> [options]

# Display map corners for a theater
python src/falcon_toolset.py corners [options]

# List available theaters
python src/falcon_toolset.py theaters
```

#### Conversion Options

- `--theater THEATER`: Specify theater (korea, balkans, israel, falcon)
- `--elevation`: Include elevation lookup from heightmaps
- `--reverse`: Convert from lat/lon to game coordinates
- `--unit UNIT`: Output unit for game coordinates (feet/meters)
- `--dms`: Include degrees/minutes/seconds format

### Tacview XML Export

Generate a Tacview-compatible XML file with airbase and runway data:

```bash
# Export default theater (Korea)
python src/eval_airbases_to_tacview_final.py

# Export specific theater
python src/eval_airbases_to_tacview_final.py israel

# Export with debug information
python src/eval_airbases_to_tacview_final.py korea --debug
```

## Available Theaters

- `korea` - Default Korea theater (UTM Zone 52)
- `balkans` - Balkans add-on theater (UTM Zone 34)
- `israel` - Israel add-on theater (UTM Zone 36)  
- `falcon` - Falcon add-on theater (UTM Zone 33)

## File Structure

```
falcon-bms-tacview-converter/
├── src/
│   ├── config.py                           # Configuration settings
│   ├── eval_airbases_to_tacview_final.py   # Main Tacview export script
│   ├── falcon_toolset.py                   # Coordinate conversion CLI
│   └── utils/
│       ├── __init__.py
│       ├── coordinate_converter.py         # Core conversion logic
│       └── file_parser.py                  # BMS file parsing
├── requirements.txt                        # Python dependencies
└── README.md                              # This file
```

## Examples

### Coordinate Conversion Examples

```bash
# Convert airbase coordinates to lat/lon with elevation
python src/falcon_toolset.py convert 1500000 2000000 --elevation --theater korea

# Output:
# 🗺️ Converting game coordinates with elevation:
#    Input: 1500000, 2000000 (feet)
#    Latitude: 37.123456° (37° 7.4074')
#    Longitude: 127.654321° (127° 39.2593')
#    Elevation: 245 ft / 74.7 m
#    DMS: 37° 7' 24.44", 127° 39' 15.56"

# Reverse conversion
python src/falcon_toolset.py convert 37.5 127.0 --reverse --unit meters

# Output:
# 🌍 Converting lat/lon to game coordinates:
#    Input: 37.500000°, 127.000000°
#    Output: 1234567.89, 987654.32 (meters)
#    Output (feet): 4050419.58, 3240338.58
```

### Map Corner Examples

```bash
python src/falcon_toolset.py corners --theater korea

# Output:
# ============================================================
# MAP CORNER COORDINATES - KOREA
# ============================================================
# 
# 🗺️  SW CORNER (0, 0)
# ----------------------------------------
# Latitude (decimal):     33.123456°
# Longitude (decimal):    124.567890°
# [... more coordinate formats ...]
```

## Configuration

Edit the `FALCON_BMS_ROOT` path in `src/config.py` to point to your Falcon BMS installation:

```python
FALCON_BMS_ROOT = r"E:\Spiele\Falcon BMS 4.38"
```

The tool automatically detects available theaters from your installation. You can also modify the `THEATER_CONFIGS` dictionary to add support for additional theaters.

## Error Codes

Elevation lookup may return error codes:
- `-999`: Heightmap file not found
- `-998`: Error reading heightmap file  
- `-997`: Coordinates outside valid range
- `-996`: File read error

## Output

The tool generates an XML file containing:
- Airport objects with accurate positions and ICAO codes
- Runway objects as 3D blue rectangles with proper dimensions
- Elevation data from terrain heightmaps

## Development

### Running in Debug Mode

For development in VS Code, you can run the tools with debug arguments:

```bash
# Debug coordinate conversion
python src/falcon_toolset.py convert 1500000 2000000 --theater korea --elevation --dms

# Debug Tacview export
python src/eval_airbases_to_tacview_final.py korea --debug
```

### Adding New Theaters

To add support for a new theater:

1. Add theater configuration to `THEATER_CONFIGS` in `src/config.py`
2. Specify the correct UTM zone and file paths
3. Test coordinate conversion with known reference points

### Heightmap Structure

Falcon BMS heightmaps are typically:
- 1024x1024 pixel raw files
- 16-bit unsigned integers (little endian)
- Covering the full theater area
- Y-axis flipped (0,0 = southwest corner)

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Contributions are welcome! Please submit pull requests with:
- Clear descriptions of changes
- Test cases for new features
- Updated documentation