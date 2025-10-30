"""Tests for Rust documentation extractor."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from introligo.rustdoc_extractor import RustDocExtractor


class TestRustDocExtractor:
    """Test RustDoc extraction and conversion."""

    def test_init_without_path(self):
        """Test initialization without crate path."""
        extractor = RustDocExtractor()
        assert extractor.crate_path is None

    def test_init_with_path(self):
        """Test initialization with crate path."""
        path = Path("/tmp/test")
        extractor = RustDocExtractor(crate_path=path)
        assert extractor.crate_path == path

    @patch("subprocess.run")
    def test_check_cargo_available_success(self, mock_run):
        """Test check_cargo_available when Cargo is installed."""
        mock_run.return_value = MagicMock(returncode=0)
        extractor = RustDocExtractor()

        assert extractor.check_cargo_available() is True
        mock_run.assert_called_once_with(
            ["cargo", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_check_cargo_available_not_found(self, mock_run):
        """Test check_cargo_available when Cargo is not installed."""
        mock_run.side_effect = FileNotFoundError()
        extractor = RustDocExtractor()

        assert extractor.check_cargo_available() is False

    @patch("subprocess.run")
    def test_check_cargo_available_timeout(self, mock_run):
        """Test check_cargo_available when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("cargo", 5)
        extractor = RustDocExtractor()

        assert extractor.check_cargo_available() is False

    @patch("subprocess.run")
    def test_extract_crate_metadata_success(self, mock_run):
        """Test extract_crate_metadata when metadata is available."""
        mock_metadata = {
            "packages": [
                {
                    "name": "test_crate",
                    "version": "0.1.0",
                    "id": "test_crate 0.1.0 (path+file:///tmp/test_crate)",
                }
            ]
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_metadata))

        extractor = RustDocExtractor(crate_path=Path("/tmp/test_crate"))
        metadata = extractor.extract_crate_metadata()

        assert metadata is not None
        assert metadata["name"] == "test_crate"
        assert metadata["version"] == "0.1.0"

    @patch("subprocess.run")
    def test_extract_crate_metadata_no_crate_path(self, mock_run):
        """Test extract_crate_metadata when no crate path is set."""
        extractor = RustDocExtractor()
        metadata = extractor.extract_crate_metadata()

        assert metadata is None
        mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_extract_crate_metadata_failure(self, mock_run):
        """Test extract_crate_metadata when cargo metadata fails."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error")

        extractor = RustDocExtractor(crate_path=Path("/tmp/test"))
        metadata = extractor.extract_crate_metadata()

        assert metadata is None

    @patch("subprocess.run")
    def test_extract_crate_doc_cargo_not_available(self, mock_run):
        """Test extract_crate_doc when Cargo is not available."""
        mock_run.side_effect = FileNotFoundError()
        extractor = RustDocExtractor(crate_path=Path("/tmp/test"))

        result = extractor.extract_crate_doc("test_crate")
        assert result is None

    @patch("subprocess.run")
    def test_extract_crate_doc_no_crate_path(self, mock_run):
        """Test extract_crate_doc when no crate path is set."""
        extractor = RustDocExtractor()
        result = extractor.extract_crate_doc("test_crate")

        assert result is None

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
//! # Test Crate
//!
//! This is a test crate for testing documentation extraction.

/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// A test struct for demonstration.
pub struct Calculator {
    /// The current value
    value: i32,
}
""",
    )
    @patch("subprocess.run")
    def test_extract_crate_doc_success(self, mock_run, mock_file):
        """Test extract_crate_doc when documentation is successfully extracted."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        # Mock the file paths
        with patch.object(Path, "exists", return_value=True):
            result = extractor.extract_crate_doc("test_crate")

        assert result is not None
        assert "Test Crate" in result
        assert "pub fn add" in result or "add" in result

    @patch("subprocess.run")
    def test_extract_crate_doc_timeout(self, mock_run):
        """Test extract_crate_doc when cargo doc times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("cargo", 120)

        extractor = RustDocExtractor(crate_path=Path("/tmp/test"))
        result = extractor.extract_crate_doc("test_crate")

        assert result is None

    def test_extract_public_items(self):
        """Test _extract_public_items with sample Rust code."""
        extractor = RustDocExtractor()

        rust_code = """
/// Adds two numbers
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// A calculator struct
pub struct Calculator {
    value: i32,
}

/// Private function (should not be extracted)
fn private_func() {}
"""

        items = extractor._extract_public_items(rust_code)

        assert len(items) > 0
        # Check that public items are present
        result_str = "".join(items)
        assert "pub fn add" in result_str
        assert "pub struct Calculator" in result_str
        # Private function should not be extracted
        assert "private_func" not in result_str

    def test_convert_to_rst_empty(self):
        """Test convert_to_rst with empty input."""
        extractor = RustDocExtractor()

        result = extractor.convert_to_rst(None)
        assert result == ""

        result = extractor.convert_to_rst("")
        assert result == ""

    def test_convert_to_rst_with_content(self):
        """Test convert_to_rst with actual content."""
        extractor = RustDocExtractor()

        content = "Module Documentation\nTest content"
        result = extractor.convert_to_rst(content, "test_crate")

        assert "Test content" in result

    def test_extract_and_convert_no_crate_path(self):
        """Test extract_and_convert when no crate path is set."""
        extractor = RustDocExtractor()

        success, content = extractor.extract_and_convert("test_crate")

        assert success is False
        assert "not available" in content
        assert "test_crate" in content

    @patch("subprocess.run")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
//! Test crate
pub fn test() {}
""",
    )
    def test_extract_and_convert_success(self, mock_file, mock_run):
        """Test extract_and_convert with successful extraction."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(Path, "exists", return_value=True):
            success, content = extractor.extract_and_convert("test_crate")

        # Should extract something
        assert isinstance(success, bool)
        assert isinstance(content, str)

    @patch("subprocess.run")
    def test_extract_multiple_crates(self, mock_run):
        """Test extract_multiple_crates with multiple crate paths."""
        mock_metadata = {
            "packages": [
                {"name": "crate1", "version": "0.1.0"},
            ]
        }
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_metadata))

        extractor = RustDocExtractor()
        crate_paths = [Path("/tmp/crate1"), Path("/tmp/crate2")]

        with patch.object(Path, "exists", return_value=True), patch(
            "builtins.open", mock_open(read_data="//! Test\npub fn test() {}")
        ):
            results = extractor.extract_multiple_crates(crate_paths)

        assert len(results) == 2
        for crate_name, success, content in results:
            assert isinstance(crate_name, str)
            assert isinstance(success, bool)
            assert isinstance(content, str)

    def test_parse_rust_source_with_module_docs(self):
        """Test _parse_rust_source with module-level documentation."""
        extractor = RustDocExtractor()

        rust_source = Path("/tmp/test_lib.rs")
        content = """
//! # My Crate
//! This is module documentation.
//!
//! It can have multiple lines.

/// Public function
pub fn my_function() {}
"""

        with patch("builtins.open", mock_open(read_data=content)):
            result = extractor._parse_rust_source(rust_source)

        assert "My Crate" in result
        assert "module documentation" in result
        assert "pub fn my_function" in result
