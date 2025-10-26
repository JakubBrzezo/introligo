"""Tests for introligo/__init__.py module."""

import sys
from unittest.mock import patch


class TestInitModule:
    """Test the __init__ module."""

    def test_version_import_fallback(self):
        """Test that version fallback works when _version module is not available."""
        # Mock the import to raise ImportError
        with patch.dict(sys.modules, {"introligo._version": None}):
            # Force reimport with missing _version module
            import importlib

            # Remove from cache to force re-import
            if "introligo" in sys.modules:
                del sys.modules["introligo"]

            # Mock _version import to fail
            import builtins

            original_import = builtins.__import__

            def mock_import(name, *args, **kwargs):  # noqa: ANN002, ANN003, ANN202
                if name == "introligo._version":
                    raise ImportError("No module named 'introligo._version'")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                import introligo

                # Should use fallback version
                assert introligo.__version__ == "0.0.0.dev0"

            # Clean up
            if "introligo" in sys.modules:
                del sys.modules["introligo"]
            importlib.reload(sys.modules.get("introligo", importlib.import_module("introligo")))

    def test_public_api_exports(self):
        """Test that all expected symbols are exported in __all__."""
        import introligo

        # Check that __all__ contains expected exports
        assert "IntroligoGenerator" in introligo.__all__
        assert "IntroligoError" in introligo.__all__
        assert "PageNode" in introligo.__all__
        assert "main" in introligo.__all__
        assert "slugify" in introligo.__all__
        assert "__version__" in introligo.__all__

        # Check that symbols are actually accessible
        assert hasattr(introligo, "IntroligoGenerator")
        assert hasattr(introligo, "IntroligoError")
        assert hasattr(introligo, "PageNode")
        assert hasattr(introligo, "main")
        assert hasattr(introligo, "slugify")
        assert hasattr(introligo, "__version__")

    def test_module_metadata(self):
        """Test module metadata attributes."""
        import introligo

        assert introligo.__author__ == "Jakub Brzezowski"
        assert introligo.__email__ == "brzezoo@gmail.com"
        assert introligo.__license__ == "Apache-2.0"
