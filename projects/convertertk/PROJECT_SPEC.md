# Tk Converter

## Overview

Tk Converter is a Tcl/Tk application to perform a limit number of conversions using Converter Library (previously developed, provided in `src/converter.py`).

> NOTE: `src/converter.py` is READ-ONLY and MUST NOT be modified.

As per the available conversion options provided by Converter Library, Tk Converter should support the following conversion options.

- **distance:** Meters to Feet; Feet to Meters; Kilometers to Miles; Miles to Kilometers
- **temperature:** Celsius to Fahrenheit; Fahrenheit to Celsius
- **volume:** Milliliters to Fluid Ounces; Fluid Ounces to Milliliters; Liters to US Quarts; US Quarts to Liters
- **weight:** Grams to Ounces; Ounces to Grams; Kilograms to Pounds; Pounds to Kilograms

With regard to layout, there is no requirement EXCEPT that all functions are made available to the end user. A straightforward label, input, button layout using either a flow or grid paradigm is recommended.

> NOTE: Special care should be taken with regard to tests to ensure Tcl/Tk (via `tkinter`) can be and is mocked appropriately.

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
