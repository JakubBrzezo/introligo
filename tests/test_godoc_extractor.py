"""Tests for Go documentation extractor."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from introligo.godoc_extractor import GoDocExtractor


class TestGoDocExtractor:
    """Test GoDoc extraction and conversion."""

    def test_init_without_path(self):
        """Test initialization without package path."""
        extractor = GoDocExtractor()
        assert extractor.package_path is None

    def test_init_with_path(self):
        """Test initialization with package path."""
        path = Path("/tmp/test")
        extractor = GoDocExtractor(package_path=path)
        assert extractor.package_path == path

    @patch("subprocess.run")
    def test_check_go_available_success(self, mock_run):
        """Test check_go_available when Go is installed."""
        mock_run.return_value = MagicMock(returncode=0)
        extractor = GoDocExtractor()

        assert extractor.check_go_available() is True
        mock_run.assert_called_once_with(
            ["go", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_check_go_available_not_found(self, mock_run):
        """Test check_go_available when Go is not installed."""
        mock_run.side_effect = FileNotFoundError()
        extractor = GoDocExtractor()

        assert extractor.check_go_available() is False

    @patch("subprocess.run")
    def test_check_go_available_timeout(self, mock_run):
        """Test check_go_available when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("go", 5)
        extractor = GoDocExtractor()

        assert extractor.check_go_available() is False

    @patch("subprocess.run")
    def test_extract_package_doc_go_not_available(self, mock_run):
        """Test extract_package_doc when Go is not available."""
        mock_run.side_effect = FileNotFoundError()
        extractor = GoDocExtractor()

        result = extractor.extract_package_doc("example.com/pkg")
        assert result is None

    @patch("subprocess.run")
    def test_extract_package_doc_success_without_path(self, mock_run):
        """Test successful package extraction without package path."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # go version
            MagicMock(returncode=0, stdout="package example\n\nDoc content"),  # go doc
        ]
        extractor = GoDocExtractor()

        result = extractor.extract_package_doc("example.com/pkg")
        assert result == "package example\n\nDoc content"
        assert mock_run.call_count == 2

        # Check the go doc call
        go_doc_call = mock_run.call_args_list[1]
        assert go_doc_call[0][0] == ["go", "doc", "-all", "example.com/pkg"]
        assert "cwd" not in go_doc_call[1]

    @patch("subprocess.run")
    def test_extract_package_doc_success_with_path(self, mock_run):
        """Test successful package extraction with package path."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # go version
            MagicMock(returncode=0, stdout="package example\n\nDoc content"),  # go doc
        ]
        package_path = Path("/tmp/test")
        extractor = GoDocExtractor(package_path=package_path)

        result = extractor.extract_package_doc("example.com/pkg")
        assert result == "package example\n\nDoc content"

        # Check the go doc call includes cwd
        go_doc_call = mock_run.call_args_list[1]
        assert go_doc_call[1]["cwd"] == str(package_path)

    @patch("subprocess.run")
    def test_extract_package_doc_failure(self, mock_run):
        """Test package extraction when go doc fails."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # go version
            MagicMock(returncode=1, stderr="package not found"),  # go doc fails
        ]
        extractor = GoDocExtractor()

        result = extractor.extract_package_doc("example.com/invalid")
        assert result is None

    @patch("subprocess.run")
    def test_extract_package_doc_timeout(self, mock_run):
        """Test package extraction when command times out."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # go version
            subprocess.TimeoutExpired("go", 30),  # go doc times out
        ]
        extractor = GoDocExtractor()

        result = extractor.extract_package_doc("example.com/pkg")
        assert result is None

    @patch("subprocess.run")
    def test_extract_package_doc_exception(self, mock_run):
        """Test package extraction when an exception occurs."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # go version
            Exception("Unexpected error"),  # go doc throws exception
        ]
        extractor = GoDocExtractor()

        result = extractor.extract_package_doc("example.com/pkg")
        assert result is None

    def test_convert_to_rst_empty_input(self):
        """Test convert_to_rst with empty input."""
        extractor = GoDocExtractor()
        result = extractor.convert_to_rst("")
        assert result == ""

    def test_convert_to_rst_none_input(self):
        """Test convert_to_rst with None input."""
        extractor = GoDocExtractor()
        result = extractor.convert_to_rst(None)
        assert result == ""

    def test_convert_to_rst_package_line(self):
        """Test convert_to_rst skips package declaration line."""
        extractor = GoDocExtractor()
        godoc = "package example\n\nSome documentation."
        result = extractor.convert_to_rst(godoc)

        assert "package example" not in result
        assert "Some documentation." in result

    def test_convert_to_rst_function_declaration(self):
        """Test convert_to_rst handles function declarations."""
        extractor = GoDocExtractor()
        godoc = """package example

func Add(a, b int) int
    Add returns the sum of two integers."""

        result = extractor.convert_to_rst(godoc)
        assert ".. code-block:: go" in result
        assert "func Add(a, b int) int" in result
        assert "Add returns the sum" in result

    def test_convert_to_rst_type_declaration(self):
        """Test convert_to_rst handles type declarations."""
        extractor = GoDocExtractor()
        godoc = """package example

type Person struct {
    Name string
    Age  int
}"""

        result = extractor.convert_to_rst(godoc)
        assert ".. code-block:: go" in result
        assert "type Person struct" in result

    def test_convert_to_rst_const_declaration(self):
        """Test convert_to_rst handles const declarations."""
        extractor = GoDocExtractor()
        godoc = """package example

const MaxSize = 100"""

        result = extractor.convert_to_rst(godoc)
        assert ".. code-block:: go" in result
        assert "const MaxSize = 100" in result

    def test_convert_to_rst_var_declaration(self):
        """Test convert_to_rst handles var declarations."""
        extractor = GoDocExtractor()
        godoc = """package example

var GlobalVar string"""

        result = extractor.convert_to_rst(godoc)
        assert ".. code-block:: go" in result
        assert "var GlobalVar string" in result

    def test_convert_to_rst_uppercase_section(self):
        """Test convert_to_rst handles uppercase sections."""
        extractor = GoDocExtractor()
        godoc = """package example

CONSTANTS

const MaxSize = 100"""

        result = extractor.convert_to_rst(godoc)
        assert "CONSTANTS" in result
        assert "~~~~~~~~~" in result  # Underline for section

    def test_convert_to_rst_multiline_function(self):
        """Test convert_to_rst handles multi-line function signatures."""
        extractor = GoDocExtractor()
        godoc = """package example

func Process(
    name string,
    value int,
) error"""

        result = extractor.convert_to_rst(godoc)
        assert ".. code-block:: go" in result
        assert "func Process(" in result
        assert "name string," in result

    def test_convert_to_rst_closes_code_block_at_end(self):
        """Test convert_to_rst closes code block at end if still open."""
        extractor = GoDocExtractor()
        godoc = """package example

func Incomplete("""

        result = extractor.convert_to_rst(godoc)
        # Should not raise error and should close the block
        assert ".. code-block:: go" in result

    @patch.object(GoDocExtractor, "extract_package_doc")
    @patch.object(GoDocExtractor, "convert_to_rst")
    def test_extract_and_convert_success(self, mock_convert, mock_extract):
        """Test extract_and_convert when extraction succeeds."""
        mock_extract.return_value = "godoc output"
        mock_convert.return_value = "rst content"

        extractor = GoDocExtractor()
        success, content = extractor.extract_and_convert("example.com/pkg")

        assert success is True
        assert content == "rst content"
        mock_extract.assert_called_once_with("example.com/pkg")
        mock_convert.assert_called_once_with("godoc output")

    @patch.object(GoDocExtractor, "extract_package_doc")
    def test_extract_and_convert_failure(self, mock_extract):
        """Test extract_and_convert when extraction fails."""
        mock_extract.return_value = None

        extractor = GoDocExtractor()
        success, content = extractor.extract_and_convert("example.com/pkg")

        assert success is False
        assert "Automatic documentation extraction" in content
        assert "example.com/pkg" in content
        assert "Go is not installed" in content

    @patch.object(GoDocExtractor, "extract_and_convert")
    def test_extract_multiple_packages(self, mock_extract_convert):
        """Test extract_multiple_packages with multiple packages."""
        mock_extract_convert.side_effect = [
            (True, "content1"),
            (False, "fallback2"),
            (True, "content3"),
        ]

        extractor = GoDocExtractor()
        results = extractor.extract_multiple_packages(
            [
                "pkg1",
                "pkg2",
                "pkg3",
            ]
        )

        assert len(results) == 3
        assert results[0] == ("pkg1", True, "content1")
        assert results[1] == ("pkg2", False, "fallback2")
        assert results[2] == ("pkg3", True, "content3")

    def test_convert_to_rst_empty_lines_at_start(self):
        """Test convert_to_rst skips empty lines at start."""
        extractor = GoDocExtractor()
        godoc = "\n\n\npackage example\n\nDocumentation."

        result = extractor.convert_to_rst(godoc)
        # Should not have leading empty lines
        assert not result.startswith("\n\n")
        assert "Documentation." in result

    def test_convert_to_rst_preserves_empty_lines(self):
        """Test convert_to_rst preserves empty lines in content."""
        extractor = GoDocExtractor()
        godoc = """package example

First paragraph.

Second paragraph."""

        result = extractor.convert_to_rst(godoc)
        # Should have empty line between paragraphs
        assert "First paragraph.\n\nSecond paragraph." in result

    def test_convert_to_rst_code_block_closes_before_new_declaration(self):
        """Test code block closes when new declaration starts."""
        extractor = GoDocExtractor()
        godoc = """package example

func First() int
    Documentation for first.

func Second() string
    Documentation for second."""

        result = extractor.convert_to_rst(godoc)
        # Should have two separate code blocks
        assert result.count(".. code-block:: go") == 2
        assert "func First() int" in result
        assert "func Second() string" in result
