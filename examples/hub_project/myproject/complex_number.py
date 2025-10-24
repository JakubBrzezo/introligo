"""Complex Number implementation for demonstration purposes.

This module provides a ComplexNumber class that represents complex numbers
and supports basic arithmetic operations.
"""

import math
from typing import Union


class ComplexNumber:
    """A class representing a complex number in the form a + bi.

    This class provides methods for basic arithmetic operations on complex numbers,
    including addition, subtraction, multiplication, and division. It also includes
    utility methods for calculating magnitude, phase, and conjugate.

    Attributes:
        real (float): The real part of the complex number.
        imag (float): The imaginary part of the complex number.

    Examples:
        >>> z1 = ComplexNumber(3, 4)
        >>> z2 = ComplexNumber(1, 2)
        >>> z3 = z1 + z2
        >>> print(z3)
        4.0 + 6.0i
        >>> print(z1.magnitude())
        5.0
    """

    def __init__(self, real: float = 0.0, imag: float = 0.0):
        """Initialize a complex number.

        Args:
            real: The real part of the complex number. Defaults to 0.0.
            imag: The imaginary part of the complex number. Defaults to 0.0.

        Examples:
            >>> z = ComplexNumber(3, 4)
            >>> z.real
            3.0
            >>> z.imag
            4.0
        """
        self.real = float(real)
        self.imag = float(imag)

    def __add__(self, other: Union["ComplexNumber", float, int]) -> "ComplexNumber":
        """Add two complex numbers or a complex number and a real number.

        Args:
            other: Another ComplexNumber, or a real number to add.

        Returns:
            A new ComplexNumber representing the sum.

        Examples:
            >>> z1 = ComplexNumber(3, 4)
            >>> z2 = ComplexNumber(1, 2)
            >>> z3 = z1 + z2
            >>> print(z3)
            4.0 + 6.0i
            >>> z4 = z1 + 5
            >>> print(z4)
            8.0 + 4.0i
        """
        if isinstance(other, ComplexNumber):
            return ComplexNumber(self.real + other.real, self.imag + other.imag)
        elif isinstance(other, (int, float)):
            return ComplexNumber(self.real + other, self.imag)
        else:
            return NotImplemented

    def __sub__(self, other: Union["ComplexNumber", float, int]) -> "ComplexNumber":
        """Subtract two complex numbers or subtract a real number from a complex number.

        Args:
            other: Another ComplexNumber, or a real number to subtract.

        Returns:
            A new ComplexNumber representing the difference.

        Examples:
            >>> z1 = ComplexNumber(3, 4)
            >>> z2 = ComplexNumber(1, 2)
            >>> z3 = z1 - z2
            >>> print(z3)
            2.0 + 2.0i
        """
        if isinstance(other, ComplexNumber):
            return ComplexNumber(self.real - other.real, self.imag - other.imag)
        elif isinstance(other, (int, float)):
            return ComplexNumber(self.real - other, self.imag)
        else:
            return NotImplemented

    def __mul__(self, other: Union["ComplexNumber", float, int]) -> "ComplexNumber":
        """Multiply two complex numbers or a complex number by a real number.

        Uses the formula: (a + bi) * (c + di) = (ac - bd) + (ad + bc)i

        Args:
            other: Another ComplexNumber, or a real number to multiply by.

        Returns:
            A new ComplexNumber representing the product.

        Examples:
            >>> z1 = ComplexNumber(3, 4)
            >>> z2 = ComplexNumber(1, 2)
            >>> z3 = z1 * z2
            >>> print(z3)
            -5.0 + 10.0i
            >>> z4 = z1 * 2
            >>> print(z4)
            6.0 + 8.0i
        """
        if isinstance(other, ComplexNumber):
            real = self.real * other.real - self.imag * other.imag
            imag = self.real * other.imag + self.imag * other.real
            return ComplexNumber(real, imag)
        elif isinstance(other, (int, float)):
            return ComplexNumber(self.real * other, self.imag * other)
        else:
            return NotImplemented

    def __truediv__(self, other: Union["ComplexNumber", float, int]) -> "ComplexNumber":
        """Divide two complex numbers or divide a complex number by a real number.

        Uses the formula: (a + bi) / (c + di) = [(ac + bd) + (bc - ad)i] / (c² + d²)

        Args:
            other: Another ComplexNumber, or a real number to divide by.

        Returns:
            A new ComplexNumber representing the quotient.

        Raises:
            ZeroDivisionError: If attempting to divide by zero.

        Examples:
            >>> z1 = ComplexNumber(4, 2)
            >>> z2 = ComplexNumber(1, 1)
            >>> z3 = z1 / z2
            >>> print(z3)
            3.0 + -1.0i
        """
        if isinstance(other, ComplexNumber):
            if other.real == 0 and other.imag == 0:
                raise ZeroDivisionError("Cannot divide by zero complex number")
            denominator = other.real**2 + other.imag**2
            real = (self.real * other.real + self.imag * other.imag) / denominator
            imag = (self.imag * other.real - self.real * other.imag) / denominator
            return ComplexNumber(real, imag)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return ComplexNumber(self.real / other, self.imag / other)
        else:
            return NotImplemented

    def __eq__(self, other: object) -> bool:
        """Check if two complex numbers are equal.

        Args:
            other: Another ComplexNumber to compare with.

        Returns:
            True if both real and imaginary parts are equal, False otherwise.

        Examples:
            >>> z1 = ComplexNumber(3, 4)
            >>> z2 = ComplexNumber(3, 4)
            >>> z3 = ComplexNumber(3, 5)
            >>> z1 == z2
            True
            >>> z1 == z3
            False
        """
        if not isinstance(other, ComplexNumber):
            return NotImplemented
        return self.real == other.real and self.imag == other.imag

    def __str__(self) -> str:
        """Return a string representation of the complex number.

        Returns:
            A string in the format "a + bi" or "a - bi".

        Examples:
            >>> z1 = ComplexNumber(3, 4)
            >>> str(z1)
            '3.0 + 4.0i'
            >>> z2 = ComplexNumber(3, -4)
            >>> str(z2)
            '3.0 - 4.0i'
        """
        if self.imag >= 0:
            return f"{self.real} + {self.imag}i"
        else:
            return f"{self.real} - {abs(self.imag)}i"

    def __repr__(self) -> str:
        """Return a detailed string representation of the complex number.

        Returns:
            A string that can be used to recreate the object.

        Examples:
            >>> z = ComplexNumber(3, 4)
            >>> repr(z)
            'ComplexNumber(3.0, 4.0)'
        """
        return f"ComplexNumber({self.real}, {self.imag})"

    def magnitude(self) -> float:
        """Calculate the magnitude (absolute value) of the complex number.

        The magnitude is calculated as sqrt(a² + b²).

        Returns:
            The magnitude of the complex number.

        Examples:
            >>> z = ComplexNumber(3, 4)
            >>> z.magnitude()
            5.0
            >>> z = ComplexNumber(0, 1)
            >>> z.magnitude()
            1.0
        """
        return math.sqrt(self.real**2 + self.imag**2)

    def phase(self) -> float:
        """Calculate the phase (argument) of the complex number in radians.

        The phase is the angle θ in the polar representation r*e^(iθ).

        Returns:
            The phase of the complex number in radians, in the range (-π, π].

        Examples:
            >>> z = ComplexNumber(1, 1)
            >>> round(z.phase(), 4)
            0.7854
            >>> z = ComplexNumber(0, 1)
            >>> round(z.phase(), 4)
            1.5708
        """
        return math.atan2(self.imag, self.real)

    def conjugate(self) -> "ComplexNumber":
        """Return the complex conjugate.

        The conjugate of a + bi is a - bi.

        Returns:
            A new ComplexNumber representing the conjugate.

        Examples:
            >>> z = ComplexNumber(3, 4)
            >>> z_conj = z.conjugate()
            >>> print(z_conj)
            3.0 - 4.0i
        """
        return ComplexNumber(self.real, -self.imag)

    @classmethod
    def from_polar(cls, magnitude: float, phase: float) -> "ComplexNumber":
        """Create a complex number from polar coordinates.

        Args:
            magnitude: The magnitude (r) of the complex number.
            phase: The phase (θ) in radians.

        Returns:
            A new ComplexNumber created from polar coordinates.

        Examples:
            >>> import math
            >>> z = ComplexNumber.from_polar(5, math.pi/4)
            >>> round(z.real, 4)
            3.5355
            >>> round(z.imag, 4)
            3.5355
        """
        real = magnitude * math.cos(phase)
        imag = magnitude * math.sin(phase)
        return cls(real, imag)
