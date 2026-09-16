# Converter Library - Project Specification

## Overview

The Converter Library is a Python library intended to be used in other Python software projects.

The Converter Library is intended to be flexible, and makes no assumption about how it will be used -- HOWEVER, functions are expected to fail gracefully if called with invalid arguments, and to use appropriate error handling without disrupting the program flow of calling program. Meaningful error messages should be provided in the event of an error relating to bad data.

The Converter Library will feature the following conversion routines:

- **distance:** Meters to Feet; Feet to Meters; Kilometers to Miles; Miles to Kilometers
- **temperature:** Celsius to Fahrenheit; Fahrenheit to Celsius
- **volume:** Milliliters to Fluid Ounces; Fluid Ounces to Milliliters; Liters to US Quarts; US Quarts to Liters
- **weight:** Grams to Ounces; Ounces to Grams; Kilograms to Pounds; Pounds to Kilograms

Conversions should be performed using the simplest correct formula.

A command-line test harness should be made available to perform conversions. The harness should include the ability to select a conversion, enter the value to be converte then trigger the conversion to see the result.

### Formulas

| From | To | Formula |
| - | - | - |
| Meters | Feet | {Meters} * 3.280839895 |
| Feet | Meters | {Feet} / 3.280839895 |
| Kilometers | Miles | {Kilometers} * 0.6213711922 |
| Miles | Kilometers | {Miles} / 0.6213711922 |
| Celsius | Fahrenheit | {Fahrenheit} = ({Celsius} * 9/5) + 32 |
| Fahrenheit | Celsius | {Celsius} = ({Fahrenheit} - 32) * 5/9 |
| Milliliters | Fluid Ounces | {Milliliters} * 0.0338140386 |
| Fluid Ounces | Milliliters | {Fluid Ounces} / 0.0338140386 |
| Liters | Quarts | {Liters} * 1.0566887074 |
| Quarts | Liters | {Quarts} / 1.0566887074 |
| Grams | Ounces | {Grams} * 0.0352739907 |
| Ounces | Grams | {Ounces} / 0.0352739907 |
| Kilograms | Pounds | {Kilograms} * 2.2046244202 |
| Pounds | Kilograms | {Pounds} / 2.2046244202 |

### Example Conversions

For reference, see the following equivalency measures.

| Conversion | Source Units | Converted Units | Formula |
| - | - | - |
| Meters to Feet | 1 | 3.280839895 |
| Feet to Meters | 1 | 0.3048 |
| Kilometers to Miles | 1 | 0.6213711922 |
| Miles to Kilometers | 1 | 1.609344 |
| Celsius to Fahrenheit | -40 | -40 |
| Celsius to Fahrenheit | 0 | 32 |
| Celsius to Fahrenheit | 100 | 212 |
| Fahrenheit to Celsius | -40 | -40 |
| Fahrenheit to Celsius | 32 | 0 |
| Fahrenheit to Celsius | 212 | 100 |
| Milliliters to Fluid Ounces | 1 | 0.0338140386 |
| Fluid Ounces to Milliliters | 1 | 29.573515625 |
| Liters to Quarts | 1 | 1.0566887074 |
| Quarts to Liters | 1 | 0.9463525 |
| Grams to Ounces | 1 | 0.0352739907 |
| Ounces to Grams | 1 | 28.3495 |
| Kilograms to Pounds | 1 | 2.2046244202 |
| Pounds to Kilograms | 1 | 0.453592 |

## Configuration
<!-- AR0_CONFIG: API_URL=http://localhost:5001/v1/chat/completions -->

---

## Technical Stack

### Approved
* **Languages & Runtimes:** Python, Bash

### Prohibited
* **Remote Network Access:** Strictly forbidden by default. Remote resources may only be accessed via local network bridges explicitly authorized by the Human Orchestrator.

---

## Execution Guidelines

1. **Output Standard:** Prioritize human-readable, human-verifiable, and machine-reproducible artifacts over dense black-box outputs.
