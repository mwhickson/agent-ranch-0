import unittest
from src.converter import meters_to_feet, celsius_to_fahrenheit, grams_to_ounces

class TestConverter(unittest.TestCase):
    def test_meters_to_feet(self):
        # 1 meter is approx 3.28084 feet
        self.assertAlmostEqual(meters_to_feet(1), 3.280839895, places=5)

    def test_celsius_to_fahrenheit(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)

    def test_grams_to_ounces(self):
        # 1 gram is approx 0.035274 ounces
        self.assertAlmostEqual(grams_to_ounces(100), 3.52739907, places=5)

if __name__ == '__main__':
    unittest.main()
