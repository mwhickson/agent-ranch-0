import unittest
from src.game import generate_target, evaluate_guess

class TestGame(unittest.TestCase):
    def test_evaluate_too_low(self):
        self.assertEqual(evaluate_guess(50, 20), 'Too low! Try a higher number.')

    def test_evaluate_too_high(self):
        self.assertEqual(evaluate_guess(50, 80), 'Too high! Try a lower number.')

    def test_evaluate_correct(self):
        self.assertEqual(evaluate_guess(50, 50), 'Congratulations! You guessed the number correctly.')

    def test_generate_target_range(self):
        # Test multiple times to ensure randomness stays within bounds
        for _ in range(100):
            target = generate_target()
            self.assertIsInstance(target, int)
            self.assertTrue(1 <= target <= 100)

if __name__ == '__main__':
    unittest.main()
