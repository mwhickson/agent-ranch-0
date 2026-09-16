import unittest
from src.converter import (
    meters_to_feet, feet_to_meters, kilometers_to_miles, miles_to_kilometers,
    celsius_to_fahrenheit, fahrenheit_to_celsius,
    milliliters_to_fluid_ounces, fluid_ounces_to_milliliters,
    liters_to_quarts, quarts_to_liters,
    grams_to_ounces, ounces_to_grams,
    kilograms_to_pounds, pounds_to_kilograms
)

class TestConverterFull(unittest.TestCase):
    def test_distance(self):
        self.assertAlmostEqual(meters_to_feet(1), 3.280839895, places=5)
        self.assertAlmostEqual(feet_to_meters(3.280839895), 1, places=5)
        self.assertAlmostEqual(kilometers_to_miles(1), 0.6213711922, places=5)
        self.assertAlmostEqual(miles_to_kilometers(0.6213711922), 1, places=5)

    def test_temperature(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)

    def test_volume(self):
        self.assertAlmostEqual(milliliters_to_fluid_ounces(100), 3.38140386, places=5)
        self.assertAlmostEqual(fluid_ounces_to_milliliters(3.38140386), 100, places=5)
        self.assertAlmostEqual(liters_to_quarts(1), 1.0566887074, places=5)
        self.assertAlmostEqual(quarts_to_liters(1.0566887074), 1, places=5)

    def test_weight(self):
        self.assertAlmostEqual(grams_to_ounces(100), 3.52739907, places=5)
        self.assertAlmostEqual(ounces_to_grams(3.52739907), 100, places=5)
        self.assertAlmostEqual(kilograms_to_pounds(1), 2.2046244202, places=5)
        self.assertAlmostEqual(pounds_to_kilograms(2.2046244202), 1, places=5)

if __name__ == '__main__':
    unittest.main()
