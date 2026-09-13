package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"time"
)

// generateRandomNumber selects a random integer between min (inclusive) and max (inclusive).
func generateRandomNumber(min, max int) int {
	// Seed the random number generator
	// NOTE: Seeding inside a function called repeatedly can lead to the same seed if called too fast.
	// For a simple console game, this is acceptable, but for robust testing, seeding should be done once in main.
	rand.Seed(time.Now().UnixNano())
	// Generate a random number in the range [min, max]
	return rand.Intn(max-min+1) + min
}

// playRound handles a single round of the number guessing game.
// It returns true if the guess was correct, false otherwise.
func playRound() bool {
	// 1. Generate the secret number (1 to 100)
	secretNumber := generateRandomNumber(1, 100)

	// 2. Prompt user for input	fmt.Printf("Welcome to the Number Guessing Game! I have selected a number between 1 and 100.\n")
	fmt.Println("Please enter your guess:")
	reader := bufio.NewReader(os.Stdin)
	input, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("Error reading input. Round ended.")
		return false
	}
	guessStr := input
	guess, err := strconv.Atoi(guessStr)
	if err != nil {
		fmt.Printf("Invalid input: '%s'. Please enter an integer. Round ended.\n", guessStr)
		return false
	}
	
	// 3. Comparison logic
	if guess < 1 || guess > 100 {
		fmt.Printf("Your guess must be between 1 and 100. Try again.\n")
		return false
	}

	if guess == secretNumber {
		fmt.Printf("Congratulations! You guessed the number %d correctly!\n", secretNumber)
		return true // Correct guess, continue to next round
	}

	if guess < secretNumber {
		fmt.Printf("Too low! Try again.\n")
		return false // Incorrect guess, end round
	}

	// If guess > secretNumber
	fmt.Printf("Too high! Try again.\n")
	return false // Incorrect guess, end round
}

func main() {
	keepPlaying := true
	for keepPlaying {
		if playRound() {
			// If playRound returns true, the user guessed correctly, so we ask to play again.
			fmt.Println("----------------------------------------")
			var playAgain string
			// Read the entire line for the play again prompt
			 fmt.Print("Do you want to play another round? (y/n): ")
			 reader := bufio.NewReader(os.Stdin)
			 playAgain, err := reader.ReadString('\n')
			 if err != nil {
				keepPlaying = false
				continue
			} 
			 
			 // Check if the first character is 'y' or 'Y' (case-insensitive check on the first char)
			 if len(playAgain) > 0 && (playAgain[0] == 'y' || playAgain[0] == 'Y') {
				// Continue loop
			} else {
				keepPlaying = false // Exit condition if not 'y'
			}
		} else {
			// If playRound returns false, the round ended (wrong guess or invalid input)
			fmt.Println("----------------------------------------")
			var playAgain string
			// Read the entire line for the play again prompt
			 fmt.Print("Do you want to play another round? (y/n): ")
			 reader := bufio.NewReader(os.Stdin)
			 playAgain, err := reader.ReadString('\n')
			 if err != nil {
				keepPlaying = false
				continue
			} 
			 
			 // Check if the first character is 'y' or 'Y' (case-insensitive check on the first char)
			 if len(playAgain) > 0 && (playAgain[0] == 'y' || playAgain[0] == 'Y') {
				// Continue loop
			} else {
				keepPlaying = false // Exit condition if not 'y'
			}
		}
	}
	fmt.Println("Thank you for playing! Goodbye.")
}
