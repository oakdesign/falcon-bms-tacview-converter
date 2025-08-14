# Falcon BMS Tacview Converter

A comprehensive toolset for extracting airbase and runway data from Falcon BMS and converting coordinates between game coordinates and real-world latitude/longitude. Features **automatic theater discovery**, intelligent configuration management, elevation lookup from terrain heightmaps, and Tacview XML generation.

## 🚀 Key Features

- **🎯 Zero Configuration** - Automatically discovers theaters from your BMS installation
- **🌍 Multi-theater Support** - Korea, Balkans, Israel, Falcon + any custom add-ons
- **📐 High-Precision Conversion** - Game coordinates ↔ Lat/Lon with <±5m accuracy
- **🗻 Elevation Lookup** - Extract elevation data from terrain heightmaps  
- **📊 Tacview XML Export** - Generate Tacview-compatible airbase and runway data
- **💻 Command-line Interface** - Easy-to-use CLI for coordinate conversion
- **🔧 Smart Fallback** - Works even without BMS installation (static config)
- **🧩 Modular Design** - Clean, maintainable codebase

## 📦 Installation

1. **Install Python 3.7 or later**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **That's it!** No configuration needed - the tool automatically finds your BMS installation

## 🎮 Usage

### Theater Discovery

The tool automatically discovers theaters from your Falcon BMS installation:

```bash
# List all available theaters (discovered + static)
python src/falcon_toolset.py theaters

# Example output:
# Available Theaters:
# ========================================
# korea_kto  - Korea KTO       (Center: 38.5, 127.5, UTM Zone 52)
# balkans    - Balkans         (Center: 41.8327, 16.4191, UTM Zone 34)
# israel     - Israel          (Center: 31.5, 35.0, UTM Zone 36)
# falcon     - Falcon          (Center: 41.0, 15.0, UTM Zone 33)
```

### Coordinate Conversion

```bash
# Basic coordinate conversion with elevation
python src/falcon_toolset.py convert 1417055 736872 --theater korea_kto --elevation

# Reverse conversion (lat/lon to game coordinates)
python src/falcon_toolset.py convert 37.5 127.0 --reverse --unit meters --theater korea_kto

# Show map corners for a theater
python src/falcon_toolset.py corners --theater korea_kto
```

#### 🛠️ Conversion Options

- `--theater THEATER`: Theater to use (automatically discovered from your BMS installation)
- `--elevation`: Include elevation lookup from heightmaps
- `--reverse`: Convert from lat/lon to game coordinates
- `--unit UNIT`: Output unit for game coordinates (`feet`/`meters`)
- `--dms`: Include degrees/minutes/seconds format

### Tacview XML Export

Generate Tacview-compatible XML files with airbase and runway data:

```bash
# Export default theater
python src/eval_airbases_to_tacview_final.py

# Export specific theater
python src/eval_airbases_to_tacview_final.py korea_kto

# Export with debug information
python src/eval_airbases_to_tacview_final.py korea_kto --debug
```

## 🏗️ System Architecture

### Intelligent Configuration System

The tool uses a **smart configuration hierarchy**:

1. **🎯 Primary**: Reads from your BMS installation
   - `Data/TerrData/TheaterDefinition/Theater.lst` - Available theaters
   - Individual `.tdf` files - Theater metadata and paths
   - `Theater.txt` files - Coordinate system parameters

2. **🔄 Fallback**: Uses built-in static configuration when BMS files unavailable

### File Structure

```
falcon-bms-tacview-converter/
├── src/
│   ├── theater_config.py                   # 🧠 Unified configuration system
│   ├── theater_data.py                     # 📊 Static fallback data
│   ├── falcon_toolset.py                   # 💻 Coordinate conversion CLI
│   ├── eval_airbases_to_tacview_final.py   # 📈 Tacview export script
│   └── utils/
│       ├── coordinate_converter.py         # ⚙️ Core conversion logic
│       └── file_parser.py                  # 📄 BMS file parsing
├── docs/
│   └── configuration.md                    # 📖 Configuration guide
├── requirements.txt                        # 📦 Python dependencies
└── README.md                              # 📘 This file
```

## 📋 Examples

### Real-World Usage Examples

```bash
# Convert Kunsan AB coordinates with elevation
python src/falcon_toolset.py convert 1417055 736872 --theater korea_kto --elevation --dms

# Output:
# 🗺️ Converting game coordinates with elevation:
#    Input: 1,417,055, 736,872 (feet)
#    Latitude: 35.906333° (35.9° 54.3800')
#    Longitude: 126.612523° (126.6° 36.7514')
#    Elevation: 22 ft / 6.7 m
#    DMS: 35° 54' 22.80", 126° 36' 45.08"

# Reverse conversion - find game coordinates for Seoul
python src/falcon_toolset.py convert 37.5665 126.9780 --reverse --theater korea_kto

# Output:
# 🌍 Converting lat/lon to game coordinates:
#    Input: 37.566500°, 126.978000°
#    Latitude: 37.566500° (37.6° 33.9900')
#    Longitude: 126.978000° (126.0° 58.6800')
```

### Map Corners

```bash
python src/falcon_toolset.py corners --theater korea_kto

# Output:
# ============================================================
# MAP CORNER COORDINATES - KOREA KTO
# ============================================================
# 
# 🗺️  SW CORNER (0, 0)
# ----------------------------------------
# Latitude (decimal):     33.123456°
# Longitude (decimal):    124.567890°
# Game coordinates:       0.0, 0.0 (feet)
# DMS format:             33° 7' 24.44", 124° 34' 4.40"
```

## 🔧 Advanced Configuration

### Custom BMS Installation Path

If the tool can't find your BMS installation automatically:

```python
from theater_config import set_falcon_bms_root
set_falcon_bms_root("C:/Games/Falcon BMS 4.38")
```

### Check System Status

```python
from theater_config import is_bms_installation_available, get_available_theaters

# Check if BMS installation is detected
print("BMS detected:", is_bms_installation_available())

# List discovered theaters
theaters = get_available_theaters()
print("Available theaters:", theaters)
```

## 🎯 Accuracy & Precision

- **Coordinate Conversion**: <±5 meter accuracy using Karney's algorithm
- **Elevation Data**: Direct from BMS terrain heightmaps
- **Projection System**: Accurate UTM/Transverse Mercator projections
- **Theater Data**: Sourced directly from BMS installation files

## 🚨 Error Handling

The system uses **modern exception-based error handling**:

```bash
# Example error messages
python src/falcon_toolset.py convert 1417055 736872 --theater korea_kto --elevation

# Possible elevation messages:
#    Elevation: 22 ft / 6.7 m                    # ✅ Success
#    Elevation: Heightmap file not found         # ⚠️ Missing heightmap
#    Elevation: Coordinates outside valid range  # ⚠️ Out of bounds
#    Elevation: Error reading heightmap data     # ⚠️ File error
```

## 📊 Output Formats

### Tacview XML Output

The tool generates XML files containing:
- **Airport objects** with accurate ICAO codes and positions
- **Runway objects** as 3D blue rectangles with proper dimensions  
- **Elevation data** from terrain heightmaps
- **Theater-specific** coordinate systems and projections

## 🧪 Development

### Running in Debug Mode

```bash
# Debug coordinate conversion
python src/falcon_toolset.py convert 1500000 2000000 --theater korea_kto --elevation --dms

# Debug Tacview export
python src/eval_airbases_to_tacview_final.py korea_kto --debug
```

### Testing Theater Discovery

```bash
# Test automatic theater detection
python -c "
from theater_config import get_available_theaters, get_theater_config
print('Discovered theaters:', get_available_theaters())
for theater in get_available_theaters()[:2]:  # Test first 2
    config = get_theater_config(theater)
    print(f'{theater}: {config.get(\"name\")} - {config.get(\"center_lat\")}, {config.get(\"center_lon\")}')
"
```

## 🎖️ What's New

### Recent Improvements

- **✅ Automatic Theater Discovery** - No more manual configuration
- **✅ Dynamic TDF Parsing** - Reads real BMS theater definition files  
- **✅ Smart Fallback System** - Works with or without BMS installation
- **✅ Modern Exception Handling** - Clear error messages, no magic numbers
- **✅ Clean Architecture** - Separated data from business logic
- **✅ Updated Documentation** - Reflects current capabilities

### Migration from Old Versions

- **No action required!** The new system includes all previous theaters as fallbacks
- **Better accuracy** using actual BMS configuration files
- **Future-proof** - automatically detects new theater add-ons

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions are welcome! Please submit pull requests with:
- Clear descriptions of changes
- Test cases for new features  
- Updated documentation

## 📚 Documentation

- **[Configuration Guide](docs/configuration.md)** - Detailed configuration information
- **[Migration Guide](CONFIG_MIGRATION.md)** - System architecture changes