import tkinter as tk
from tkinter import ttk, messagebox
from src.converter import CONVERSION_MAP

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tk Converter")
        self.root.geometry("400x300")
        
        self._setup_ui()

    def _setup_ui(self):
        """Initializes the GUI components."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=("N", "S", "E", "W"))

        # Conversion Type Selection
        ttk.Label(main_frame, text="Select Conversion:").grid(row=0, column=0, sticky="W", pady=5)
        self.conversion_var = tk.StringVar()
        self.combo = ttk.Combobox(main_frame, textvariable=self.conversion_var, state="readonly")
        # Extract names from CONVERSION_MAP values
        self.combo['values'] = [val[0] for val in CONVERSION_MAP.values()]
        self.combo.grid(row=0, column=1, columnspan=2, sticky="EW", pady=5)
        if self.combo['values']:
            self.combo.current(0)

        # Input Value
        ttk.Label(main_frame, text="Input Value:").grid(row=1, column=0, sticky="W", pady=5)
        self.input_entry = ttk.Entry(main_frame)
        self.input_entry.grid(row=1, column=1, columnspan=2, sticky="EW", pady=5)

        # Convert Button
        self.convert_button = ttk.Button(main_frame, text="Convert", command=self._perform_conversion)
        self.convert_button.grid(row=2, column=0, columnspan=3, pady=20)

        # Result Display
        ttk.Label(main_frame, text="Result:").grid(row=3, column=0, sticky="W", pady=5)
        self.result_label = ttk.Label(main_frame, text="---", font=("Helvetica", 10, "bold"))
        self.result_label.grid(row=3, column=1, columnspan=2, sticky="W", pady=5)

        main_frame.columnconfigure(1, weight=1)

    def _perform_conversion(self):
        """Handles the conversion logic when the button is clicked."""
        try:
            # Get selected conversion name
            selected_name = self.conversion_var.get()
            if not selected_name:
                raise ValueError("Please select a conversion type.")

            # Find the corresponding function from CONVERSION_MAP
            conversion_func = None
            for name, func in CONVERSION_MAP.values():
                if name == selected_name:
                    conversion_func = func
                    break
            
            if not conversion_func:
                raise ValueError("Conversion function not found.")

            # Get and validate input
            input_val_str = self.input_entry.get()
            if not input_val_str:
                raise ValueError("Please enter a value.")
            
            input_val = float(input_val_str)
            
            # Perform conversion
            result = conversion_func(input_val)
            
            # Display result
            self.result_label.config(text=f"{result:.4f}")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def main():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
