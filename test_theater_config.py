#!/usr/bin/env python3
"""
Test script for the new theater configuration system
"""
import sys
import os

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

from theater_config import get_theater_config, get_available_theaters
from utils.coordinate_converter import CoordinateConverter

def test_theater_config_loading():
    """Test the new theater configuration loading system."""
    print("Testing Theater Configuration Loader")
    print("=" * 50)
    
    # Test getting available theaters
    print("\n1. Getting available theaters:")
    try:
        theaters = get_available_theaters()
        print(f"   Found theaters: {theaters}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test loading Korea theater config
    print("\n2. Loading Korea theater config:")
    try:
        korea_config = get_theater_config('korea')
        print(f"   Name: {korea_config.get('name')}")
        print(f"   Center: {korea_config.get('center_lat')}, {korea_config.get('center_lon')}")
        print(f"   Theater size: {korea_config.get('theater_size_km')} km")
        print(f"   Heightmap size: {korea_config.get('heightmap_size')}")
        print(f"   Projection: {korea_config.get('projection_string')}")
        print(f"   Config keys: {list(korea_config.keys())}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test coordinate conversion with new system
    print("\n3. Testing coordinate conversion:")
    try:
        converter = CoordinateConverter(theater_name='korea')
        
        # Test converting a known point
        test_x, test_y = 1000000, 1000000  # feet
        lat, lon = converter.game_to_latlon_grid_karney(test_x, test_y, from_feet=True)
        
        print(f"   Game coords: {test_x}, {test_y} (feet)")
        print(f"   Lat/Lon: {lat:.6f}, {lon:.6f}")
        
        # Test reverse conversion
        reverse_x, reverse_y = converter.latlon_to_game(lat, lon, to_feet=True)
        print(f"   Reverse: {reverse_x:.1f}, {reverse_y:.1f} (feet)")
        
        # Check accuracy
        diff_x = abs(test_x - reverse_x)
        diff_y = abs(test_y - reverse_y)
        print(f"   Accuracy: ±{diff_x:.1f}, ±{diff_y:.1f} feet")
        
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_theater_config_loading()
    sys.exit(0 if success else 1)
