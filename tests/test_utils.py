import unittest
from src.utils.coordinate_converter import convert_coordinates
from src.utils.file_parser import parse_airbase_data

class TestUtils(unittest.TestCase):

    def test_convert_coordinates(self):
        # Test coordinate conversion with sample data
        input_coords = (1000, 2000)
        expected_output = (1000, 2000)  # Replace with expected output based on conversion logic
        self.assertEqual(convert_coordinates(input_coords), expected_output)

    def test_parse_airbase_data(self):
        # Test parsing of airbase data from a sample file
        sample_data = "Sample airbase data"  # Replace with actual sample data
        expected_airbase = {"name": "Sample Airbase", "icao": "SAMP"}  # Replace with expected output
        self.assertEqual(parse_airbase_data(sample_data), expected_airbase)

if __name__ == '__main__':
    unittest.main()