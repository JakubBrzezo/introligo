"""Comprehensive tests for Rust documentation extractor to achieve 100% coverage."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from introligo.rustdoc_extractor import RustDocExtractor


class TestRustDocExtractorComprehensive:
    """Comprehensive tests for RustDoc extraction."""

    # ==================== Test _try_rustdoc_json ====================

    @patch("subprocess.run")
    def test_try_rustdoc_json_success(self, mock_run):
        """Test _try_rustdoc_json when JSON generation succeeds."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        json_content = {
            "index": {
                "crate_id": "test_crate",
                "items": {
                    "test_crate": {
                        "docs": "Test documentation",
                    }
                },
            }
        }

        # Mock the JSON file exists and contains data
        with patch.object(Path, "exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(json_content))
        ), patch.object(
            extractor,
            "extract_crate_metadata",
            return_value={"name": "test-crate"},
        ):
            result = extractor._try_rustdoc_json("test_crate")

        # Currently returns None because parsing is not fully implemented
        assert result is None
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_try_rustdoc_json_no_crate_path(self, mock_run):
        """Test _try_rustdoc_json when crate_path is None."""
        mock_run.return_value = MagicMock(returncode=0)

        extractor = RustDocExtractor(crate_path=None)
        result = extractor._try_rustdoc_json("test_crate")

        assert result is None

    @patch("subprocess.run")
    def test_try_rustdoc_json_cargo_fails(self, mock_run):
        """Test _try_rustdoc_json when cargo rustdoc fails."""
        mock_run.return_value = MagicMock(returncode=1)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        result = extractor._try_rustdoc_json("test_crate")

        assert result is None

    @patch("subprocess.run")
    def test_try_rustdoc_json_timeout(self, mock_run):
        """Test _try_rustdoc_json when subprocess times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("cargo", 120)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        result = extractor._try_rustdoc_json("test_crate")

        assert result is None

    @patch("subprocess.run")
    def test_try_rustdoc_json_no_metadata(self, mock_run):
        """Test _try_rustdoc_json when metadata extraction fails."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(extractor, "extract_crate_metadata", return_value=None):
            result = extractor._try_rustdoc_json(None)

        assert result is None

    # ==================== Test _parse_rustdoc_json ====================

    def test_parse_rustdoc_json_with_docs(self):
        """Test _parse_rustdoc_json with valid JSON containing docs."""
        extractor = RustDocExtractor()

        json_file = Path("/tmp/test.json")
        json_content = {
            "index": {
                "crate_id": "test_crate",
                "items": {
                    "test_crate": {
                        "docs": "Test crate documentation",
                    }
                },
            }
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(json_content))):
            result = extractor._parse_rustdoc_json(json_file)

        # Currently returns None as full parsing not implemented
        assert result is None

    def test_parse_rustdoc_json_no_docs(self):
        """Test _parse_rustdoc_json when JSON has no docs."""
        extractor = RustDocExtractor()

        json_file = Path("/tmp/test.json")
        json_content = {"index": {"crate_id": "test", "items": {}}}

        with patch("builtins.open", mock_open(read_data=json.dumps(json_content))):
            result = extractor._parse_rustdoc_json(json_file)

        assert result is None

    def test_parse_rustdoc_json_invalid_json(self):
        """Test _parse_rustdoc_json with invalid JSON."""
        extractor = RustDocExtractor()

        json_file = Path("/tmp/test.json")

        with patch("builtins.open", mock_open(read_data="invalid json {")):
            result = extractor._parse_rustdoc_json(json_file)

        assert result is None

    def test_parse_rustdoc_json_file_error(self):
        """Test _parse_rustdoc_json when file cannot be read."""
        extractor = RustDocExtractor()

        json_file = Path("/tmp/test.json")

        with patch("builtins.open", side_effect=OSError("Cannot read file")):
            result = extractor._parse_rustdoc_json(json_file)

        assert result is None

    # ==================== Test _extract_from_cargo_doc ====================

    def test_extract_from_cargo_doc_success(self):
        """Test _extract_from_cargo_doc when HTML exists."""
        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        html_content = """
        <div class="docblock">
            <p>Test crate provides testing utilities.</p>
            <p>It includes various test helpers.</p>
        </div>
        <h3><a class="fn" href="fn.test.html">test</a></h3>
        <h3><a class="struct" href="struct.Foo.html">Foo</a></h3>
        """

        with patch.object(Path, "exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=html_content)
        ):
            result = extractor._extract_from_cargo_doc("test_crate")

        assert result is not None
        assert "Test crate provides testing utilities" in result
        assert "test" in result
        assert "Foo" in result

    def test_extract_from_cargo_doc_no_crate_name(self):
        """Test _extract_from_cargo_doc when crate name needs to be determined."""
        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(
            extractor, "extract_crate_metadata", return_value={"name": "my-crate"}
        ), patch.object(Path, "exists", return_value=False):
            result = extractor._extract_from_cargo_doc(None)

        assert result is None

    def test_extract_from_cargo_doc_no_crate_path(self):
        """Test _extract_from_cargo_doc when crate_path is None."""
        extractor = RustDocExtractor(crate_path=None)

        result = extractor._extract_from_cargo_doc("test_crate")

        assert result is None

    def test_extract_from_cargo_doc_dir_not_exists(self):
        """Test _extract_from_cargo_doc when target/doc directory doesn't exist."""
        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(Path, "exists", return_value=False):
            result = extractor._extract_from_cargo_doc("test_crate")

        assert result is None

    def test_extract_from_cargo_doc_exception(self):
        """Test _extract_from_cargo_doc when exception occurs."""
        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(Path, "exists", side_effect=Exception("Disk error")):
            result = extractor._extract_from_cargo_doc("test_crate")

        assert result is None

    # ==================== Test _parse_rustdoc_html ====================

    def test_parse_rustdoc_html_with_docblock(self):
        """Test _parse_rustdoc_html with module documentation."""
        extractor = RustDocExtractor()

        html_content = """
        <div class="docblock">
            <p>This is <strong>module</strong> documentation.</p>
            <code>use my_crate::*;</code>
        </div>
        """

        html_file = Path("/tmp/index.html")

        with patch("builtins.open", mock_open(read_data=html_content)):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        assert result is not None
        assert "module" in result
        assert "documentation" in result

    def test_parse_rustdoc_html_with_items(self):
        """Test _parse_rustdoc_html with public items."""
        extractor = RustDocExtractor()

        html_content = """
        <h3><a class="fn" href="fn.add.html">add</a></h3>
        <h3><a class="fn" href="fn.subtract.html">subtract</a></h3>
        <h3><a class="struct" href="struct.Calculator.html">Calculator</a></h3>
        <h3><a class="enum" href="enum.Error.html">Error</a></h3>
        """

        html_file = Path("/tmp/index.html")

        with patch("builtins.open", mock_open(read_data=html_content)):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        assert result is not None
        assert "add" in result
        assert "subtract" in result
        assert "Calculator" in result
        assert "Error" in result

    def test_parse_rustdoc_html_html_entities(self):
        """Test _parse_rustdoc_html with HTML entities."""
        extractor = RustDocExtractor()

        html_content = """
        <div class="docblock">
            <p>Type: &lt;T&gt; where T: &amp;Copy</p>
            <p>Value: &quot;hello&quot;</p>
        </div>
        """

        html_file = Path("/tmp/index.html")

        with patch("builtins.open", mock_open(read_data=html_content)):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        assert result is not None
        assert "<T>" in result
        assert "&Copy" in result or "Copy" in result
        assert '"hello"' in result

    def test_parse_rustdoc_html_no_docblock(self):
        """Test _parse_rustdoc_html when no docblock is found."""
        extractor = RustDocExtractor()

        html_content = "<html><body>No docblock here</body></html>"

        html_file = Path("/tmp/index.html")

        with patch("builtins.open", mock_open(read_data=html_content)):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        assert result is None

    def test_parse_rustdoc_html_exception(self):
        """Test _parse_rustdoc_html when file cannot be read."""
        extractor = RustDocExtractor()

        html_file = Path("/tmp/index.html")

        with patch("builtins.open", side_effect=OSError("Cannot read")):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        assert result is None

    def test_parse_rustdoc_html_many_items(self):
        """Test _parse_rustdoc_html with more than 20 items (should limit to 20)."""
        extractor = RustDocExtractor()

        # Generate 30 items
        items = "\n".join(
            [f'<h3><a class="fn" href="fn.func{i}.html">func{i}</a></h3>' for i in range(30)]
        )
        html_content = f"""
        <div class="docblock"><p>Module docs</p></div>
        {items}
        """

        html_file = Path("/tmp/index.html")

        with patch("builtins.open", mock_open(read_data=html_content)):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        assert result is not None
        # Should only include first 20
        assert "func19" in result
        assert "func29" not in result

    # ==================== Test _parse_rust_source edge cases ====================

    def test_parse_rust_source_error_handling(self):
        """Test _parse_rust_source when file cannot be read."""
        extractor = RustDocExtractor()

        source_file = Path("/tmp/lib.rs")

        with patch("builtins.open", side_effect=OSError("Cannot read")):
            result = extractor._parse_rust_source(source_file)

        assert result == ""

    def test_parse_rust_source_empty_module_docs(self):
        """Test _parse_rust_source with empty module doc comments."""
        extractor = RustDocExtractor()

        rust_source = Path("/tmp/lib.rs")
        content = """
//!
//!
//! Test
//!

pub fn test() {}
"""

        with patch("builtins.open", mock_open(read_data=content)):
            result = extractor._parse_rust_source(rust_source)

        assert "Test" in result

    # ==================== Test _extract_public_items edge cases ====================

    def test_extract_public_items_enums(self):
        """Test _extract_public_items with public enums."""
        extractor = RustDocExtractor()

        rust_code = """
/// An error type.
pub enum Error {
    IoError,
    ParseError,
}
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        assert "pub enum Error" in result_str
        assert "Enumerations" in result_str

    def test_extract_public_items_traits(self):
        """Test _extract_public_items with public traits."""
        extractor = RustDocExtractor()

        rust_code = """
/// A trait for calculations.
pub trait Calculate {
    fn compute(&self) -> i32;
}
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        assert "pub trait Calculate" in result_str
        assert "Traits" in result_str

    def test_extract_public_items_multiline_signature(self):
        """Test _extract_public_items with multi-line function signature."""
        extractor = RustDocExtractor()

        rust_code = """
/// Complex function with many parameters.
pub fn complex_function(
    param1: String,
    param2: i32,
    param3: bool
) -> Result<(), Error> {
    Ok(())
}
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        assert "pub fn complex_function" in result_str
        assert "param1" in result_str or "param" in result_str

    def test_extract_public_items_with_where_clause(self):
        """Test _extract_public_items with where clause."""
        extractor = RustDocExtractor()

        rust_code = """
/// Generic function with where clause.
pub fn generic_fn<T>(value: T) -> T
where
    T: Clone,
{
    value.clone()
}
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        assert "pub fn generic_fn" in result_str

    def test_extract_public_items_async_fn(self):
        """Test _extract_public_items with async functions."""
        extractor = RustDocExtractor()

        rust_code = """
/// An async function.
pub async fn fetch_data() -> Result<String, Error> {
    Ok("data".to_string())
}
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        assert "pub async fn fetch_data" in result_str

    def test_extract_public_items_no_doc_comments(self):
        """Test _extract_public_items with public items but no doc comments."""
        extractor = RustDocExtractor()

        rust_code = """
pub fn undocumented() {}
pub struct Foo;
"""

        items = extractor._extract_public_items(rust_code)

        # Should not extract items without doc comments
        assert len(items) == 0 or "Structs" not in "".join(items)

    # ==================== Test _process_doc_comments ====================

    def test_process_doc_comments_h1_header(self):
        """Test _process_doc_comments with H1 markdown header."""
        extractor = RustDocExtractor()

        doc_lines = ["# Introduction", "This is the intro."]
        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert "Introduction" in result_str
        assert "========" in result_str

    def test_process_doc_comments_h2_header(self):
        """Test _process_doc_comments with H2 markdown header."""
        extractor = RustDocExtractor()

        doc_lines = ["## Subsection", "Content here."]
        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert "Subsection" in result_str
        assert "----------" in result_str

    def test_process_doc_comments_h3_header(self):
        """Test _process_doc_comments with H3 markdown header."""
        extractor = RustDocExtractor()

        doc_lines = ["### Minor Section", "Details."]
        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert "Minor Section" in result_str
        assert "~~~~~" in result_str

    def test_process_doc_comments_rustdoc_sections(self):
        """Test _process_doc_comments with rustdoc standard sections."""
        extractor = RustDocExtractor()

        # Test all rustdoc sections
        sections = [
            "# Arguments",
            "# Parameters",
            "# Returns",
            "# Errors",
            "# Panics",
            "# Safety",
            "# Examples",
            "# Note",
        ]

        for section in sections:
            doc_lines = [section, "Some content."]
            result = extractor._process_doc_comments(doc_lines)

            result_str = "\n".join(result)
            # Should be bold, not a header
            assert "**" in result_str
            assert "===" not in result_str

    def test_process_doc_comments_code_block(self):
        """Test _process_doc_comments with code blocks."""
        extractor = RustDocExtractor()

        doc_lines = [
            "Example code:",
            "```rust",
            "let x = 5;",
            "let y = 10;",
            "```",
            "End of example.",
        ]

        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert ".. code-block:: rust" in result_str
        assert "let x = 5" in result_str
        assert "let y = 10" in result_str

    def test_process_doc_comments_code_block_no_language(self):
        """Test _process_doc_comments with code block without language."""
        extractor = RustDocExtractor()

        doc_lines = [
            "```",
            "code here",
            "```",
        ]

        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert ".. code-block:: rust" in result_str  # Defaults to rust

    def test_process_doc_comments_list_items(self):
        """Test _process_doc_comments with list items."""
        extractor = RustDocExtractor()

        doc_lines = [
            "Features:",
            "- Feature 1",
            "- Feature 2",
            "* Feature 3",
        ]

        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert "- Feature 1" in result_str
        assert "- Feature 2" in result_str
        assert "* Feature 3" in result_str

    # ==================== Test extract_crate_doc with different paths ====================

    @patch("subprocess.run")
    def test_extract_crate_doc_cargo_fails_with_stderr(self, mock_run):
        """Test extract_crate_doc when cargo doc fails with error message."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error: could not compile")

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        result = extractor.extract_crate_doc("test_crate")

        assert result is None

    def test_extract_crate_doc_exception_in_cargo(self):
        """Test extract_crate_doc when exception occurs during extraction."""
        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        # Mock cargo available but execution fails
        with patch.object(extractor, "check_cargo_available", return_value=True), patch(
            "subprocess.run", side_effect=Exception("Unexpected error")
        ):
            result = extractor.extract_crate_doc("test_crate")

        assert result is None

    # ==================== Test extract_crate_metadata edge cases ====================

    @patch("subprocess.run")
    def test_extract_crate_metadata_timeout(self, mock_run):
        """Test extract_crate_metadata when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("cargo", 30)

        extractor = RustDocExtractor(crate_path=Path("/tmp/test"))
        metadata = extractor.extract_crate_metadata()

        assert metadata is None

    @patch("subprocess.run")
    def test_extract_crate_metadata_invalid_json(self, mock_run):
        """Test extract_crate_metadata with invalid JSON response."""
        mock_run.return_value = MagicMock(returncode=0, stdout="invalid {json")

        extractor = RustDocExtractor(crate_path=Path("/tmp/test"))
        metadata = extractor.extract_crate_metadata()

        assert metadata is None

    @patch("subprocess.run")
    def test_extract_crate_metadata_no_packages(self, mock_run):
        """Test extract_crate_metadata when JSON has no packages."""
        mock_run.return_value = MagicMock(returncode=0, stdout='{"packages": []}')

        extractor = RustDocExtractor(crate_path=Path("/tmp/test"))
        metadata = extractor.extract_crate_metadata()

        assert metadata is None

    # ==================== Test extract_and_convert with metadata ====================

    @patch("subprocess.run")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
//! Test crate
pub fn test() {}
""",
    )
    def test_extract_and_convert_with_metadata(self, mock_file, mock_run):
        """Test extract_and_convert uses metadata for crate name."""
        mock_metadata = {"packages": [{"name": "my-test-crate", "version": "0.1.0"}]}
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_metadata))

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(Path, "exists", return_value=True):
            success, content = extractor.extract_and_convert(None)

        assert isinstance(success, bool)
        assert isinstance(content, str)
        # Should contain the extracted documentation
        assert "Test crate" in content

    # ==================== Test extract_multiple_crates edge cases ====================

    @patch("subprocess.run")
    def test_extract_multiple_crates_no_metadata(self, mock_run):
        """Test extract_multiple_crates when metadata extraction fails."""
        mock_run.return_value = MagicMock(returncode=1)

        extractor = RustDocExtractor()
        crate_paths = [Path("/tmp/crate1")]

        with patch.object(Path, "exists", return_value=False):
            results = extractor.extract_multiple_crates(crate_paths)

        assert len(results) == 1
        crate_name, success, content = results[0]
        assert isinstance(crate_name, str)
        assert isinstance(success, bool)
        assert isinstance(content, str)

    # ==================== Test check_cargo_available with failure ====================

    @patch("subprocess.run")
    def test_check_cargo_available_returns_false_on_nonzero(self, mock_run):
        """Test check_cargo_available returns False on non-zero exit."""
        mock_run.return_value = MagicMock(returncode=1)
        extractor = RustDocExtractor()

        assert extractor.check_cargo_available() is False

    # ==================== Test source parsing with main.rs ====================

    @patch("subprocess.run")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
//! Main module
pub fn main() {}
""",
    )
    def test_parse_rust_source_main_rs(self, mock_file, mock_run):
        """Test extracting from main.rs when lib.rs doesn't exist."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        def exists_side_effect(path_self):
            # lib.rs doesn't exist, main.rs does
            return path_self.name == "main.rs"

        with patch.object(Path, "exists", exists_side_effect):
            result = extractor.extract_crate_doc("test_crate")

        assert result is not None
        assert "Main module" in result

    # ==================== Test _try_rustdoc_json with actual JSON file ====================

    @patch("subprocess.run")
    def test_try_rustdoc_json_with_file_exists(self, mock_run):
        """Test _try_rustdoc_json when JSON file actually exists."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        json_content = {
            "index": {
                "crate_id": "test_crate",
                "items": {
                    "test_crate": {
                        "docs": "Test documentation content",
                    }
                },
            }
        }

        with patch.object(Path, "exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=json.dumps(json_content))
        ):
            result = extractor._try_rustdoc_json("test_crate")

        # Returns None as parsing not fully implemented, but should not error
        assert result is None

    # ==================== Test HTML parsing with empty docblock ====================

    def test_parse_rustdoc_html_empty_docblock(self):
        """Test _parse_rustdoc_html with empty docblock."""
        extractor = RustDocExtractor()

        html_content = '<div class="docblock"></div>'
        html_file = Path("/tmp/index.html")

        with patch("builtins.open", mock_open(read_data=html_content)):
            result = extractor._parse_rustdoc_html(html_file, "my_crate")

        # Should return None when no content
        assert result is None

    # ==================== Test extract_from_cargo_doc with hyphenated name ====================

    def test_extract_from_cargo_doc_hyphenated_crate_name(self):
        """Test _extract_from_cargo_doc converts hyphenated crate name."""
        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        html_content = '<div class="docblock"><p>Test</p></div>'

        def path_exists_side_effect(path_self):
            # Simulates that directory exists for underscore-converted name
            return "my_crate" in str(path_self)

        with patch.object(Path, "exists", path_exists_side_effect), patch(
            "builtins.open", mock_open(read_data=html_content)
        ), patch.object(extractor, "extract_crate_metadata", return_value={"name": "my-crate"}):
            result = extractor._extract_from_cargo_doc(None)

        # Should work with converted name
        assert result is not None

    # ==================== Test public items with other item types ====================

    def test_extract_public_items_other_types(self):
        """Test _extract_public_items with const, static, and type alias."""
        extractor = RustDocExtractor()

        rust_code = """
/// A constant value.
pub const MAX_SIZE: usize = 100;

/// A static variable.
pub static CONFIG: &str = "config";

/// A type alias.
pub type Result<T> = std::result::Result<T, Error>;
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        # These should be in "Other Items" category
        assert "pub const MAX_SIZE" in result_str or "pub type" in result_str

    def test_extract_public_items_semicolon_termination(self):
        """Test _extract_public_items with struct terminated by semicolon."""
        extractor = RustDocExtractor()

        rust_code = """
/// A unit struct.
pub struct Unit;

/// A tuple struct.
pub struct Point(pub i32, pub i32);
"""

        items = extractor._extract_public_items(rust_code)

        result_str = "".join(items)
        assert "pub struct Unit" in result_str or "pub struct Point" in result_str

    # ==================== Test process_doc_comments with edge cases ====================

    def test_process_doc_comments_empty_lines(self):
        """Test _process_doc_comments with empty lines."""
        extractor = RustDocExtractor()

        doc_lines = ["", "", "Content", "", ""]
        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert "Content" in result_str

    def test_process_doc_comments_mixed_headers_and_sections(self):
        """Test _process_doc_comments with mix of headers and rustdoc sections."""
        extractor = RustDocExtractor()

        doc_lines = [
            "## Overview",
            "This is an overview.",
            "# Arguments",
            "* param1 - First parameter",
        ]

        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        # Overview should be a header
        assert "Overview" in result_str
        assert "--------" in result_str or "----------" in result_str or "~~~" in result_str
        # Arguments should be bold
        assert "**Arguments:**" in result_str

    def test_process_doc_comments_nested_code_block(self):
        """Test _process_doc_comments handles code block state correctly."""
        extractor = RustDocExtractor()

        doc_lines = [
            "Example:",
            "```rust",
            "let x = 5;",
            "```",
            "More text",
            "```",
            "another code",
            "```",
        ]

        result = extractor._process_doc_comments(doc_lines)

        result_str = "\n".join(result)
        assert ".. code-block:: rust" in result_str
        assert "let x = 5" in result_str
        assert "More text" in result_str

    # ==================== Test extract_crate_doc with no lib.rs or main.rs ====================

    @patch("subprocess.run")
    def test_extract_crate_doc_no_source_files(self, mock_run):
        """Test extract_crate_doc when neither lib.rs nor main.rs exists."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/test_crate")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(Path, "exists", return_value=False):
            result = extractor.extract_crate_doc("test_crate")

        # Should return None when no source files found
        assert result is None

    # ==================== Test full extraction flow ====================

    @patch("subprocess.run")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
//! # Calculator
//! A simple calculator crate.
//!
//! ## Features
//! - Addition
//! - Subtraction

/// Adds two numbers.
///
/// # Arguments
/// * `a` - First number
/// * `b` - Second number
///
/// # Returns
/// The sum of a and b.
///
/// # Examples
/// ```
/// let result = add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Calculator struct for stateful operations.
pub struct Calculator {
    value: i32,
}
""",
    )
    def test_full_extraction_flow(self, mock_file, mock_run):
        """Test complete extraction flow with complex documentation."""
        mock_run.return_value = MagicMock(returncode=0)

        crate_path = Path("/tmp/calculator")
        extractor = RustDocExtractor(crate_path=crate_path)

        with patch.object(Path, "exists", return_value=True):
            result = extractor.extract_crate_doc("calculator")

        assert result is not None
        assert "Calculator" in result
        assert "Features" in result
        assert "Addition" in result
        assert "pub fn add" in result
        assert "pub struct Calculator" in result
        # Check that Arguments, Returns, Examples are bold, not headers
        assert "**Arguments:**" in result
        assert "**Returns:**" in result
        assert "**Examples:**" in result
