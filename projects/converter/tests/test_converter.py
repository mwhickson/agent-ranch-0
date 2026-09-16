import unittest
from src.converter import (
    meters_to_feet, feet_to_meters, kilometers_to_miles, miles_to_kilometers,
    celsius_to_fahrenheit, fahrenheit_to_celsius,
    milliliters_to_fluid_ounces, fluid_ounces_to_milliliters,
    liters_to_quarts, quarts_to_liters,
    grams_to_ounces, ounces_to_grams,
    kilograms_to_pounds, pounds_to_kilograms,
    _validate_input
)

class TestConverter(unittest.TestCase):
    def test_distance(self):
        self.assertAlmostEqual(meters_to_feet(1), 3.280839895)
        self.assertAlmostEqual(feet_to_meters(1), 1/3.280839895)
        self.assertAlmostEqual(kilometers_to_miles(1), 0.6213711922)
        self.assertAlmostEqual(miles_to_kilometers(1), 1/0.6213711922)

    def test_temperature(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212)
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)
        self.assertAlmostEqual(celsius_to_fahrenheit(-40), -40)

    def test_volume(self):
        self.assertAlmostEqual(milliliters_to_fluid_ounces(1), 0.0338140386)
        self.assertAlmostEqual(fluid_ounces_to_milliliters(1), 1/0.0338140386)
        self.assertAlmostEqual(liters_to_quarts(1), 1.0566887074)
        self.assertAlmostEqual(quarts_to_liters(1), 1/1.0566887074)

    def test_weight(self):
        self.assertAlmostEqual(grams_to_ounces(1), 0.0352739907)
        self.assertAlmostEqual(ounces_to_grams(1), 1/0.0352739907)
        self.assertAlmostEqual(kilograms_to_pounds(1), 2.2046244202)
        self.assertAlmostEqual(pounds_to_kilograms(1), 1/2.2046244202)

    def test_validation(self):
        self.assertEqual(_validate_input(10), 10.0)
        self.assertEqual(_validate_input(10.5), 10.5)
        with self.assertRaises(ValueError):
            _validate_input("not a number")

if __name__ == '__main__':
    unittest.main()
