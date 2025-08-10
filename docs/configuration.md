# Configuration

The `config.py` file is crucial for setting up the Falcon BMS Tacview Airbase Converter. It allows users to customize various settings to match their Falcon BMS installation and desired theater configurations.

## Configuration Settings

### Falcon BMS Installation Directory
- **Description**: Set the path to your Falcon BMS installation directory.
- **Example**: 
  ```python
  falcon_bms_path = "C:/Path/To/Falcon/BMS"
  ```

### Theater Configurations
- **Description**: Add or modify theater configurations in the `THEATER_CONFIGS` dictionary.
- **Structure**:
  ```python
  'theater_name': {
      'name': "Theater Display Name",
      'folder_path': "Add-On Theater Name",  # Empty string "" for default Korea
      'projection_string': "++proj=tmerc +lon_0=127.5 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-3.74929e+06",
      'camp_w': 3358699.5,  # Campaign width (adjust per theater)
      'camp_h': 3358699.5,  # Campaign height (adjust per theater)
      'heightmap_subpath': "Theater/NewTerrain/HeightMaps/HeightMap.raw"
  }
  ```

### Projection Settings
- **Description**: Adjust the projection string to match the coordinate system used in your theater.
- **Example**: 
  ```python
  projection_string = "3358699.5"
  ```

### Campaign Dimensions
- **Description**: Set the campaign width and height based on the specific theater requirements.
- **Example**: 
  ```python
  camp_w = 3358699.5
  camp_h = 3358699.5
  ```

### Heightmap Path
- **Description**: Specify the relative path to the heightmap file for the theater.
- **Example**: 
  ```python
  heightmap_subpath = "Theater/NewTerrain/HeightMaps/HeightMap.raw"
  ```

## Example Configuration

Here is an example of how a theater configuration might look in `config.py`:

```python
THEATER_CONFIGS = {
    'korea': {
        'name': "Korea",
        'folder_path': "",
        'projection_string': "+proj=tmerc +lon_0=127.5 +ellps=WGS84 +k=0.9996 +units=m +x_0=512000 +y_0=-3.74929e+06",
        'camp_w': 3358699.5,
        'camp_h': 3358699.5,
        'heightmap_subpath': "Korea/NewTerrain/HeightMaps/HeightMap.raw"
    },
    'balkans': {
        'name': "Balkans",
        'folder_path': "Add-On Theater/Balkans",
        'projection_string': "+proj=utm +zone=34 +datum=WGS84 +units=m +no_defs",
        'camp_w': 3000000.0,
        'camp_h': 3000000.0,
        'heightmap_subpath': "Balkans/NewTerrain/HeightMaps/HeightMap.raw"
    }
}
```

By properly configuring the `config.py` file, users can ensure that the Falcon BMS Tacview Airbase Converter operates correctly with their specific setup.