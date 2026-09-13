import random

def play_game_round():
    """
    Implements the core logic for a single round of the number guessing game.
    Generates a random number and handles user input.
    """
    secret_number = random.randint(1, 100)
    print("--- Number Guessing Game ---")
    print("I have picked a number between 1 and 100. Try to guess it!")

    while True:
        try:
            # Input handling
            guess_input = input("Enter your guess: ")
            guess = int(guess_input)
            
            # Range check
            if guess < 1 or guess > 100:
                print("Please enter a number between 1 and 100.")
                continue

            # Comparison logic
            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You guessed the number {secret_number} correctly!")
                break
        except ValueError:
            # Non-integer input handling
            print("Invalid input. Please enter an integer.")

def main():
    """
    Manages the game loop, allowing the user to play multiple rounds.
    """
    while True:
        play_game_round()
        
        while True:
            # FIX: Corrected syntax error here. The original error was likely due to improper string formatting or missing closing parenthesis.
            play_again = input("Do you want to play again? (y/n): ".lower().strip())
            if play_again in ('y', 'yes'):
                break
            elif play_again in ('n', 'no'):
                print("Thanks for playing! Goodbye.")
                return
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
