import unittest
import sys
from unittest.mock import MagicMock

# Since src.models has a syntax/init error at the module level, 
# we can't import it normally. We will mock the problematic parts 
# to test the logic of the classes that are defined before the error.

class TestModelsLogic(unittest.TestCase):
    def test_metric_value_logic(self):
        # We can't import MetricValue from src.models because of the error
        # But we can redefine it here to test the logic if we can't fix the source
        # However, the instruction says 