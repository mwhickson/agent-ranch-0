import random

def generate_target_number() -> int:
    """
    Generates a random integer between 1 and 100 (inclusive).

    Returns:
        int: The secret target number.
    """
    return random.randint(1, 100)

def compare_guess(target: int, guess: int) -> str:
    """
    Compares the user's guess against the target number.

    Args:
        target: The secret number.
        guess: The user's guess.

    Returns:
        str: A message indicating if the guess was correct, too high, or too low.
    """
    if guess < target:
        return "Too low! Try again."
    elif guess > target:
        return "Too high! Try again."
    else:
        return "Congratulations! You guessed the number correctly."

def play_game():
    """
    Runs the main number guessing game loop.
    """
    while True:
        target = generate_target_number()
        print("=========================================")
        print("Welcome to the Number Guessing Game!")
        print("I have picked a number between 1 and 100. Can you guess it?")
        print("=========================================")

        while True:
            try:
                guess_input = input("Enter your guess: ")
                guess = int(guess_input)
                
                feedback = compare_guess(target, guess)
                print(f"Feedback: {feedback}")

                if "Congratulations! You guessed the number correctly." in feedback:
                    print(f"You won! The target number was {target}.")
                    break
            except ValueError:
                print("Invalid input. Please enter a whole number.")

        play_again = input("Do you want to play again? (y/n): ").lower()
        if play_again != 'y':
            print("Thanks for playing! Goodbye.")
            break

if __name__ == '__main__':
    play_game()
