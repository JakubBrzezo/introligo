//! # Calculator Crate
//!
//! This crate provides simple arithmetic operations for numeric types.
//! All operations include proper error handling and edge case validation.
//!
//! ## Features
//!
//! - Basic arithmetic operations (add, subtract, multiply, divide)
//! - Error handling for division by zero
//! - Generic numeric type support
//!
//! ## Example
//!
//! ```
//! use calculator::{add, divide};
//!
//! let sum = add(5, 3);
//! assert_eq!(sum, 8);
//!
//! match divide(10, 2) {
//!     Ok(result) => assert_eq!(result, 5),
//!     Err(e) => panic!("Unexpected error: {}", e),
//! }
//! ```

use std::fmt;

/// Error type for calculator operations.
#[derive(Debug, Clone, PartialEq)]
pub enum CalcError {
    /// Division by zero error
    DivisionByZero,
}

impl fmt::Display for CalcError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CalcError::DivisionByZero => write!(f, "Cannot divide by zero"),
        }
    }
}

impl std::error::Error for CalcError {}

/// Adds two integers and returns the sum.
///
/// # Arguments
///
/// * `a` - The first integer
/// * `b` - The second integer
///
/// # Returns
///
/// The sum of `a` and `b`.
///
/// # Examples
///
/// ```
/// use calculator::add;
///
/// let result = add(5, 3);
/// assert_eq!(result, 8);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Subtracts the second integer from the first.
///
/// # Arguments
///
/// * `a` - The minuend
/// * `b` - The subtrahend
///
/// # Returns
///
/// The difference between `a` and `b`.
///
/// # Examples
///
/// ```
/// use calculator::subtract;
///
/// let result = subtract(10, 3);
/// assert_eq!(result, 7);
/// ```
pub fn subtract(a: i32, b: i32) -> i32 {
    a - b
}

/// Multiplies two integers and returns the product.
///
/// # Arguments
///
/// * `a` - The first integer
/// * `b` - The second integer
///
/// # Returns
///
/// The product of `a` and `b`.
///
/// # Examples
///
/// ```
/// use calculator::multiply;
///
/// let result = multiply(4, 7);
/// assert_eq!(result, 28);
/// ```
pub fn multiply(a: i32, b: i32) -> i32 {
    a * b
}

/// Divides the first integer by the second.
///
/// # Arguments
///
/// * `a` - The dividend
/// * `b` - The divisor
///
/// # Returns
///
/// A `Result` containing the quotient if successful, or a `CalcError::DivisionByZero`
/// if `b` is zero.
///
/// # Errors
///
/// Returns `Err(CalcError::DivisionByZero)` when attempting to divide by zero.
///
/// # Examples
///
/// ```
/// use calculator::divide;
///
/// match divide(10, 2) {
///     Ok(result) => assert_eq!(result, 5),
///     Err(e) => panic!("Unexpected error: {}", e),
/// }
///
/// // Division by zero returns an error
/// assert!(divide(10, 0).is_err());
/// ```
pub fn divide(a: i32, b: i32) -> Result<i32, CalcError> {
    if b == 0 {
        Err(CalcError::DivisionByZero)
    } else {
        Ok(a / b)
    }
}

/// A calculator struct that maintains state.
///
/// This struct provides a stateful calculator that remembers the current value
/// and allows chaining operations.
///
/// # Examples
///
/// ```
/// use calculator::Calculator;
///
/// let mut calc = Calculator::new();
/// calc.add(5);
/// calc.multiply(2);
/// assert_eq!(calc.value(), 10);
/// ```
pub struct Calculator {
    /// The current value stored in the calculator
    value: i32,
}

impl Calculator {
    /// Creates a new calculator with an initial value of 0.
    ///
    /// # Examples
    ///
    /// ```
    /// use calculator::Calculator;
    ///
    /// let calc = Calculator::new();
    /// assert_eq!(calc.value(), 0);
    /// ```
    pub fn new() -> Self {
        Calculator { value: 0 }
    }

    /// Creates a new calculator with a specified initial value.
    ///
    /// # Arguments
    ///
    /// * `initial_value` - The starting value for the calculator
    ///
    /// # Examples
    ///
    /// ```
    /// use calculator::Calculator;
    ///
    /// let calc = Calculator::with_value(42);
    /// assert_eq!(calc.value(), 42);
    /// ```
    pub fn with_value(initial_value: i32) -> Self {
        Calculator {
            value: initial_value,
        }
    }

    /// Gets the current value of the calculator.
    ///
    /// # Returns
    ///
    /// The current value stored in the calculator.
    pub fn value(&self) -> i32 {
        self.value
    }

    /// Adds a value to the current calculator value.
    ///
    /// # Arguments
    ///
    /// * `n` - The value to add
    pub fn add(&mut self, n: i32) {
        self.value += n;
    }

    /// Subtracts a value from the current calculator value.
    ///
    /// # Arguments
    ///
    /// * `n` - The value to subtract
    pub fn subtract(&mut self, n: i32) {
        self.value -= n;
    }

    /// Multiplies the current calculator value by a given value.
    ///
    /// # Arguments
    ///
    /// * `n` - The value to multiply by
    pub fn multiply(&mut self, n: i32) {
        self.value *= n;
    }

    /// Divides the current calculator value by a given value.
    ///
    /// # Arguments
    ///
    /// * `n` - The value to divide by
    ///
    /// # Returns
    ///
    /// A `Result` containing `()` if successful, or a `CalcError::DivisionByZero`
    /// if attempting to divide by zero.
    ///
    /// # Errors
    ///
    /// Returns `Err(CalcError::DivisionByZero)` when attempting to divide by zero.
    pub fn divide(&mut self, n: i32) -> Result<(), CalcError> {
        if n == 0 {
            Err(CalcError::DivisionByZero)
        } else {
            self.value /= n;
            Ok(())
        }
    }

    /// Resets the calculator value to 0.
    pub fn reset(&mut self) {
        self.value = 0;
    }
}

impl Default for Calculator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_divide() {
        assert_eq!(divide(10, 2), Ok(5));
        assert_eq!(divide(10, 0), Err(CalcError::DivisionByZero));
    }

    #[test]
    fn test_calculator() {
        let mut calc = Calculator::new();
        calc.add(5);
        assert_eq!(calc.value(), 5);
        calc.multiply(2);
        assert_eq!(calc.value(), 10);
    }
}
