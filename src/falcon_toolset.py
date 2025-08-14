#!/usr/bin/env python3
"""
Falcon BMS Coordinate Conversion Toolset

A command-line utility for converting coordinates between Falcon BMS game coordinates
and real-world latitude/longitude, with elevation lookup capabilities.
"""

import argparse
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theater_config import get_theater_config, get_available_theaters, get_theater_paths, THEATER_CONFIGS
from utils.coordinate_converter import (CoordinateConverter, create_proj_string, 
                                      ElevationError, HeightmapNotFoundError, 
                                      CoordinatesOutOfBoundsError, HeightmapReadError)
from utils.file_parser import parse_stations_file

def format_coordinate_output(lat, lon, x=None, y=None, elevation=None, unit='feet', include_dms=False):
    """Format coordinate conversion output for display."""
    if x is not None and y is not None:
        print(f"🗺️ Converting game coordinates{'with elevation' if elevation is not None else ''}:")
        print(f"   Input: {x:,.0f}, {y:,.0f} ({unit})")
        print(f"   Latitude: {lat:.6f}° ({lat:.1f}° {abs(lat-int(lat))*60:.4f}')")
        print(f"   Longitude: {lon:.6f}° ({lon:.1f}° {abs(lon-int(lon))*60:.4f}')")
        
        if elevation is not None:
            elevation_m = elevation * 0.3048
            print(f"   Elevation: {elevation:.0f} ft / {elevation_m:.1f} m")
        
        if include_dms:
            lat_d = int(lat)
            lat_m = int(abs(lat - lat_d) * 60)
            lat_s = (abs(lat - lat_d) * 60 - lat_m) * 60
            
            lon_d = int(lon)
            lon_m = int(abs(lon - lon_d) * 60)
            lon_s = (abs(lon - lon_d) * 60 - lon_m) * 60
            
            print(f"   DMS: {lat_d}° {lat_m}' {lat_s:.2f}\", {lon_d}° {lon_m}' {lon_s:.2f}\"")
    else:
        print(f"🌍 Converting lat/lon to game coordinates:")
        print(f"   Input: {lat:.6f}°, {lon:.6f}°")
        if x is not None and y is not None:
            if unit == 'feet':
                x_m = x * 0.3048
                y_m = y * 0.3048
                print(f"   Output: {x:,.2f}, {y:,.2f} ({unit})")
                print(f"   Output (meters): {x_m:,.2f}, {y_m:,.2f}")
            else:
                x_ft = x / 0.3048
                y_ft = y / 0.3048
                print(f"   Output: {x:,.2f}, {y:,.2f} ({unit})")
                print(f"   Output (feet): {x_ft:,.2f}, {y_ft:,.2f}")

def format_map_corners(corner_coords, theater_name):
    """Format map corner coordinates for display."""
    theater_config = THEATER_CONFIGS[theater_name]
    
    print("=" * 60)
    print(f"MAP CORNER COORDINATES - {theater_config['name'].upper()}")
    print("=" * 60)
    print()
    
    corner_names = {
        'sw': 'SW CORNER (0, 0)',
        'se': 'SE CORNER (Max X, 0)', 
        'nw': 'NW CORNER (0, Max Y)',
        'ne': 'NE CORNER (Max X, Max Y)'
    }
    
    for corner_key, corner_name in corner_names.items():
        if corner_key in corner_coords:
            data = corner_coords[corner_key]
            game_x, game_y = data['game']
            lat, lon = data['latlon']
            
            print(f"🗺️  {corner_name}")
            print("-" * 40)
            print(f"Latitude (decimal):     {lat:.6f}°")
            print(f"Longitude (decimal):    {lon:.6f}°")
            print(f"Game coordinates:       {round(lat, 2):.2f}°")
            print(f"Game coordinates:       {round(lon, 1):.2f}°")
            print(f"Game coordinates:       {game_x:,.1f}, {game_y:,.1f} (feet)")
            print(f"Game coordinates:       {game_x*0.3048799096:,.0f}, {game_y*0.3048799096:,.0f} (meters)")
            
            # DMS format
            lat_d = int(lat)
            lat_m = int(abs(lat - lat_d) * 60)
            lat_s = (abs(lat - lat_d) * 60 - lat_m) * 60
            
            lon_d = int(lon)
            lon_m = int(abs(lon - lon_d) * 60)
            lon_s = (abs(lon - lon_d) * 60 - lon_m) * 60
            
            print(f"DMS format:             {lat_d}° {lat_m}' {lat_s:.2f}\", {lon_d}° {lon_m}' {lon_s:.2f}\"")
            print()

def convert_coordinates(args):
    """Handle coordinate conversion command."""
    theater_name = args.theater
    
    # Try to get theater config using dynamic loading
    try:
        theater_config = get_theater_config(theater_name)
    except ValueError as e:
        print(f"Error: {e}")
        available_theaters = get_available_theaters()
        print(f"Available theaters: {', '.join(available_theaters)}")
        return 1
    
    
    
    # Get heightmap path if elevation is requested
    heightmap_path = None
    if args.elevation:
        try:
            paths = get_theater_paths(theater_name)
            heightmap_path = paths['heightmap']
        except Exception as e:
            print(f"Warning: Could not get heightmap path: {e}")
    
    # Initialize converter using new theater_name parameter
    converter = CoordinateConverter(theater_name=theater_name, heightmap_path=heightmap_path)
    
    try:
        x_or_lat = float(args.x_or_lat)
        y_or_lon = float(args.y_or_lon)
    except ValueError:
        print("Error: Coordinates must be numeric values")
        return 1
    
    if args.reverse:
        # Convert lat/lon to game coordinates
        lat, lon = x_or_lat, y_or_lon
        to_feet = (args.unit == 'feet')
        game_x, game_y = converter.latlon_to_game(lat, lon, to_feet=to_feet)
        
        format_coordinate_output(lat, lon, game_x, game_y, unit=args.unit, include_dms=args.dms)
    else:
        # Convert game coordinates to lat/lon
        game_x, game_y = x_or_lat, y_or_lon
        from_feet = (args.unit == 'feet')
        # Use the ultra-high precision method with empirical correction (±5m accuracy)
        #lat, lon = converter.game_to_latlon_high_precision(game_x, game_y, from_feet=from_feet)
        lat, lon = converter.game_to_latlon_grid_karney(game_x, game_y, from_feet=from_feet)
        
        elevation = None
        if args.elevation:
            try:
                elevation = converter.get_elevation(game_x, game_y, from_feet=from_feet)
            except HeightmapNotFoundError:
                print("   Elevation: Heightmap file not found")
            except CoordinatesOutOfBoundsError:
                print("   Elevation: Coordinates outside valid range")
            except HeightmapReadError as e:
                print(f"   Elevation: Error reading heightmap data ({e})")
            except ElevationError as e:
                print(f"   Elevation: {e}")
        
        format_coordinate_output(lat, lon, game_x, game_y, elevation, args.unit, args.dms)
    
    return 0

def show_corners(args):
    """Handle map corners command."""
    theater_name = args.theater
    
    # Try to get theater config using dynamic loading
    try:
        theater_config = get_theater_config(theater_name)
    except ValueError as e:
        print(f"Error: {e}")
        available_theaters = get_available_theaters()
        print(f"Available theaters: {', '.join(available_theaters)}")
        return 1

    converter = CoordinateConverter(theater_name=theater_name)
    
    corner_coords = converter.get_map_corners(in_feet=True)
    format_map_corners(corner_coords, theater_name)
    
    return 0

def list_theaters(args):
    """List available theaters."""
    print("Available Theaters:")
    print("=" * 40)
    
    # Get theaters from dynamic loading (includes both file-based and static)
    available_theaters = get_available_theaters()
    
    for theater in sorted(available_theaters):
        try:
            config = get_theater_config(theater)
            name = config.get('name', theater.title())
            center_lat = config.get('center_lat', 'Unknown')
            center_lon = config.get('center_lon', 'Unknown')
            utm_zone = config.get('utm_zone', 'Unknown')
            print(f"{theater:<10} - {name:<15} (Center: {center_lat}, {center_lon}, UTM Zone {utm_zone})")
        except Exception as e:
            print(f"{theater:<10} - Error loading config: {e}")
    
    if not available_theaters:
        print("\nNo theaters found. Please check your Falcon BMS installation path in config.py")
    
    return 0
def calculate_projection_string(args):
    """Calculate projection string for a given center lat/lon."""
    try:
        center_lat = float(args.center_lat)
        center_lon = float(args.center_lon)
        desired_y = float(args.desired_y) if hasattr(args, 'desired_y') and args.desired_y else 512000
    except ValueError:
        print("Error: Coordinates must be numeric values")
        return 1
    
    print(f"🗺️  Calculating projection string for:")
    print(f"   Center Latitude:  {center_lat:.6f}°")
    print(f"   Center Longitude: {center_lon:.6f}°")
    print(f"   Desired Y value:  {desired_y:,.0f} meters")
    print()
    
    try:
        # Calculate the required false northing
        y_0 = create_proj_string(center_lat, center_lon, desired_y)
        
        # Construct the complete projection string
        proj_string = f"+proj=tmerc +lon_0={center_lon} +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0={y_0:.5e}"
        
        print("✅ Projection string calculated successfully!")
        print("=" * 60)
        print(f"Projection String:")
        print(f"{proj_string}")
        print("=" * 60)
        print()
        print("You can use this projection string in your theater configuration.")
        print("Copy the string above and add it to your theater config in config.py")
        
        return 0
        
    except Exception as e:
        print(f"Error calculating projection string: {e}")
        return 1

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Falcon BMS Coordinate Conversion Toolset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert game coordinates to lat/lon
  %(prog)s convert 1500000 2000000 --theater korea
  
  # Convert with elevation lookup
  %(prog)s convert 1500000 2000000 --elevation --theater korea
  
  # Reverse conversion (lat/lon to game coordinates)
  %(prog)s convert 37.5 127.0 --reverse --unit meters --theater korea
  
  # Show map corners
  %(prog)s corners --theater korea
  
  # List available theaters
  %(prog)s theaters
  
  # Generate projection string for new theater
  %(prog)s projection 37.5 127.0 --desired-y 512000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert coordinates')
    convert_parser.add_argument('x_or_lat', help='X coordinate (game) or latitude (reverse)')
    convert_parser.add_argument('y_or_lon', help='Y coordinate (game) or longitude (reverse)')
    convert_parser.add_argument('--theater', default='korea', 
                               choices=list(THEATER_CONFIGS.keys()),
                               help='Theater to use for conversion (default: korea)')
    convert_parser.add_argument('--elevation', action='store_true',
                               help='Include elevation lookup from heightmaps')
    convert_parser.add_argument('--reverse', action='store_true',
                               help='Convert from lat/lon to game coordinates')
    convert_parser.add_argument('--unit', choices=['feet', 'meters'], default='feet',
                               help='Unit for game coordinates (default: feet)')
    convert_parser.add_argument('--dms', action='store_true',
                               help='Include degrees/minutes/seconds format')
    convert_parser.set_defaults(func=convert_coordinates)
    
    # Corners command
    corners_parser = subparsers.add_parser('corners', help='Show map corner coordinates')
    corners_parser.add_argument('--theater', default='korea',
                               choices=list(THEATER_CONFIGS.keys()),
                               help='Theater to show corners for (default: korea)')
    corners_parser.set_defaults(func=show_corners)
    
    # Theaters command
    theaters_parser = subparsers.add_parser('theaters', help='List available theaters')
    theaters_parser.set_defaults(func=list_theaters)

    # Projection string command
    projection_parser = subparsers.add_parser('projection', help='Generate projection string for a given center lat/lon')
    projection_parser.add_argument('center_lat', help='Center latitude of the theater (decimal degrees)')
    projection_parser.add_argument('center_lon', help='Center longitude of the theater (decimal degrees)')
    projection_parser.add_argument('--desired-y', type=float, default=512000,
                                 help='Desired Y position in projected space (default: 512000 meters)')
    projection_parser.set_defaults(func=calculate_projection_string)

    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)

if __name__ == '__main__':
    sys.exit(main())
