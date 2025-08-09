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
    """Generate XML from airbase data matching the original format."""
    
    def to_dms(deg):
        """Convert decimal degrees to degrees and decimal minutes format."""
        d = int(deg)
        m = abs((deg - d) * 60)
        return f"{d}° {m:.4f}'"
    
    def clean_shortname(name):
        """Extract short name from full name."""
        remove_terms = ["Airbase", "Airstrip", "Airport", "Highway Strip", "Highwaystrip", "Hiwaystrip"]
        shortname = name
        for term in remove_terms:
            shortname = shortname.replace(term, "")
        return shortname.strip()
    
    # Create root element - simple Objects container like original
    root = ET.Element('Objects')
    
    processed_count = 0
    
    for airbase in airbases:
        try:
            # Convert game coordinates to lat/lon
            lat, lon = converter.game_to_latlon(airbase['x'], airbase['y'], from_feet=True)
            
            # Get elevation if available
            elevation = converter.get_elevation(airbase['x'], airbase['y'], from_feet=True)
            if elevation < -900:  # Error code
                elevation = 0
            
            # Determine ID format
            if airbase['icao'].startswith('AB'):
                obj_id = f"CampId:{airbase['id']}"
            else:
                obj_id = f"ICAO:{airbase['icao']}"
            
            # Create airbase object
            obj = ET.SubElement(root, 'Object', attrib={'ID': obj_id})
            
            # Add object properties
            ET.SubElement(obj, 'Type').text = 'Airport'
            
            # Add name - either with or without ICAO code
            if airbase['icao'].startswith('AB'):
                ET.SubElement(obj, 'Name').text = airbase['name']
            else:
                # Only add ICAO if it's not already in the name
                if airbase['icao'] in airbase['name']:
                    ET.SubElement(obj, 'Name').text = airbase['name']
                else:
                    ET.SubElement(obj, 'Name').text = f"{airbase['name']} ({airbase['icao']})"
            
            # Add short name
            short_name = clean_shortname(airbase['name'])
            if airbase['icao'].startswith('AB'):
                ET.SubElement(obj, 'ShortName').text = short_name
            else:
                ET.SubElement(obj, 'ShortName').text = airbase['icao']
            
            # Add position in DMS format
            position = ET.SubElement(obj, 'Position')
            ET.SubElement(position, 'Latitude').text = to_dms(lat)
            ET.SubElement(position, 'Longitude').text = to_dms(lon)
            ET.SubElement(position, 'Altitude').text = f"{elevation * 0.3048:.1f}"
            
            processed_count += 1
            
            if debug:
                print(f"  ✓ {airbase['icao']} - {airbase['name']} at {lat:.6f}, {lon:.6f}")
            
            # Add runways as separate objects (like original format)
            for runway in airbase.get('runways', []):
                # Calculate runway position (airbase position + runway offset)
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
                
                # Create runway object (no ID attribute like in original)
                runway_obj = ET.SubElement(root, 'Object')
                
                # Runway position in DMS format
                runway_pos = ET.SubElement(runway_obj, 'Position')
                ET.SubElement(runway_pos, 'Latitude').text = to_dms(runway_lat)
                ET.SubElement(runway_pos, 'Longitude').text = to_dms(runway_lon)
                ET.SubElement(runway_pos, 'Altitude').text = f"{runway_elevation * 0.3048:.1f}"
                
                # Runway shape and appearance (matching original format)
                ET.SubElement(runway_obj, 'Shape').text = 'Cube'
                ET.SubElement(runway_obj, 'Color').text = '#2d94ff'
                
                # Runway size
                size = ET.SubElement(runway_obj, 'Size')
                ET.SubElement(size, 'Width').text = f"{int(runway['width'] * 0.3048)}"
                ET.SubElement(size, 'Length').text = f"{int(runway['length'] * 0.3048)}"
                ET.SubElement(size, 'Height').text = "2"
                
                # Runway orientation
                orientation = ET.SubElement(runway_obj, 'Orientation')
                ET.SubElement(orientation, 'Yaw').text = f"{runway['heading']:.1f}"
                
                if debug:
                    print(f"    ➤ Runway {runway['id']}: {runway['length']:.0f}ft x {runway['width']:.0f}ft, HDG {runway['heading']:.1f}°")
                
        except Exception as e:
            print(f"Error processing airbase {airbase.get('name', 'Unknown')}: {e}")
            if debug:
                import traceback
                traceback.print_exc()
    
    print(f"Processed {processed_count} airbases with {len(root) - processed_count} runways")
    return root

def main():
    """Main entry point."""
    print("Entering main() function...")
    
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
    
    print("Parsing arguments...")
    args = parser.parse_args()
    print(f"Parsed arguments: {args}")
    
    theater_name = args.theater
    output_file = args.output or f"{theater_name}_airbases_tacview.xml"
    
    print(f"Theater: {theater_name}, Output file: {output_file}")
    
    # Validate theater
    print(f"Available theater configs: {list(THEATER_CONFIGS.keys())}")
    if theater_name not in THEATER_CONFIGS:
        print(f"Error: Unknown theater '{theater_name}'")
        print(f"Available theaters: {', '.join(THEATER_CONFIGS.keys())}")
        return 1
    
    # Check if theater is available
    print("Checking available theaters...")
    try:
        available_theaters = get_available_theaters()
        print(f"Available theaters found: {available_theaters}")
    except Exception as e:
        print(f"Error checking available theaters: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
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
        
        # Generate XML manually to match original format exactly
        xml_lines = ["<?xml version='1.0' encoding='utf-8'?>", '<Objects>']
        
        def add_element(lines, name, text=None, attribs=None, indent=1):
            """Add an XML element with proper indentation."""
            spaces = "  " * indent
            if attribs:
                attr_str = ' '.join(f'{k}="{v}"' for k, v in attribs.items())
                if text:
                    lines.append(f'{spaces}<{name} {attr_str}>{text}</{name}>')
                else:
                    lines.append(f'{spaces}<{name} {attr_str}>')
            else:
                if text:
                    lines.append(f'{spaces}<{name}>{text}</{name}>')
                else:
                    lines.append(f'{spaces}<{name}>')
        
        def close_element(lines, name, indent=1):
            """Close an XML element with proper indentation."""
            spaces = "  " * indent
            lines.append(f'{spaces}</{name}>')
        
        # Convert ET elements to manual XML generation
        for obj in xml_root:
            # Get object attributes
            obj_attribs = obj.attrib if obj.attrib else None
            add_element(xml_lines, 'Object', attribs=obj_attribs, indent=1)
            
            # Add child elements
            for child in obj:
                if child.tag in ['Position', 'Size', 'Orientation']:
                    add_element(xml_lines, child.tag, indent=2)
                    for subchild in child:
                        add_element(xml_lines, subchild.tag, subchild.text, indent=3)
                    close_element(xml_lines, child.tag, indent=2)
                else:
                    add_element(xml_lines, child.tag, child.text, indent=2)
            
            close_element(xml_lines, 'Object', indent=1)
        
        xml_lines.append('</Objects>')
        final_xml = '\n'.join(xml_lines)
        
        with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
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
    try:
        print("Starting Falcon BMS Tacview Converter...")
        print(f"Python path: {sys.path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script arguments: {sys.argv}")
        
        result = main()
        print(f"Script completed with result: {result}")
        sys.exit(result)
    except Exception as e:
        print(f"Fatal error in main execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)