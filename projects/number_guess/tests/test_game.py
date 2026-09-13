import unittest
from src.game import generate_random_number

class TestGame(unittest.TestCase):
    def test_generate_random_number_range(self):
        for _ in range(100): 
            self.assertGreaterEqual(generate_random_number(), 1)
            self.assertLessEqual(generate_random_number(), 100)
