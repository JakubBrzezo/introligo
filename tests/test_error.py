"""Tests for IntroligoError exception class."""

import pytest

from introligo import IntroligoError


class TestIntroligoError:
    """Test cases for IntroligoError exception."""

    def test_error_with_message_only(self):
        """Test IntroligoError with just a message."""
        error = IntroligoError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.context is None

    def test_error_with_context(self):
        """Test IntroligoError with message and context."""
        error = IntroligoError("Test error", context="Additional context")
        expected = "Test error\nContext: Additional context"
        assert str(error) == expected
        assert error.message == "Test error"
        assert error.context == "Additional context"

    def test_error_can_be_raised(self):
        """Test that IntroligoError can be raised and caught."""
        with pytest.raises(IntroligoError) as exc_info:
            raise IntroligoError("Test error")
        assert str(exc_info.value) == "Test error"

    def test_error_inheritance(self):
        """Test that IntroligoError inherits from Exception."""
        error = IntroligoError("Test")
        assert isinstance(error, Exception)

    def test_error_with_empty_message(self):
        """Test IntroligoError with empty message."""
        error = IntroligoError("")
        assert str(error) == ""
        assert error.message == ""

    def test_error_context_in_repr(self):
        """Test IntroligoError string representation with context."""
        error = IntroligoError("Error", context="Context info")
        error_str = str(error)
        assert "Error" in error_str
        assert "Context: Context info" in error_str
