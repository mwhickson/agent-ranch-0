import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock tkinter before importing app
mock_tk = MagicMock()
mock_ttk = MagicMock()
mock_messagebox = MagicMock()
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = mock_ttk
sys.modules['tkinter.messagebox'] = mock_messagebox

from src.app import ConverterApp

class TestConverterGUI(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        # Mock the widgets created in _setup_ui
        # We need to mock the config method specifically to track calls
        self.app = ConverterApp(self.root)
        
        # Manually patch the widgets in the app instance to be controlled mocks
        self.app.result_label = MagicMock()
        self.app.result_label.config = MagicMock()
        self.app.input_entry = MagicMock()
        self.app.input_entry.get = MagicMock()
        self.app.conversion_var = MagicMock()
        self.app.conversion_var.get = MagicMock()
        self.app.convert_button = MagicMock()
        # Mock the invoke method to actually call the command
        self.app.convert_button.invoke = lambda: self.app._perform_conversion()

    def test_initial_state(self):
        # The constructor calls _setup_ui. We check if title was set.
        self.root.title.assert_called_with("Tk Converter")

    def test_successful_conversion_workflow(self):
        # Setup mock return values
        self.app.conversion_var.get.return_value = "Celsius to Fahrenheit"
        self.app.input_entry.get.return_value = "100"
        
        # Trigger conversion
        self.app.convert_button.invoke()
        
        # Verify result label was updated with 212.0000
        self.app.result_label.config.assert_called_with(text="212.0000")

    @patch('src.app.messagebox.showerror')
    def test_invalid_input_error(self, mock_showerror):
        self.app.conversion_var.get.return_value = "Meters to Feet"
        self.app.input_entry.get.return_value = "abc"
        
        self.app.convert_button.invoke()
        
        mock_showerror.assert_called_once()

    @patch('src.app.messagebox.showerror')
    def test_no_selection_error(self, mock_showerror):
        self.app.conversion_var.get.return_value = ""
        self.app.input_entry.get.return_value = "10"
        
        self.app.convert_button.invoke()
        
        mock_showerror.assert_called_once()

if __name__ == '__main__':
    unittest.main()
