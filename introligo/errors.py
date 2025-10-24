#!/usr/bin/env python
"""Custom exceptions for Introligo.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

from typing import Optional


class IntroligoError(Exception):
    """Custom exception for Introligo errors.

    Args:
        message: The error message.
        context: Optional additional context about the error.

    Attributes:
        message: The error message.
        context: Additional context information.
    """

    def __init__(self, message: str, context: Optional[str] = None):
        """Initialize the IntroligoError.

        Args:
            message: The error message.
            context: Optional additional context about the error.
        """
        self.message = message
        self.context = context
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error.

        Returns:
            Formatted error message with optional context.
        """
        if self.context:
            return f"{self.message}\nContext: {self.context}"
        return self.message
