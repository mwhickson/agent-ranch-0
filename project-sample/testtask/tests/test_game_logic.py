import unittest
from unittest.mock import patch
from testtask.src.game_logic import compare_guess, generate_target_number

class TestGameLogic(unittest.TestCase):

    def test_compare_guess_too_low(self):
        # Target is 10, guess is 5
        self.assertEqual(compare_guess(10, 5), "Too low! Try again.")

    def test_compare_guess_too_high(self):
        # Target is 10, guess is 15
        self.assertEqual(compare_guess(10, 15), "Too high! Try again.")

    def test_compare_guess_correct(self):
        # Target is 10, guess is 10
        self.assertEqual(compare_guess(10, 10), "Congratulations! You guessed the number correctly.")

    @patch('testtask.src.game_logic.random.randint')
    def test_generate_target_number_range(self, mock_randint):
        # Mock randint to return a specific value, e.g., 42
        mock_randint.return_value = 42
        
        # Call the function
        result = generate_target_number()
        
        # Assert it called randint with the correct bounds (1, 100)
        mock_randint.assert_called_once_with(1, 100)
        # Assert the returned value is correct
        self.assertEqual(result, 42)

if __name__ == '__main__':
    unittest.main()
