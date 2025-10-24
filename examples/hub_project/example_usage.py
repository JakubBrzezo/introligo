#!/usr/bin/env python3
"""Example usage of the ComplexNumber class.

This script demonstrates various operations with complex numbers
using the MyProject ComplexNumber class.
"""

import math

from myproject import ComplexNumber


def main():
    """Run example demonstrations of ComplexNumber functionality."""
    print("=" * 60)
    print("MyProject ComplexNumber Examples")
    print("=" * 60)
    print()

    # Creating complex numbers
    print("1. Creating Complex Numbers")
    print("-" * 40)
    z1 = ComplexNumber(3, 4)
    z2 = ComplexNumber(1, 2)
    z3 = ComplexNumber(2, -3)
    print(f"z1 = {z1}")
    print(f"z2 = {z2}")
    print(f"z3 = {z3}")
    print()

    # Arithmetic operations
    print("2. Arithmetic Operations")
    print("-" * 40)
    print(f"z1 + z2 = {z1 + z2}")
    print(f"z1 - z2 = {z1 - z2}")
    print(f"z1 * z2 = {z1 * z2}")
    print(f"z1 / z2 = {z1 / z2}")
    print()

    # Operations with real numbers
    print("3. Operations with Real Numbers")
    print("-" * 40)
    print(f"z1 + 5 = {z1 + 5}")
    print(f"z1 * 2 = {z1 * 2}")
    print(f"z1 / 2 = {z1 / 2}")
    print()

    # Magnitude and phase
    print("4. Magnitude and Phase")
    print("-" * 40)
    print(f"|z1| = {z1.magnitude()}")
    print(f"phase(z1) = {z1.phase():.4f} radians")
    print(f"phase(z1) = {math.degrees(z1.phase()):.2f} degrees")
    print()

    # Conjugate
    print("5. Complex Conjugate")
    print("-" * 40)
    print(f"z1 = {z1}")
    print(f"conjugate(z1) = {z1.conjugate()}")
    print()

    # Polar form
    print("6. Creating from Polar Coordinates")
    print("-" * 40)
    magnitude = 5
    phase_rad = math.pi / 4
    z_polar = ComplexNumber.from_polar(magnitude, phase_rad)
    print("From polar (r=5, θ=π/4):")
    print(f"z = {z_polar}")
    print(f"Verification: |z| = {z_polar.magnitude():.4f}")
    print(f"              θ = {z_polar.phase():.4f}")
    print()

    # Equality
    print("7. Equality Testing")
    print("-" * 40)
    z4 = ComplexNumber(3, 4)
    z5 = ComplexNumber(3, 5)
    print(f"z1 = {z1}")
    print(f"z4 = {z4}")
    print(f"z5 = {z5}")
    print(f"z1 == z4: {z1 == z4}")
    print(f"z1 == z5: {z1 == z5}")
    print()

    print("=" * 60)
    print("Examples complete! Check the API documentation for more details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
