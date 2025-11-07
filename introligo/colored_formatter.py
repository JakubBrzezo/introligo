#!/usr/bin/env python
"""Colored logging formatter for Introligo.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
import os

from colorama import Fore, Style, init

# Initialize colorama for cross-platform support
# strip=False ensures colors work when output is redirected
init(autoreset=True, strip=False)

# Check if colors should be forced or disabled
FORCE_COLOR = os.environ.get("FORCE_COLOR", "").lower() in ("1", "true", "yes")
NO_COLOR = os.environ.get("NO_COLOR", "").lower() in ("1", "true", "yes")


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels.

    Uses colorama for cross-platform color support with high contrast colors:
    - ERROR: Bright Red
    - WARNING: Bright Yellow
    - INFO: Green
    - DEBUG: Cyan
    """

    # Define color mapping for each log level
    COLORS = {
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.INFO: Fore.GREEN,
        logging.DEBUG: Fore.CYAN,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors.

        Args:
            record: The log record to format.

        Returns:
            Colored and formatted log message.
        """
        # Check if colors should be used
        use_colors = not NO_COLOR and (FORCE_COLOR or self._should_use_colors())

        # Get the color for this log level
        color = self.COLORS.get(record.levelno, "") if use_colors else ""

        # Save the original levelname
        original_levelname = record.levelname

        # Apply color to levelname
        if color:
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"

        # Format the message using the parent formatter
        formatted = super().format(record)

        # Restore the original levelname (in case the record is reused)
        record.levelname = original_levelname

        return formatted

    @staticmethod
    def _should_use_colors() -> bool:
        """Determine if colors should be used based on terminal capabilities.

        Returns:
            True if the output is a TTY and supports colors, False otherwise.
        """
        import sys

        # Check if stdout is a terminal
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            return False

        # Check for common "dumb" terminals that don't support colors
        term = os.environ.get("TERM", "")
        return term != "dumb"
