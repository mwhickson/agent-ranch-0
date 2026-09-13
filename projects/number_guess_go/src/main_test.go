package main

import (
	"testing"
)

func TestGenerateRandomNumber(t *testing.T) {
	// Test lower bound
	min := 1
	max := 100
	for i := 0; i < 100; i++ {
		num := generateRandomNumber(min, max)
		if num < min || num > max {
			 t.Errorf("generateRandomNumber(%d, %d) returned %d, expected in range [%d, %d]", min, max, num, min, max)
		}
	}

	// Test upper bound
	for i := 0; i < 100; i++ {
		num := generateRandomNumber(min, max)
		if num < min || num > max {
			 t.Errorf("generateRandomNumber(%d, %d) returned %d, expected in range [%d, %d]", min, max, num, min, max)
		}
	}
}
