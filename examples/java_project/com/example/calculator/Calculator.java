package com.example.calculator;

/**
 * Calculator class provides simple arithmetic operations.
 *
 * This class implements basic calculator functionality including
 * addition, subtraction, multiplication, and division operations
 * with appropriate error handling.
 *
 * @author Example Team
 * @version 1.0.0
 */
public class Calculator {

    /**
     * Maximum allowed operand value to prevent overflow.
     */
    public static final int MAX_VALUE = Integer.MAX_VALUE;

    /**
     * Adds two integers.
     *
     * This method performs addition of two integer values and returns
     * the sum.
     *
     * @param a The first integer (addend)
     * @param b The second integer (addend)
     * @return The sum of a and b
     */
    public int add(int a, int b) {
        return a + b;
    }

    /**
     * Subtracts one integer from another.
     *
     * This method performs subtraction of the second integer from
     * the first integer.
     *
     * @param a The first integer (minuend)
     * @param b The second integer (subtrahend)
     * @return The difference of a and b (a - b)
     */
    public int subtract(int a, int b) {
        return a - b;
    }

    /**
     * Multiplies two integers.
     *
     * This method performs multiplication of two integer values and
     * returns the product.
     *
     * @param a The first integer (multiplicand)
     * @param b The second integer (multiplier)
     * @return The product of a and b
     */
    public int multiply(int a, int b) {
        return a * b;
    }

    /**
     * Divides one integer by another.
     *
     * This method performs division of the first integer by the second
     * integer. It throws an exception if division by zero is attempted.
     *
     * @param a The dividend
     * @param b The divisor
     * @return The quotient of a divided by b
     * @throws ArithmeticException If b is zero (division by zero)
     */
    public int divide(int a, int b) throws ArithmeticException {
        if (b == 0) {
            throw new ArithmeticException("Division by zero is not allowed");
        }
        return a / b;
    }

    /**
     * Calculates the modulo of two integers.
     *
     * This method returns the remainder when the first integer is divided
     * by the second integer.
     *
     * @param a The dividend
     * @param b The divisor
     * @return The remainder of a divided by b
     * @throws ArithmeticException If b is zero
     */
    public int modulo(int a, int b) throws ArithmeticException {
        if (b == 0) {
            throw new ArithmeticException("Modulo by zero is not allowed");
        }
        return a % b;
    }
}
