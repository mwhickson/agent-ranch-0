"""
Converter Library
Provides various unit conversion routines for distance, temperature, volume, and weight.
"""

from typing import Union

def _validate_input(value: Union[int, float]) -> float:
    """Validates that the input is a number."""
    if not isinstance(value, (int, float)):
        raise ValueError(f"Invalid input type: {type(value).__name__}. Expected number.")
    return float(value)

# --- Distance Conversions ---

def meters_to_feet(meters: float) -> float:
    return _validate_input(meters) * 3.280839895

def feet_to_meters(feet: float) -> float:
    return _validate_input(feet) / 3.280839895

def kilometers_to_miles(kilometers: float) -> float:
    return _validate_input(kilometers) * 0.6213711922

def miles_to_kilometers(miles: float) -> float:
    return _validate_input(miles) / 0.6213711922

# --- Temperature Conversions ---

def celsius_to_fahrenheit(celsius: float) -> float:
    return (_validate_input(celsius) * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (_validate_input(fahrenheit) - 32) * 5/9

# --- Volume Conversions ---

def milliliters_to_fluid_ounces(milliliters: float) -> float:
    return _validate_input(milliliters) * 0.0338140386

def fluid_ounces_to_milliliters(fluid_ounces: float) -> float:
    return _validate_input(fluid_ounces) / 0.0338140386

def liters_to_quarts(liters: float) -> float:
    return _validate_input(liters) * 1.0566887074

def quarts_to_liters(quarts: float) -> float:
    return _validate_input(quarts) / 1.0566887074

# --- Weight Conversions ---

def grams_to_ounces(grams: float) -> float:
    return _validate_input(grams) * 0.0352739907

def ounces_to_grams(ounces: float) -> float:
    return _validate_input(ounces) / 0.0352739907

def kilograms_to_pounds(kilograms: float) -> float:
    return _validate_input(kilograms) * 2.2046244202

def pounds_to_kilograms(pounds: float) -> float:
    return _validate_input(pounds) / 2.2046244202

# Mapping for CLI harness
CONVERSION_MAP = {
    "1": ("Meters to Feet", meters_to_feet),
    "2": ("Feet to Meters", feet_to_meters),
    "3": ("Kilometers to Miles", kilometers_to_miles),
    "4": ("Miles to Kilometers", miles_to_kilometers),
    "5": ("Celsius to Fahrenheit", celsius_to_fahrenheit),
    "6": ("Fahrenheit to Celsius", fahrenheit_to_celsius),
    "7": ("Milliliters to Fluid Ounces", milliliters_to_fluid_ounces),
    "8": ("Fluid Ounces to Milliliters", fluid_ounces_to_milliliters),
    "9": ("Liters to Quarts", liters_to_quarts),
    "10": ("Quarts to Liters", quarts_to_liters),
    "11": ("Grams to Ounces", grams_to_ounces),
    "12": ("Ounces to Grams", ounces_to_grams),
    "13": ("Kilograms to Pounds", kilograms_to_pounds),
    "14": ("Pounds to Kilograms", pounds_to_kilograms),
}
