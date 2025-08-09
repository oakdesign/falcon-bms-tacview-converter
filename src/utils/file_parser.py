"""
File parsing utilities for Falcon BMS data files
Based on the original working logic
"""
import xml.etree.ElementTree as ET
import os
import re
import math

def parse_valid_airbase_indices(ct_file):
    """Parse Falcon4_CT.xml to get valid airbase indices."""
    valid_indices = set()
    
    if not os.path.exists(ct_file):
        print(f"Warning: CT file not found: {ct_file}")
        return valid_indices
    
    try:
        tree = ET.parse(ct_file)
        for ct in tree.getroot().iter("CT"):
            try:
                domain = int(ct.find("Domain").text)
                class_val = int(ct.find("Class").text)
                type_val = int(ct.find("Type").text)
                specific = int(ct.find("Specific").text)
                
                # Check for airbase criteria: Domain=3, Class=4, Type=1 or 2, Specific=255
                if (domain == 3 and class_val == 4 and 
                    type_val in (1, 2) and specific == 255):
                    entity_idx = int(ct.find("EntityIdx").text)
                    valid_indices.add(entity_idx)
            except (AttributeError, ValueError, TypeError):
                continue
    except Exception as e:
        print(f"Error parsing CT file: {e}")
    
    return valid_indices

def parse_campaign_data(obj_file, valid_indices):
    """Parse CampObjData.XML file to get airbase information using valid indices."""
    airbases = []
    
    if not os.path.exists(obj_file):
        print(f"Error: Campaign data file not found: {obj_file}")
        return airbases
    
    try:
        tree = ET.parse(obj_file)
        for obj in tree.getroot().iter("CampObj"):
            try:
                ocd_index = int(obj.find("OcdIndex").text)
                
                # Only process objects with valid airbase indices
                if ocd_index not in valid_indices:
                    continue
                
                name = obj.find("CampName").text.strip()
                # Note: In Falcon BMS, PositionX is actually Y coordinate and vice versa
                y = float(obj.find("PositionX").text) 
                x = float(obj.find("PositionY").text)
                camp_id = int(obj.get("CampId"))
                
                airbase = {
                    'id': camp_id,
                    'name': name,
                    'x': x,
                    'y': y,
                    'ocd_index': ocd_index
                }
                airbases.append(airbase)
                
            except (AttributeError, ValueError, TypeError) as e:
                continue
                    
    except Exception as e:
        print(f"Error parsing campaign data: {e}")
    
    return airbases

def parse_stations_file(stations_path):
    """Parse Stations+Ils.dat file to get ICAO code mappings from comments."""
    icao_map = {}
    
    if not os.path.exists(stations_path):
        print(f"Warning: Stations file not found: {stations_path}")
        return icao_map
    
    try:
        with open(stations_path, encoding="utf-8") as f:
            lines = f.readlines()
            
        for i in range(len(lines)):
            line = lines[i].strip()
            
            # Look for comment lines with ICAO codes in parentheses
            if line.startswith("#") and "(" in line and ")" in line:
                icao_match = re.search(r'\(([A-Z]{4})\)', line)
                if not icao_match:
                    continue
                    
                icao = icao_match.group(1)
                
                # Check the next line for data
                if i + 1 < len(lines):
                    data_line = lines[i + 1].strip()
                    if data_line and not data_line.startswith("#"):
                        try:
                            camp_id_str = data_line.split()[0]
                            camp_id = int(camp_id_str)
                            icao_map[camp_id] = icao
                        except (ValueError, IndexError):
                            continue
                            
    except Exception as e:
        print(f"Error parsing stations file: {e}")
    
    return icao_map

def get_objective_related_paths(ocd_index, objective_data_path):
    """Get paths to PHD and PDX files for runway data."""
    folder = f"OCD_{ocd_index:05d}"
    base = os.path.join(objective_data_path, folder)
    phd_path = os.path.join(base, f"PHD_{ocd_index:05d}.XML")
    pdx_path = os.path.join(base, f"PDX_{ocd_index:05d}.XML")
    return phd_path, pdx_path

def extract_runway_shapes(phd_path):
    """Extract runway shape data from PHD file."""
    runways = []
    
    if not os.path.exists(phd_path):
        return runways
    
    try:
        tree = ET.parse(phd_path)
        for phd in tree.getroot().iter("PHD"):
            try:
                if int(phd.find("Type").text) == 8:  # Runway type
                    count = int(phd.find("PointCount").text)
                    first_idx = int(phd.find("FirstPtIdx").text)
                    yaw = float(phd.find("Data").text)
                    runways.append((first_idx, count, yaw))
            except (AttributeError, ValueError, TypeError):
                continue
    except Exception as e:
        print(f"Error parsing PHD file {phd_path}: {e}")
    
    return runways

def parse_pdx_points(pdx_path, first_idx, count):
    """Parse PDX file to get runway corner points."""
    points = []
    
    if not os.path.exists(pdx_path):
        return points
    
    try:
        tree = ET.parse(pdx_path)
        for pd in tree.getroot().iter("PD"):
            try:
                pd_type = pd.find("Type")
                pd_num = pd.get("Num")
                
                if pd_type is None or pd_num is None:
                    continue
                
                pd_num_int = int(pd_num)
                if (pd_num_int >= first_idx and 
                    pd_num_int < first_idx + count and 
                    int(pd_type.text) == 8):
                    
                    x = float(pd.find("OffsetX").text)
                    y = float(pd.find("OffsetY").text)
                    points.append((x, y))
                    
            except (AttributeError, ValueError, TypeError):
                continue
                
    except Exception as e:
        print(f"Error parsing PDX file {pdx_path}: {e}")
    
    return points

def compute_runway_geometry(corner_pts):
    """Compute runway geometry from corner points."""
    if len(corner_pts) < 4:
        return None
    
    try:
        # Center point
        cx = sum(p[0] for p in corner_pts) / len(corner_pts)
        cy = sum(p[1] for p in corner_pts) / len(corner_pts)
        
        # Length (from corner 0 to corner 3)
        dx = corner_pts[3][0] - corner_pts[0][0]
        dy = corner_pts[3][1] - corner_pts[0][1]
        yaw = (math.degrees(math.atan2(dx, dy)) + 360) % 360
        length = math.hypot(dx, dy)
        
        # Width (from corner 0 to corner 1)  
        dx_w = corner_pts[1][0] - corner_pts[0][0]
        dy_w = corner_pts[1][1] - corner_pts[0][1]
        width = math.hypot(dx_w, dy_w)
        
        return {
            'x': cx,
            'y': cy, 
            'length': length,
            'width': width,
            'heading': yaw
        }
    except Exception:
        return None

def get_all_airbase_data(paths, icao_map):
    """Get complete airbase data including runways using original logic."""
    import math
    
    # First, get valid airbase indices from CT file
    valid_indices = parse_valid_airbase_indices(paths['falcon_ct'])
    print(f"Found {len(valid_indices)} valid airbase indices")
    
    # Parse airbase data using valid indices
    airbases = parse_campaign_data(paths['campaign_data'], valid_indices)
    print(f"Found {len(airbases)} airbases in campaign data")
    
    # Add ICAO codes and runway information
    for airbase in airbases:
        airbase_id = airbase['id']
        
        # Add ICAO code if available
        airbase['icao'] = icao_map.get(airbase_id, f"AB{airbase_id:03d}")
        
        # Get runway data from objective files
        airbase['runways'] = []
        
        try:
            phd_path, pdx_path = get_objective_related_paths(
                airbase['ocd_index'], 
                paths['objective_data']
            )
            
            # Extract runway shapes from PHD file
            runway_shapes = extract_runway_shapes(phd_path)
            
            for first_idx, count, yaw in runway_shapes:
                # Get corner points from PDX file
                corner_points = parse_pdx_points(pdx_path, first_idx, count)
                
                if len(corner_points) >= 4:
                    runway_geom = compute_runway_geometry(corner_points)
                    if runway_geom:
                        runway_geom['id'] = f"{first_idx:03d}"
                        airbase['runways'].append(runway_geom)
                        
        except Exception as e:
            if len(str(e)) > 0:  # Only print non-empty errors
                print(f"Warning: Could not load runway data for {airbase['name']}: {e}")
    
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