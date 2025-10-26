// Package calculator provides simple arithmetic operations.
//
// This package implements basic calculator functionality including
// addition, subtraction, multiplication, and division operations
// with appropriate error handling.
package calculator

import "errors"

// Add returns the sum of two integers.
//
// Parameters:
//   - a: The first integer
//   - b: The second integer
//
// Returns the sum of a and b.
func Add(a, b int) int {
	return a + b
}

// Subtract returns the difference between two integers.
//
// Parameters:
//   - a: The first integer (minuend)
//   - b: The second integer (subtrahend)
//
// Returns the result of a - b.
func Subtract(a, b int) int {
	return a - b
}

// Multiply returns the product of two integers.
//
// Parameters:
//   - a: The first integer
//   - b: The second integer
//
// Returns the product of a and b.
func Multiply(a, b int) int {
	return a * b
}

// Divide returns the quotient of two integers.
//
// Parameters:
//   - a: The dividend
//   - b: The divisor
//
// Returns the quotient and an error if division by zero is attempted.
func Divide(a, b int) (int, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}
