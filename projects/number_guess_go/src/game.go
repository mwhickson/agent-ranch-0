package main

import (
	"fmt"
	"math/rand"
	"time"
)

type GuessResult int

const (
	TooLow GuessResult = iota
	TooHigh
	Correct
)

// GenerateTarget returns a random number between 1 and 100.
func GenerateTarget() int {
	// Using a local random source to avoid global state issues if needed,
	// but for this simple implementation, we'll use the global one seeded in main.
	return rand.Intn(100) + 1
}

// CompareGuess compares the guess with the target and returns the result.
func CompareGuess(target, guess int) GuessResult {
	if guess < target {
		return TooLow
	} else if guess > target {
		return TooHigh
	}
	return Correct
}

// PlayRound handles the I/O for a single round of the game.
func PlayRound(target int) error {
	fmt.Printf("\nI'm thinking of a number between 1 and 100.\n")

	for {
		var guess int
		fmt.Print("Enter your guess: ")
		_, err := fmt.Scan(&guess)
		if err != nil {
			return fmt.Errorf("invalid input: please enter an integer")
		}

		result := CompareGuess(target, guess)
		switch result {
		case TooLow:
			fmt.Println("Too low! Try again.")
		case TooHigh:
			fmt.Println("Too high! Try again.")
		case Correct:
			fmt.Printf("Congratulations! You guessed it: %d\n", target)
			return nil
		}
	}
}

func main() {
	rand.Seed(time.Now().UnixNano())

	for {
		target := GenerateTarget()
		err := PlayRound(target)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			break
		}

		var choice string
		fmt.Print("Would you like to play again? (y/n): ")
		fmt.Scan(&choice)
		if choice != "y" && choice != "Y" {
			fmt.Println("Thanks for playing!")
			break
		}
	}
}
