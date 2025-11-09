"""Tests for Java documentation extractor."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from introligo.javadoc_extractor import JavaDocExtractor


class TestJavaDocExtractor:
    """Test JavaDoc extraction and conversion."""

    def test_init_without_path(self):
        """Test initialization without source path."""
        extractor = JavaDocExtractor()
        assert extractor.source_path is None

    def test_init_with_path(self):
        """Test initialization with source path."""
        path = Path("/tmp/test")
        extractor = JavaDocExtractor(source_path=path)
        assert extractor.source_path == path

    @patch("subprocess.run")
    def test_check_java_available_success(self, mock_run):
        """Test check_java_available when Java and javadoc are installed."""
        mock_run.return_value = MagicMock(returncode=0)
        extractor = JavaDocExtractor()

        assert extractor.check_java_available() is True
        assert mock_run.call_count == 2
        # Check both java and javadoc were tested
        mock_run.assert_any_call(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        mock_run.assert_any_call(
            ["javadoc", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_check_java_available_java_not_found(self, mock_run):
        """Test check_java_available when Java is not installed."""
        mock_run.side_effect = FileNotFoundError()
        extractor = JavaDocExtractor()

        assert extractor.check_java_available() is False

    @patch("subprocess.run")
    def test_check_java_available_javadoc_not_found(self, mock_run):
        """Test check_java_available when javadoc is not installed."""
        mock_run.side_effect = [
            MagicMock(returncode=0),  # java works
            FileNotFoundError(),  # javadoc not found
        ]
        extractor = JavaDocExtractor()

        assert extractor.check_java_available() is False

    @patch("subprocess.run")
    def test_check_java_available_timeout(self, mock_run):
        """Test check_java_available when command times out."""
        mock_run.side_effect = subprocess.TimeoutExpired("java", 5)
        extractor = JavaDocExtractor()

        assert extractor.check_java_available() is False

    @patch("builtins.open", new_callable=mock_open, read_data="public class Test {}")
    def test_extract_from_source_success(self, mock_file):
        """Test successful source extraction from Java file."""
        extractor = JavaDocExtractor()
        result = extractor.extract_from_source(Path("/tmp/Test.java"))

        assert result == "public class Test {}"
        mock_file.assert_called_once()

    @patch("introligo.javadoc_extractor.open", side_effect=FileNotFoundError())
    def test_extract_from_source_file_not_found(self, mock_file):
        """Test extract_from_source when file doesn't exist."""
        extractor = JavaDocExtractor()
        result = extractor.extract_from_source(Path("/tmp/NotFound.java"))

        assert result is None

    @patch(
        "introligo.javadoc_extractor.open",
        side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, ""),
    )
    def test_extract_from_source_encoding_error(self, mock_file):
        """Test extract_from_source when file has encoding issues."""
        extractor = JavaDocExtractor()
        result = extractor.extract_from_source(Path("/tmp/Bad.java"))

        assert result is None

    def test_parse_java_source_empty_input(self):
        """Test parse_java_source with empty input."""
        extractor = JavaDocExtractor()
        result = extractor.parse_java_source("")
        assert result == ""

    def test_parse_java_source_class_declaration(self):
        """Test parse_java_source handles class declarations."""
        extractor = JavaDocExtractor()
        java_code = """
/**
 * A simple test class.
 */
public class TestClass {
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public class TestClass" in result
        assert "A simple test class." in result

    def test_parse_java_source_interface_declaration(self):
        """Test parse_java_source handles interface declarations."""
        extractor = JavaDocExtractor()
        java_code = """
/**
 * A test interface.
 */
public interface TestInterface {
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public interface TestInterface" in result
        assert "A test interface." in result

    def test_parse_java_source_method_declaration(self):
        """Test parse_java_source handles method declarations."""
        extractor = JavaDocExtractor()
        java_code = """
public class Test {
    /**
     * Adds two numbers.
     * @param a First number
     * @param b Second number
     * @return Sum of a and b
     */
    public int add(int a, int b) {
        return a + b;
    }
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public int add(int a, int b)" in result
        assert "Adds two numbers." in result
        assert "**Parameters:**" in result
        assert "``a``" in result
        assert "First number" in result
        assert "**Returns:**" in result
        assert "Sum of a and b" in result

    def test_parse_java_source_field_declaration(self):
        """Test parse_java_source handles field declarations."""
        extractor = JavaDocExtractor()
        java_code = """
public class Test {
    /**
     * Maximum size constant.
     */
    public static final int MAX_SIZE = 100;
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public static final int MAX_SIZE = 100;" in result
        assert "Maximum size constant." in result

    def test_parse_java_source_method_with_throws(self):
        """Test parse_java_source handles methods with @throws."""
        extractor = JavaDocExtractor()
        java_code = """
public class Test {
    /**
     * Opens a file.
     * @param filename Name of the file
     * @return File content
     * @throws IOException If file cannot be read
     */
    public String readFile(String filename) throws IOException {
        return "";
    }
}
"""
        result = extractor.parse_java_source(java_code)
        assert "**Throws:**" in result
        assert "``IOException``" in result
        assert "If file cannot be read" in result

    def test_parse_java_source_multiline_method(self):
        """Test parse_java_source handles multi-line method signatures."""
        extractor = JavaDocExtractor()
        java_code = """
public class Test {
    public void process(
        String name,
        int value,
        boolean flag) {
    }
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public void process(" in result

    def test_convert_javadoc_to_rst_empty(self):
        """Test _convert_javadoc_to_rst with empty javadoc."""
        extractor = JavaDocExtractor()
        result = extractor._convert_javadoc_to_rst([])
        assert result == []

    def test_convert_javadoc_to_rst_basic_description(self):
        """Test _convert_javadoc_to_rst with basic description."""
        extractor = JavaDocExtractor()
        javadoc = [
            "/**",
            " * This is a description.",
            " * It spans multiple lines.",
            " */",
        ]
        result = extractor._convert_javadoc_to_rst(javadoc)

        rst_content = "\n".join(result)
        assert "This is a description." in rst_content
        assert "It spans multiple lines." in rst_content

    def test_convert_javadoc_to_rst_with_params(self):
        """Test _convert_javadoc_to_rst with parameters."""
        extractor = JavaDocExtractor()
        javadoc = [
            "/**",
            " * Method description.",
            " * @param x The x coordinate",
            " * @param y The y coordinate",
            " */",
        ]
        result = extractor._convert_javadoc_to_rst(javadoc)

        rst_content = "\n".join(result)
        assert "**Parameters:**" in rst_content
        assert "``x``" in rst_content
        assert "The x coordinate" in rst_content
        assert "``y``" in rst_content

    def test_convert_javadoc_to_rst_with_return(self):
        """Test _convert_javadoc_to_rst with return value."""
        extractor = JavaDocExtractor()
        javadoc = [
            "/**",
            " * Calculates distance.",
            " * @return The distance",
            " */",
        ]
        result = extractor._convert_javadoc_to_rst(javadoc)

        rst_content = "\n".join(result)
        assert "**Returns:**" in rst_content
        assert "The distance" in rst_content

    def test_convert_javadoc_to_rst_with_exception(self):
        """Test _convert_javadoc_to_rst with @exception tag."""
        extractor = JavaDocExtractor()
        javadoc = [
            "/**",
            " * Opens connection.",
            " * @exception IOException If connection fails",
            " */",
        ]
        result = extractor._convert_javadoc_to_rst(javadoc)

        rst_content = "\n".join(result)
        assert "**Throws:**" in rst_content
        assert "``IOException``" in rst_content
        assert "If connection fails" in rst_content

    @patch.object(JavaDocExtractor, "extract_from_source")
    @patch.object(JavaDocExtractor, "parse_java_source")
    def test_extract_and_convert_success(self, mock_parse, mock_extract):
        """Test extract_and_convert when extraction succeeds."""
        mock_extract.return_value = "java source"
        mock_parse.return_value = "rst content"

        extractor = JavaDocExtractor()
        success, content = extractor.extract_and_convert(Path("/tmp/Test.java"), "Test")

        assert success is True
        assert content == "rst content"
        mock_extract.assert_called_once()
        mock_parse.assert_called_once_with("java source", "Test")

    @patch.object(JavaDocExtractor, "extract_from_source")
    def test_extract_and_convert_failure(self, mock_extract):
        """Test extract_and_convert when extraction fails."""
        mock_extract.return_value = None

        extractor = JavaDocExtractor()
        success, content = extractor.extract_and_convert(Path("/tmp/Test.java"))

        assert success is False
        assert "Automatic documentation extraction" in content
        assert "Test.java" in content

    @patch.object(JavaDocExtractor, "extract_and_convert")
    def test_extract_multiple_files(self, mock_extract_convert):
        """Test extract_multiple_files with multiple Java files."""
        mock_extract_convert.side_effect = [
            (True, "content1"),
            (False, "fallback2"),
            (True, "content3"),
        ]

        extractor = JavaDocExtractor()
        results = extractor.extract_multiple_files(
            [
                Path("/tmp/File1.java"),
                Path("/tmp/File2.java"),
                Path("/tmp/File3.java"),
            ]
        )

        assert len(results) == 3
        assert results[0] == ("File1.java", True, "content1")
        assert results[1] == ("File2.java", False, "fallback2")
        assert results[2] == ("File3.java", True, "content3")

    @patch.object(JavaDocExtractor, "extract_and_convert")
    def test_extract_package_success(self, mock_extract_convert):
        """Test extract_package with valid package directory."""
        mock_extract_convert.side_effect = [
            (True, "class1 content"),
            (True, "class2 content"),
        ]

        extractor = JavaDocExtractor()

        # Create a mock directory with Java files
        with patch.object(Path, "exists", return_value=True), patch.object(
            Path, "is_dir", return_value=True
        ), patch.object(
            Path,
            "glob",
            return_value=[
                Path("/tmp/pkg/Class1.java"),
                Path("/tmp/pkg/Class2.java"),
            ],
        ):
            success, content = extractor.extract_package(Path("/tmp/pkg"), "com.example.pkg")

        assert success is True
        assert "Package: ``com.example.pkg``" in content
        assert "class1 content" in content
        assert "class2 content" in content

    def test_extract_package_directory_not_found(self):
        """Test extract_package when directory doesn't exist."""
        extractor = JavaDocExtractor()

        with patch.object(Path, "exists", return_value=False):
            success, content = extractor.extract_package(Path("/tmp/notfound"), "com.example.pkg")

        assert success is False
        assert "not found" in content
        assert "com.example.pkg" in content

    @patch.object(Path, "glob", return_value=[])
    def test_extract_package_no_java_files(self, mock_glob):
        """Test extract_package when no Java files found."""
        extractor = JavaDocExtractor()

        with patch.object(Path, "exists", return_value=True), patch.object(
            Path, "is_dir", return_value=True
        ):
            success, content = extractor.extract_package(Path("/tmp/empty"), "com.example.empty")

        assert success is False
        assert "No Java files found" in content
        assert "com.example.empty" in content

    def test_parse_java_source_abstract_class(self):
        """Test parse_java_source handles abstract classes."""
        extractor = JavaDocExtractor()
        java_code = """
/**
 * Abstract base class.
 */
public abstract class BaseClass {
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public abstract class BaseClass" in result

    def test_parse_java_source_final_class(self):
        """Test parse_java_source handles final classes."""
        extractor = JavaDocExtractor()
        java_code = """
/**
 * Final utility class.
 */
public final class Utils {
}
"""
        result = extractor.parse_java_source(java_code)
        assert ".. code-block:: java" in result
        assert "public final class Utils" in result

    def test_parse_java_source_static_method(self):
        """Test parse_java_source handles static methods."""
        extractor = JavaDocExtractor()
        java_code = """
public class Math {
    /**
     * Static helper method.
     */
    public static int square(int n) {
        return n * n;
    }
}
"""
        result = extractor.parse_java_source(java_code)
        assert "public static int square(int n)" in result

    def test_parse_java_source_generic_types(self):
        """Test parse_java_source handles generic types."""
        extractor = JavaDocExtractor()
        java_code = """
public class Container {
    /**
     * Generic method.
     */
    public <T> List<T> getList() {
        return null;
    }
}
"""
        result = extractor.parse_java_source(java_code)
        # Should handle generics in the signature
        assert "code-block:: java" in result

    def test_parse_java_source_array_types(self):
        """Test parse_java_source handles array types."""
        extractor = JavaDocExtractor()
        java_code = """
public class Arrays {
    /**
     * Array field.
     */
    private String[] items;
}
"""
        result = extractor.parse_java_source(java_code)
        assert "String[] items" in result

    def test_parse_java_source_edge_case_end_of_file_after_javadoc(self):
        """Test parse_java_source when javadoc is at end of file without declaration."""
        extractor = JavaDocExtractor()
        # This covers line 107 - break when reaching end of lines
        java_code = """
/**
 * Documentation at end of file.
 */
"""
        result = extractor.parse_java_source(java_code)
        # Should handle gracefully without crashing
        assert result is not None

    def test_convert_javadoc_with_skip_tags(self):
        """Test _convert_javadoc_to_rst with tags that should be skipped."""
        extractor = JavaDocExtractor()
        # This covers line 226 - continue for @version, @since, @see, @deprecated tags
        javadoc_lines = [
            "Class description.",
            "@version 1.0",
            "@since 2020",
            "@see OtherClass",
            "@deprecated Use NewClass instead",
            "@param name The name parameter",
        ]
        result = extractor._convert_javadoc_to_rst(javadoc_lines)
        result_str = "\n".join(result)
        # Should have description and param but skip version/since/see/deprecated tags
        assert "Class description" in result_str
        assert "name" in result_str or "Parameters" in result_str
        # These tags should be skipped (line 226)
        assert "@version" not in result_str
        assert "@since" not in result_str
        assert "@see" not in result_str
        assert "@deprecated" not in result_str
