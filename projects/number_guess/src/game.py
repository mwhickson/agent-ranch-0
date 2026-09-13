import random
import sys

def generate_target() -> int:
    """Generates a random target number between 1 and 100."""
    return random.randint(1, 100)

def evaluate_guess(secret: int, guess: int) -> str:
    """Compares the guess to the secret number and returns feedback."""
    if guess < secret:
        return "Too low! Try a higher number."
    elif guess > secret:
        return "Too high! Try a lower number."
    else:
        return "Congratulations! You guessed the number correctly."

def play_round(secret: int) -> bool:
    """Handles a single round of the guessing game."""
    print("--- New Game Round ---")
    print("I have selected a number between 1 and 100. Can you guess it?")
    
    while True:
        try:
            guess_input = input("Enter your guess: ")
            guess = int(guess_input)
            
            if not (1 <= guess <= 100):
                print("Please enter a number between 1 and 100.")
                continue

            feedback = evaluate_guess(secret, guess)
            print(feedback)
            
            if "correctly" in feedback:
                return True  # Game won
            
        except ValueError:
            print("Invalid input. Please enter an integer.")

def main():
    """Main function to run the game loop."""
    while True:
        secret_number = generate_target()
        
        won = play_round(secret_number)
        
        if won:
            play_again = input("Would you like to play another round? (y/n): ").lower().strip()
            if play_again != 'y':
                print("Thanks for playing! Goodbye.")
                break
        else:
            # This path should ideally not be hit if play_round always returns True on win
            print("Round ended unexpectedly. Starting a new round.")

if __name__ == "__main__": # Added missing colon
    main()
