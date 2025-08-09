import unittest
from src.eval_airbases_to_tacview_final import extract_airbase_data, generate_xml

class TestAirbaseConverter(unittest.TestCase):

    def test_extract_airbase_data(self):
        # Test the extraction of airbase data from a sample input
        sample_input = "path/to/sample/CampObjData.XML"
        expected_output = {
            'ICAO': 'KABC',
            'name': 'Sample Airbase',
            'coordinates': (34.0, -118.0)
        }
        result = extract_airbase_data(sample_input)
        self.assertEqual(result, expected_output)

    def test_generate_xml(self):
        # Test the XML generation from airbase data
        airbase_data = {
            'ICAO': 'KABC',
            'name': 'Sample Airbase',
            'coordinates': (34.0, -118.0)
        }
        expected_xml = """<Airbase>
    <ICAO>KABC</ICAO>
    <Name>Sample Airbase</Name>
    <Coordinates>
        <Latitude>34.0</Latitude>
        <Longitude>-118.0</Longitude>
    </Coordinates>
</Airbase>"""
        result = generate_xml(airbase_data)
        self.assertEqual(result.strip(), expected_xml.strip())

if __name__ == '__main__':
    unittest.main()