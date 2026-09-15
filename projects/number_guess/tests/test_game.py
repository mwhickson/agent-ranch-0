import unittest
from src.game import generate_target, evaluate_guess

class TestGame(unittest.TestCase):
    def test_generate_target_range(self):
        for _ in range(100):
            target = generate_target(1, 10)
            self.assertTrue(1 <= target <= 10)

    def test_evaluate_guess_low(self):
        self.assertEqual(evaluate_guess(50, 25), "too low")
        self.assertEqual(evaluate_guess(50, 49), "too low")

    def test_evaluate_guess_high(self):
        self.assertEqual(evaluate_guess(50, 75), "too high")
        self.assertEqual(evaluate_guess(50, 51), "too high")

    def test_evaluate_guess_correct(self):
        self.assertEqual(evaluate_guess(50, 50), "correct")

if __name__ == '__main__':
    unittest.main()
