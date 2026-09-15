package main

import "testing"

func TestGenerateTarget(t *testing.T) {
	for i := 0; i < 100; i++ {
		target := GenerateTarget()
		if target < 1 || target > 100 {
			t.Errorf("GenerateTarget() = %d; want value between 1 and 100", target)
		}
	}
}

func TestCompareGuess(t *testing.T) {
	tests := []struct {
		target int
		guess  int
		expected GuessResult
	}{
		{50, 25, TooLow},
		{50, 75, TooHigh},
		{50, 50, Correct},
		{1, 1, Correct},
		{100, 100, Correct},
		{100, 1, TooLow},
		{1, 100, TooHigh},
	}

	for _, tt := range tests {
		result := CompareGuess(tt.target, tt.guess)
		if result != tt.expected {
			t.Errorf("CompareGuess(%d, %d) = %v; want %v", tt.target, tt.guess, result, tt.expected)
		}
	}
}
