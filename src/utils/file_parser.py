"""
File parsing utilities for Falcon BMS data files
"""
import xml.etree.ElementTree as ET
import os

def parse_stations_file(stations_path):
    """Parse Stations+Ils.dat file to get ICAO code mappings."""
    icao_map = {}
    
    if not os.path.exists(stations_path):
        print(f"Warning: Stations file not found: {stations_path}")
        return icao_map
    
    try:
        with open(stations_path, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        icao_code = parts[0].strip()
                        airbase_id = parts[1].strip()
                        try:
                            airbase_id = int(airbase_id)
                            icao_map[airbase_id] = icao_code
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Error parsing stations file: {e}")
    
    return icao_map

def parse_campaign_data(campaign_path):
    """Parse CampObjData.XML file to get airbase information."""
    airbases = []
    
    if not os.path.exists(campaign_path):
        print(f"Error: Campaign data file not found: {campaign_path}")
        return airbases
    
    try:
        tree = ET.parse(campaign_path)
        root = tree.getroot()
        
        for obj in root.findall('.//Object'):
            obj_type = obj.get('Type')
            if obj_type == '6':  # Airbase type
                obj_id = int(obj.get('ID', 0))
                name_elem = obj.find('Name')
                pos_elem = obj.find('Position')
                
                if name_elem is not None and pos_elem is not None:
                    name = name_elem.text
                    x = float(pos_elem.get('X', 0))
                    y = float(pos_elem.get('Y', 0))
                    
                    airbase = {
                        'id': obj_id,
                        'name': name,
                        'x': x,
                        'y': y
                    }
                    airbases.append(airbase)
                    
    except Exception as e:
        print(f"Error parsing campaign data: {e}")
    
    return airbases

def parse_falcon_ct(ct_path):
    """Parse Falcon4_CT.xml to get class table mappings."""
    class_table = {}
    
    if not os.path.exists(ct_path):
        print(f"Warning: Class table file not found: {ct_path}")
        return class_table
    
    try:
        tree = ET.parse(ct_path)
        root = tree.getroot()
        
        for entry in root.findall('.//Entry'):
            ct_id = entry.get('ID')
            name = entry.get('Name', '')
            
            if ct_id:
                try:
                    ct_id = int(ct_id)
                    class_table[ct_id] = name
                except ValueError:
                    continue
                    
    except Exception as e:
        print(f"Error parsing class table: {e}")
    
    return class_table

def find_runway_files(objective_data_path, airbase_id):
    """Find runway geometry files for a specific airbase."""
    runway_files = []
    
    if not os.path.exists(objective_data_path):
        return runway_files
    
    # Look for files matching the airbase ID pattern
    airbase_folder = os.path.join(objective_data_path, str(airbase_id))
    if os.path.exists(airbase_folder):
        for filename in os.listdir(airbase_folder):
            if filename.endswith('.xml'):
                runway_files.append(os.path.join(airbase_folder, filename))
    
    return runway_files

def parse_runway_file(runway_path):
    """Parse a runway XML file to get runway geometry."""
    runways = []
    
    if not os.path.exists(runway_path):
        return runways
    
    try:
        tree = ET.parse(runway_path)
        root = tree.getroot()
        
        for runway in root.findall('.//Runway'):
            # Extract runway information
            runway_data = {
                'id': runway.get('ID', ''),
                'length': float(runway.get('Length', 0)),
                'width': float(runway.get('Width', 0)),
                'heading': float(runway.get('Heading', 0)),
                'x': float(runway.get('X', 0)),
                'y': float(runway.get('Y', 0)),
                'z': float(runway.get('Z', 0))
            }
            runways.append(runway_data)
            
    except Exception as e:
        print(f"Error parsing runway file {runway_path}: {e}")
    
    return runways

def get_all_airbase_data(paths, icao_map):
    """Get complete airbase data including runways."""
    airbases = parse_campaign_data(paths['campaign_data'])
    
    # Add ICAO codes and runway information
    for airbase in airbases:
        airbase_id = airbase['id']
        
        # Add ICAO code if available
        airbase['icao'] = icao_map.get(airbase_id, f"AB{airbase_id:03d}")
        
        # Find and parse runway files
        runway_files = find_runway_files(paths['objective_data'], airbase_id)
        airbase['runways'] = []
        
        for runway_file in runway_files:
            runways = parse_runway_file(runway_file)
            airbase['runways'].extend(runways)
    
    return airbases


# Legacy functions for backwards compatibility
def parse_airbase_data(file_path):
    airbases = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                data = line.split(',')
                airbase = {
                    'icao': data[0].strip(),
                    'name': data[1].strip(),
                    'latitude': float(data[2].strip()),
                    'longitude': float(data[3].strip()),
                    'elevation': float(data[4].strip())
                }
                airbases.append(airbase)
    return airbases

def parse_runway_data(file_path):
    runways = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                data = line.split(',')
                runway = {
                    'icao': data[0].strip(),
                    'length': float(data[1].strip()),
                    'width': float(data[2].strip()),
                    'heading': float(data[3].strip())
                }
                runways.append(runway)
    return runways