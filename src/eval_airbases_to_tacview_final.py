#!/usr/bin/env python3
"""
Falcon BMS Airbase to Tacview XML Converter

Extracts airbase and runway data from Falcon BMS and generates Tacview-compatible XML files.
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import THEATER_CONFIGS, get_theater_paths, get_available_theaters
from utils.coordinate_converter import CoordinateConverter
from utils.file_parser import parse_stations_file, get_all_airbase_data

def generate_tacview_xml(airbases, converter, debug=False):
    """Generate Tacview-compatible XML from airbase data."""
    
    # Create root element with Tacview namespace
    root = ET.Element('Document', attrib={
        'xmlns': 'http://www.tacview.net/xml/0.1',
        'CreatedBy': 'Falcon BMS Tacview Converter',
        'Version': '1.0'
    })
    
    # Add metadata
    metadata = ET.SubElement(root, 'Metadata')
    ET.SubElement(metadata, 'Title').text = 'Falcon BMS Airbases'
    ET.SubElement(metadata, 'Description').text = 'Airbase and runway data extracted from Falcon BMS'
    ET.SubElement(metadata, 'Author').text = 'Falcon BMS Tacview Converter'
    
    # Create objects container
    objects = ET.SubElement(root, 'Objects')
    
    object_id = 1
    processed_count = 0
    
    for airbase in airbases:
        try:
            # Convert game coordinates to lat/lon
            lat, lon = converter.game_to_latlon(airbase['x'], airbase['y'], from_feet=True)
            
            # Get elevation if available
            elevation = converter.get_elevation(airbase['x'], airbase['y'], from_feet=True)
            if elevation < -900:  # Error code
                elevation = 0
            
            # Create airbase object
            obj = ET.SubElement(objects, 'Object', attrib={'ID': str(object_id)})
            
            # Add object properties
            ET.SubElement(obj, 'Name').text = f"{airbase['icao']} - {airbase['name']}"
            ET.SubElement(obj, 'Type').text = 'Airport'
            
            # Add position
            position = ET.SubElement(obj, 'Position')
            ET.SubElement(position, 'Latitude').text = f"{lat:.8f}"
            ET.SubElement(position, 'Longitude').text = f"{lon:.8f}"
            ET.SubElement(position, 'Altitude').text = f"{elevation:.2f}"
            
            # Add additional properties
            properties = ET.SubElement(obj, 'Properties')
            ET.SubElement(properties, 'Property', attrib={'Name': 'ICAO', 'Value': airbase['icao']})
            ET.SubElement(properties, 'Property', attrib={'Name': 'AirbaseName', 'Value': airbase['name']})
            ET.SubElement(properties, 'Property', attrib={'Name': 'GameID', 'Value': str(airbase['id'])})
            ET.SubElement(properties, 'Property', attrib={'Name': 'GameCoords', 'Value': f"{airbase['x']:.0f},{airbase['y']:.0f}"})
            
            object_id += 1
            processed_count += 1
            
            if debug:
                print(f"  ✓ {airbase['icao']} - {airbase['name']} at {lat:.6f}, {lon:.6f}")
            
            # Add runways if available
            for runway in airbase.get('runways', []):
                # Calculate runway endpoints
                runway_lat, runway_lon = converter.game_to_latlon(
                    airbase['x'] + runway['x'], 
                    airbase['y'] + runway['y'], 
                    from_feet=True
                )
                runway_elevation = converter.get_elevation(
                    airbase['x'] + runway['x'], 
                    airbase['y'] + runway['y'], 
                    from_feet=True
                )
                if runway_elevation < -900:
                    runway_elevation = elevation
                
                # Create runway object
                runway_obj = ET.SubElement(objects, 'Object', attrib={'ID': str(object_id)})
                ET.SubElement(runway_obj, 'Name').text = f"Runway {runway['id']} at {airbase['icao']}"
                ET.SubElement(runway_obj, 'Type').text = 'GroundUnit'
                ET.SubElement(runway_obj, 'Color').text = '#0066CC'  # Blue color for runways
                
                # Runway position
                runway_pos = ET.SubElement(runway_obj, 'Position')
                ET.SubElement(runway_pos, 'Latitude').text = f"{runway_lat:.8f}"
                ET.SubElement(runway_pos, 'Longitude').text = f"{runway_lon:.8f}"
                ET.SubElement(runway_pos, 'Altitude').text = f"{runway_elevation:.2f}"
                
                # Runway properties
                runway_props = ET.SubElement(runway_obj, 'Properties')
                ET.SubElement(runway_props, 'Property', attrib={'Name': 'RunwayID', 'Value': runway['id']})
                ET.SubElement(runway_props, 'Property', attrib={'Name': 'Length', 'Value': f"{runway['length']:.0f}"})
                ET.SubElement(runway_props, 'Property', attrib={'Name': 'Width', 'Value': f"{runway['width']:.0f}"})
                ET.SubElement(runway_props, 'Property', attrib={'Name': 'Heading', 'Value': f"{runway['heading']:.1f}"})
                ET.SubElement(runway_props, 'Property', attrib={'Name': 'ParentAirbase', 'Value': airbase['icao']})
                
                object_id += 1
                
                if debug:
                    print(f"    ➤ Runway {runway['id']}: {runway['length']:.0f}ft x {runway['width']:.0f}ft, HDG {runway['heading']:.1f}°")
                
        except Exception as e:
            print(f"Error processing airbase {airbase.get('name', 'Unknown')}: {e}")
            if debug:
                import traceback
                traceback.print_exc()
    
    print(f"Processed {processed_count} airbases with {object_id - processed_count - 1} runways")
    return root

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Tacview XML from Falcon BMS airbase data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate for default theater (Korea)
  %(prog)s
  
  # Generate for specific theater
  %(prog)s israel
  
  # Generate with debug output
  %(prog)s korea --debug
  
  # Custom output filename
  %(prog)s balkans --output balkans_airbases.xml
        """
    )
    
    parser.add_argument('theater', nargs='?', default='korea',
                       choices=list(THEATER_CONFIGS.keys()),
                       help='Theater to process (default: korea)')
    parser.add_argument('--output', '-o', 
                       help='Output XML filename (default: <theater>_airbases_tacview.xml)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    theater_name = args.theater
    output_file = args.output or f"{theater_name}_airbases_tacview.xml"
    
    # Validate theater
    if theater_name not in THEATER_CONFIGS:
        print(f"Error: Unknown theater '{theater_name}'")
        print(f"Available theaters: {', '.join(THEATER_CONFIGS.keys())}")
        return 1
    
    # Check if theater is available
    available_theaters = get_available_theaters()
    if theater_name not in available_theaters:
        print(f"Error: Theater '{theater_name}' not found in Falcon BMS installation")
        print(f"Available theaters: {', '.join(available_theaters)}")
        return 1
    
    print(f"Processing {THEATER_CONFIGS[theater_name]['name']} theater...")
    
    try:
        # Get file paths
        paths = get_theater_paths(theater_name)
        theater_config = THEATER_CONFIGS[theater_name]
        
        if args.debug:
            print(f"Theater config: {theater_config}")
            print(f"File paths: {paths}")
        
        # Initialize coordinate converter
        converter = CoordinateConverter(theater_config, paths['heightmap'])
        
        # Parse ICAO mappings
        print("Loading ICAO code mappings...")
        icao_map = parse_stations_file(paths['stations_data'])
        print(f"Loaded {len(icao_map)} ICAO mappings")
        
        # Parse airbase data
        print("Loading airbase data...")
        airbases = get_all_airbase_data(paths, icao_map)
        print(f"Found {len(airbases)} airbases")
        
        if not airbases:
            print("No airbases found. Check your file paths and theater configuration.")
            return 1
        
        # Generate XML
        print("Generating Tacview XML...")
        xml_root = generate_tacview_xml(airbases, converter, args.debug)
        
        # Pretty print and save
        rough_string = ET.tostring(xml_root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        final_xml = '\n'.join(lines)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_xml)
        
        print(f"✓ Generated {output_file}")
        print(f"  Import this file into Tacview to see {THEATER_CONFIGS[theater_name]['name']} airbases")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())