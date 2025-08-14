"""
Configuration System Migration Summary
=====================================

This document summarizes the refactoring of the theater configuration system
to create a unified, clean architecture.

## Changes Made

### 1. Created Unified Architecture

**New Files:**
- `theater_data.py`: Pure data file with static theater configurations (no business logic)
- `theater_config.py`: Unified configuration manager with smart fallback logic

**Architecture Flow:**
1. **First Priority**: Try to load from BMS installation files (theater.txt, .tdf files)
2. **Fallback**: Use static configuration data from theater_data.py
3. **Single API**: Consistent interface regardless of data source

### 2. Migration Details

**Before:**
- `config.py`: Mixed data and business logic
- `utils/theater_config_loader.py`: Separate dynamic loading logic
- Duplicate imports and inconsistent APIs

**After:**
- `theater_data.py`: Clean separation of static data
- `theater_config.py`: Single point of configuration with intelligent fallback
- All modules now use the same unified API

### 3. Updated Files

**Core Files:**
- `falcon_toolset.py`: Updated to use unified config API
- `utils/coordinate_converter.py`: Updated to use new theater_config module
- `eval_airbases_to_tacview_final.py`: Updated imports
- `test_theater_config.py`: Updated to use new API

**Legacy Files (can be removed):**
- `config.py`: No longer needed, functionality moved to theater_config.py
- `utils/theater_config_loader.py`: Replaced by theater_config.py

## API Usage

### Simple Usage (Recommended)
```python
from theater_config import get_theater_config, get_available_theaters, get_theater_paths

# Get all available theaters
theaters = get_available_theaters()

# Get configuration for a specific theater (auto-detects BMS vs static)
config = get_theater_config('korea')

# Get file paths for a theater
paths = get_theater_paths('korea')
```

### Advanced Usage
```python
from theater_config import set_falcon_bms_root, is_bms_installation_available

# Override BMS installation path
set_falcon_bms_root('/path/to/falcon/bms')

# Check if BMS installation is available
if is_bms_installation_available():
    print("Using BMS files")
else:
    print("Using static fallback")
```

## Benefits

1. **Clean Separation**: Data separated from business logic
2. **Smart Fallback**: Automatically uses BMS files when available, static config otherwise  
3. **Single API**: One consistent interface for all configuration needs
4. **Maintainable**: Easy to modify static data without touching business logic
5. **Robust**: Graceful degradation when BMS installation is not available

## Configuration Sources

### Dynamic (BMS Files) - Priority 1
- `Data/TerrData/TheaterDefinition/Theater.lst`: List of available theaters
- `Data/TerrData/Korea/NewTerrain/Theater.txt`: Korea theater configuration
- `Data/Add-On */TerrData/*/Theater.txt`: Add-on theater configurations

### Static (Fallback) - Priority 2
- `theater_data.py`: Hard-coded theater configurations
- Used when BMS installation is not found or files cannot be read

## Migration Notes

- All existing code should work without changes
- Legacy `THEATER_CONFIGS` import still available for compatibility
- Old config.py can be safely removed after verifying no other dependencies
- theater_config_loader.py can be removed as functionality is now in theater_config.py

## Testing

The system has been tested with:
- Theater listing (`python falcon_toolset.py theaters`)
- Coordinate conversion (`python falcon_toolset.py convert ...`)
- BMS detection and fallback behavior
- All functionality works correctly with both BMS files and static fallback
"""
