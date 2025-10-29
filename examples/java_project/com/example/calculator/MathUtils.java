package com.example.calculator;

/**
 * MathUtils provides advanced mathematical utility functions.
 *
 * This class contains static utility methods for common mathematical
 * operations that are not covered by the basic Calculator class.
 *
 * @author Example Team
 * @version 1.0.0
 */
public final class MathUtils {

    /**
     * Private constructor to prevent instantiation.
     *
     * This class is designed to be used as a utility class with
     * only static methods.
     */
    private MathUtils() {
        throw new UnsupportedOperationException("Utility class cannot be instantiated");
    }

    /**
     * Calculates the power of a number.
     *
     * This method raises the base to the power of the exponent.
     *
     * @param base The base number
     * @param exponent The exponent (must be non-negative)
     * @return The result of base raised to the power of exponent
     * @throws IllegalArgumentException If exponent is negative
     */
    public static int power(int base, int exponent) throws IllegalArgumentException {
        if (exponent < 0) {
            throw new IllegalArgumentException("Exponent must be non-negative");
        }

        int result = 1;
        for (int i = 0; i < exponent; i++) {
            result *= base;
        }
        return result;
    }

    /**
     * Calculates the factorial of a number.
     *
     * This method computes n! (n factorial), which is the product
     * of all positive integers less than or equal to n.
     *
     * @param n The number to calculate factorial for (must be non-negative)
     * @return The factorial of n
     * @throws IllegalArgumentException If n is negative
     */
    public static long factorial(int n) throws IllegalArgumentException {
        if (n < 0) {
            throw new IllegalArgumentException("Factorial is not defined for negative numbers");
        }

        long result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }

    /**
     * Checks if a number is prime.
     *
     * A prime number is a natural number greater than 1 that has
     * no positive divisors other than 1 and itself.
     *
     * @param n The number to check
     * @return true if n is prime, false otherwise
     */
    public static boolean isPrime(int n) {
        if (n <= 1) {
            return false;
        }
        if (n <= 3) {
            return true;
        }
        if (n % 2 == 0 || n % 3 == 0) {
            return false;
        }

        for (int i = 5; i * i <= n; i += 6) {
            if (n % i == 0 || n % (i + 2) == 0) {
                return false;
            }
        }
        return true;
    }

    /**
     * Calculates the greatest common divisor (GCD) of two numbers.
     *
     * This method uses the Euclidean algorithm to find the largest
     * positive integer that divides both numbers without a remainder.
     *
     * @param a The first number
     * @param b The second number
     * @return The greatest common divisor of a and b
     */
    public static int gcd(int a, int b) {
        a = Math.abs(a);
        b = Math.abs(b);

        while (b != 0) {
            int temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    }
}
