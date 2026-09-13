package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

// generateRandomNumber generates a random integer between min and max (inclusive).
func generateRandomNumber(min, max int) int {
	return rand.Intn(max-min+1) + min
}

// getGuess reads a guess from standard input.
func getGuess(reader *bufio.Reader) (int, error) {
	fmt.Print("Enter your guess (1-100): ")
	input, err := reader.ReadString('\n') // Read until newline

	if err != nil {
		return 0, err
	}

	// Trim whitespace and parse the input
	guessStr := strings.TrimSpace(input)

	guess, err := strconv.Atoi(guessStr)

	if err != nil {
		return 0, fmt.Errorf("invalid input: '%s' is not an integer", guessStr)
	}

	return guess, nil
}

func main() {
	// Seed the random number generator
	rand.Seed(time.Now().UnixNano())

	reader := bufio.NewReader(os.Stdin)

	fmt.Println("--- Welcome to the Number Guessing Game! ---")

	// Game loop for multiple rounds
	for {
		// 1. Select random number
		secretNumber := generateRandomNumber(1, 100)
		fmt.Println("\nA new game has started. I have picked a number between 1 and 100.")

		// 2. Get user guess
		guess, err := getGuess(reader)
		if err != nil {
			fmt.Printf("Error reading input: %v. Exiting.\n", err)
			break
		}

		// 3. Provide feedback
		if guess < secretNumber {
			fmt.Println("Too low! Try again.")
		} else if guess > secretNumber {
			fmt.Println("Too high! Try again.")
		} else {
			fmt.Println("Congratulations! You guessed the number correctly.")
		}

		// 4. Ask to play again
		fmt.Print("Do you want to play again? (yes/no): ")
		playAgainInput, err := reader.ReadString('\n') // Read until newline
		if err != nil {
			fmt.Printf("Error reading play again input: %v. Exiting.\n", err)
			break
		}
		playAgain := strings.ToLower(strings.TrimSpace(playAgainInput)) == "yes"

		if !playAgain {
		fmt.Println("Thanks for playing! Goodbye.")
			break
		}
	}
}
