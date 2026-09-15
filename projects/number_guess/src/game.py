import random

def generate_target(min_val: int = 1, max_val: int = 100) -> int:
    """Generates a random target number within the specified range."""
    return random.randint(min_val, max_val)

def evaluate_guess(secret: int, guess: int) -> str:
    """Compares the guess to the secret number and returns the result message."""
    if guess < secret:
        return "too low"
    elif guess > secret:
        return "too high"
    else:
        return "correct"

def play_round():
    """Handles a single round of the guessing game."""
    target = generate_target()
    print("\nI'm thinking of a number between 1 and 100.")
    
    while True:
        try:
            user_input = input("Enter your guess: ")
            guess = int(user_input)
        except ValueError:
            print("Please enter a valid integer.")
            continue

        result = evaluate_guess(target, guess)
        
        if result == "correct":
            print("Congratulations! You guessed it!")
            break
        else:
            print(f"Your guess was {result}.")

def main():
    """Main entry point for the game loop."""
    print("Welcome to the Number Guessing Game!")
    
    while True:
        play_round()
        
        choice = input("Would you like to play again? (y/n): ").strip().lower()
        if choice != 'y':
            print("Thanks for playing! Goodbye.")
            break

if __name__ == "__main__":
    main()
