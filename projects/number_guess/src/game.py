import random

def generate_random_number():
    """Generates a random integer between 1 and 100 inclusive."""
    return random.randint(1, 100)

def main_game_loop():
    """Implements the core game loop structure for a single round."""
    print("--- Welcome to the Number Guessing Game! ---")
    secret_number = generate_random_number()
    attempts = 0
    guess = None

    while guess != secret_number:
        try:
            guess_input = input(f"Enter your guess (1-100): ")
            guess = int(guess_input)
            attempts += 1

            if guess < 1 or guess > 100:
                print("Please enter a number between 1 and 100.")
                continue

            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You guessed the number {secret_number} in {attempts} attempts.")
                break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def main():
    """Main application entry point to handle multiple game rounds."""
    while True:
        main_game_loop()
        
        # Ask user if they want to play again
        play_again = input("Do you want to play another round? (y/n): ").lower()
        if play_again != 'y':
            print("Thank you for playing! Goodbye.")
            break

if __name__ == "__main__":
    main()
