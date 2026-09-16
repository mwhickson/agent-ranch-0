"""
CLI Test Harness for the Converter Library.
Provides an interactive interface for performing unit conversions.
"""
import sys
from src.converter import CONVERSION_MAP

def run_cli():
    """
    Runs the interactive CLI loop.
    """
    print("--- Converter Library CLI Test Harness ---")
    
    while True:
        print("\nAvailable Conversions:")
        for key, (name, _) in CONVERSION_MAP.items():
            print(f"{key}. {name}")
        print("Q. Quit")

        choice = input("\nSelect a conversion number (or 'Q' to quit): ").strip().upper()

        if choice == 'Q':
            print("Exiting CLI. Goodbye!")
            break

        if choice not in CONVERSION_MAP:
            print("Invalid selection. Please try again.")
            continue

        conversion_name, conversion_func = CONVERSION_MAP[choice]
        
        try:
            user_input = input(f"Enter the value to convert ({conversion_name}): ").strip()
            # Convert input to float for the conversion function
            value = float(user_input)
            
            result = conversion_func(value)
            print(f"\nResult: {value} -> {result:.6f}")
            
        except ValueError as e:
            # This catches both float conversion errors and the library's _validate_input errors
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_cli()
