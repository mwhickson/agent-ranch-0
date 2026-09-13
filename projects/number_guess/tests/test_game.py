import unittest
from unittest.mock import patch, call
from src.game import main

class TestGameMain(unittest.TestCase):

    @patch('src.game.play_game_round')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_plays_multiple_rounds_and_exits_on_n(self, mock_print, mock_input, mock_play_round) 
        # Setup input sequence: Guess 1 (Win), Play Again: n
        # Input sequence: Guess 1, Play Again: n
        mock_input.side_effect = ['50', 'n']

        # Mock play_game_round to return immediately after the first call
        # Since play_game_round runs inside the main loop, we need to mock its behavior across multiple calls.
        # For this test, we simulate one successful round and then the exit condition.
        mock_play_round.side_effect = [None] # First call returns None (or whatever it returns, doesn't matter much here)

        main() 

        # Check if play_game_round was called at least once
        mock_play_round.assert_called_once()
        
        # Check if the exit message was printed
        mock_print.assert_any_call("Thanks for playing! Goodbye.")
        
    @patch('src.game.play_game_round')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_plays_multiple_rounds_and_continues_on_y(self, mock_print, mock_input, mock_play_round) 
        # Setup input sequence: Guess 1 (Win), Play Again: y
        # Input sequence: Guess 1, Play Again: y
        mock_input.side_effect = ['50', 'y']

        # Mock play_game_round to return immediately after the first call
        mock_play_round.side_effect = [None] 

        main() 

        # Check if play_game_round was called at least once
        mock_play_round.assert_called_once()
        
        # Check if the loop continued (implicitly by not exiting)
        # We check that the setup print for the game is present
        mock_print.assert_any_call("--- Number Guessing Game ---") 

    @patch('src.game.play_game_round')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_handles_invalid_play_again_input(self, mock_print, mock_input, mock_play_round) 
        # Setup input sequence: Guess 1 (Win), Play Again: invalid
        # Input sequence: Guess 1, Play Again: invalid_string
        mock_input.side_effect = ['50', 'maybe']

        # Mock play_game_round to return immediately after the first call
        mock_play_round.side_effect = [None] 

        main() 

        # Check if the invalid input message was printed
        mock_print.assert_any_call("Invalid input. Please enter 'y' or 'n'.")

if __name__ == '__main__': 
    unittest.main()
