/**
 * @file calculator.h
 * @brief Simple calculator library for basic arithmetic operations
 * @author Example Project
 * @date 2025
 *
 * This header defines a simple calculator API with basic arithmetic operations.
 */

#ifndef CALCULATOR_H
#define CALCULATOR_H

/**
 * @brief Add two numbers
 * @param a First number
 * @param b Second number
 * @return Sum of a and b
 */
int add(int a, int b);

/**
 * @brief Subtract two numbers
 * @param a First number
 * @param b Second number
 * @return Difference of a and b
 */
int subtract(int a, int b);

/**
 * @brief Multiply two numbers
 * @param a First number
 * @param b Second number
 * @return Product of a and b
 */
int multiply(int a, int b);

/**
 * @brief Divide two numbers
 * @param a Dividend
 * @param b Divisor
 * @return Quotient of a divided by b, or 0 if b is 0
 * @note Returns 0 if division by zero is attempted
 */
int divide(int a, int b);

#endif // CALCULATOR_H
