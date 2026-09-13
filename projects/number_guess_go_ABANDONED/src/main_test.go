package main

import (
	"testing"
)

func TestGenerateRandomNumber(t *testing.T) {
	// Test boundaries for min=1, max=100
	// Since rand is seeded globally, we test a few iterations to check range.
	for i := 0; i < 1000; i++ {
		num := generateRandomNumber(1, 100)
		if num < 1 || num > 100 {
			t.Errorf("generateRandomNumber(%d, %d) returned %d, which is out of range [1, 100]", 1, 100, num)
		}
	}
}
