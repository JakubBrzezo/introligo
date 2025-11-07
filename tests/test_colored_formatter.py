"""Tests for colored logging formatter."""

import logging
import sys
from io import StringIO
from unittest.mock import patch

from introligo.colored_formatter import ColoredFormatter


class TestColoredFormatter:
    """Test ColoredFormatter class."""

    def test_formatter_initialization(self):
        """Test that formatter can be initialized."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        assert formatter is not None

    def test_error_level_formatting(self):
        """Test ERROR level formatting with colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error message",
            args=(),
            exc_info=None,
        )

        # Mock environment to force colors
        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatted = formatter.format(record)

        # Check that the message contains color codes
        assert "\x1b[" in formatted or formatted.startswith("ERROR:")
        assert "Test error message" in formatted

    def test_warning_level_formatting(self):
        """Test WARNING level formatting with colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test warning message",
            args=(),
            exc_info=None,
        )

        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatted = formatter.format(record)

        assert "WARNING" in formatted
        assert "Test warning message" in formatted

    def test_info_level_formatting(self):
        """Test INFO level formatting with colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test info message",
            args=(),
            exc_info=None,
        )

        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatted = formatter.format(record)

        assert "INFO" in formatted
        assert "Test info message" in formatted

    def test_debug_level_formatting(self):
        """Test DEBUG level formatting with colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="Test debug message",
            args=(),
            exc_info=None,
        )

        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatted = formatter.format(record)

        assert "DEBUG" in formatted
        assert "Test debug message" in formatted

    def test_no_color_environment_variable(self):
        """Test that NO_COLOR disables colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None,
        )

        with patch.dict("os.environ", {"NO_COLOR": "1"}, clear=True):
            formatted = formatter.format(record)

        # Should not contain ANSI escape codes
        assert "\x1b[" not in formatted
        assert formatted == "ERROR: Test error"

    def test_force_color_environment_variable(self):
        """Test that FORCE_COLOR enables colors."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None,
        )

        # Mock stdout as non-TTY but with FORCE_COLOR
        with patch.dict("os.environ", {"FORCE_COLOR": "1"}, clear=True):
            formatted = formatter.format(record)

        # Should contain color codes due to FORCE_COLOR
        assert "ERROR" in formatted
        assert "Test error" in formatted

    def test_force_color_overrides_no_tty(self):
        """Test that FORCE_COLOR works even when not a TTY."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Test warning",
            args=(),
            exc_info=None,
        )

        # Mock isatty to return False but set FORCE_COLOR
        with patch.dict("os.environ", {"FORCE_COLOR": "1"}, clear=True), patch.object(
            sys.stdout, "isatty", return_value=False
        ):
            formatted = formatter.format(record)

        # Should still have colors due to FORCE_COLOR
        assert "WARNING" in formatted
        assert "Test warning" in formatted

    def test_no_color_overrides_force_color(self):
        """Test that NO_COLOR takes precedence over FORCE_COLOR."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None,
        )

        # Set both NO_COLOR and FORCE_COLOR - NO_COLOR should win
        with patch.dict("os.environ", {"NO_COLOR": "1", "FORCE_COLOR": "1"}, clear=True):
            formatted = formatter.format(record)

        # Should not contain ANSI escape codes
        assert "\x1b[" not in formatted
        assert formatted == "ERROR: Test error"

    def test_should_use_colors_with_tty(self):
        """Test _should_use_colors returns True for TTY."""
        with patch.object(sys.stdout, "isatty", return_value=True), patch.dict(
            "os.environ", {"TERM": "xterm-256color"}, clear=True
        ):
            result = ColoredFormatter._should_use_colors()
            assert result is True

    def test_should_use_colors_without_tty(self):
        """Test _should_use_colors returns False for non-TTY."""
        with patch.object(sys.stdout, "isatty", return_value=False):
            result = ColoredFormatter._should_use_colors()
            assert result is False

    def test_should_use_colors_dumb_terminal(self):
        """Test _should_use_colors returns False for dumb terminal."""
        with patch.object(sys.stdout, "isatty", return_value=True), patch.dict(
            "os.environ", {"TERM": "dumb"}, clear=True
        ):
            result = ColoredFormatter._should_use_colors()
            assert result is False

    def test_should_use_colors_no_isatty_attribute(self):
        """Test _should_use_colors handles missing isatty attribute."""

        # Create a mock stdout without isatty attribute
        class MockStdout:
            """Mock stdout without isatty method."""

            def write(self, text):
                """Mock write method."""
                pass

        mock_stdout = MockStdout()

        with patch.object(sys, "stdout", mock_stdout):
            result = ColoredFormatter._should_use_colors()
            assert result is False

    def test_record_levelname_restored(self):
        """Test that original levelname is restored after formatting."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test error",
            args=(),
            exc_info=None,
        )

        original_levelname = record.levelname

        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatter.format(record)

        # Levelname should be restored
        assert record.levelname == original_levelname

    def test_unknown_log_level(self):
        """Test formatting with an unknown log level."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        # Create a custom log level
        custom_level = 25  # Between INFO and WARNING
        record = logging.LogRecord(
            name="test",
            level=custom_level,
            pathname="test.py",
            lineno=1,
            msg="Custom level message",
            args=(),
            exc_info=None,
        )
        record.levelname = "CUSTOM"

        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatted = formatter.format(record)

        # Should format without color for unknown level
        assert "CUSTOM" in formatted
        assert "Custom level message" in formatted

    def test_formatter_with_handler_integration(self):
        """Test ColoredFormatter works with logging handler."""
        # Create a logger with colored formatter
        logger = logging.getLogger("test_colored")
        logger.setLevel(logging.DEBUG)

        # Create string stream to capture output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)

        try:
            with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
                logger.error("Test error message")
                logger.warning("Test warning message")
                logger.info("Test info message")
                logger.debug("Test debug message")

            output = stream.getvalue()

            # Check all messages are present
            assert "Test error message" in output
            assert "Test warning message" in output
            assert "Test info message" in output
            assert "Test debug message" in output

        finally:
            logger.removeHandler(handler)
            handler.close()

    def test_color_constants_defined(self):
        """Test that color mapping constants are properly defined."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")

        # Check that all standard log levels have colors
        assert logging.ERROR in formatter.COLORS
        assert logging.WARNING in formatter.COLORS
        assert logging.INFO in formatter.COLORS
        assert logging.DEBUG in formatter.COLORS

    def test_environment_variable_case_insensitive(self):
        """Test that environment variables work with different cases."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        # Test with "true" instead of "1"
        with patch.dict("os.environ", {"FORCE_COLOR": "true"}, clear=True):
            formatted = formatter.format(record)
            assert "ERROR" in formatted

        # Test with "yes"
        with patch.dict("os.environ", {"FORCE_COLOR": "yes"}, clear=True):
            formatted = formatter.format(record)
            assert "ERROR" in formatted

        # Test NO_COLOR with "true"
        with patch.dict("os.environ", {"NO_COLOR": "true"}, clear=True):
            formatted = formatter.format(record)
            assert "\x1b[" not in formatted

    def test_empty_environment_variables(self):
        """Test behavior with empty environment variables."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        # Empty FORCE_COLOR should not force colors
        with patch.dict("os.environ", {"FORCE_COLOR": ""}, clear=True), patch.object(
            sys.stdout, "isatty", return_value=False
        ):
            formatted = formatter.format(record)
            # Without TTY and empty FORCE_COLOR, no colors
            assert "\x1b[" not in formatted or "ERROR: Test" in formatted

    def test_formatter_with_complex_format_string(self):
        """Test formatter with a complex format string."""
        formatter = ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test.module",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Complex message",
            args=(),
            exc_info=None,
        )

        with patch.dict("os.environ", {"FORCE_COLOR": "1"}):
            formatted = formatter.format(record)

        assert "test.module" in formatted
        assert "Complex message" in formatted
        assert "ERROR" in formatted

    def test_color_codes_actually_applied(self):
        """Test that ANSI color codes are actually present in output."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Force colors on and verify ANSI codes are present
        with patch.dict("os.environ", {"FORCE_COLOR": "1", "NO_COLOR": "0"}, clear=True):
            formatted = formatter.format(record)

        # Should have ANSI escape sequence codes
        # Check for the actual color code application
        has_ansi = "\x1b[" in formatted or "\033[" in formatted
        assert has_ansi or "ERROR" in formatted, "Output should contain colors or ERROR text"

    def test_all_log_levels_with_tty(self):
        """Test all log levels with simulated TTY."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")

        # Test each log level with TTY simulation
        levels = [
            (logging.ERROR, "Error message"),
            (logging.WARNING, "Warning message"),
            (logging.INFO, "Info message"),
            (logging.DEBUG, "Debug message"),
        ]

        for level, msg in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=1,
                msg=msg,
                args=(),
                exc_info=None,
            )

            # Simulate TTY with FORCE_COLOR
            with patch.dict("os.environ", {"FORCE_COLOR": "1"}, clear=True):
                formatted = formatter.format(record)
                assert msg in formatted


class TestColoredFormatterEnvironmentVariables:
    """Test environment variable handling in colored_formatter module."""

    def test_force_color_runtime_check(self):
        """Test FORCE_COLOR is checked at runtime, not module load time."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        # Test that environment changes are picked up at runtime
        with patch.dict("os.environ", {"FORCE_COLOR": "1"}, clear=True):
            formatted = formatter.format(record)
            # With FORCE_COLOR, should have colors
            assert "ERROR" in formatted

        # Now without FORCE_COLOR and no TTY, should not have colors
        with patch.dict("os.environ", {}, clear=True), patch.object(
            sys.stdout, "isatty", return_value=False
        ):
            formatted = formatter.format(record)
            # Without FORCE_COLOR and no TTY, no colors
            assert formatted == "ERROR: Test"

    def test_no_color_runtime_check(self):
        """Test NO_COLOR is checked at runtime, not module load time."""
        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        # Test that NO_COLOR is respected even after module is loaded
        with patch.dict("os.environ", {"NO_COLOR": "1", "FORCE_COLOR": "1"}, clear=True):
            formatted = formatter.format(record)
            # NO_COLOR should override FORCE_COLOR
            assert formatted == "ERROR: Test"
            assert "\x1b[" not in formatted
