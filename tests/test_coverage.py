"""Additional tests to achieve 100% code coverage."""

from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from introligo import IncludeLoader, IntroligoError, IntroligoGenerator, PageNode


class TestIncludeLoaderEdgeCases:
    """Test IncludeLoader edge cases for coverage."""

    def test_include_without_hasattr_name(self, temp_dir: Path):
        """Test include constructor without stream.name attribute."""
        included = temp_dir / "included.yaml"
        included.write_text("value: 42", encoding="utf-8")

        main = temp_dir / "main.yaml"
        main_content = f"test: !include {included}"
        main.write_text(main_content, encoding="utf-8")

        # Read with string stream that doesn't have name attribute
        with open(main, encoding="utf-8") as f:
            content = f.read()

        # Create a stream without name attribute
        from io import StringIO

        stream = StringIO(content)
        loader = IncludeLoader(stream)

        # Should use cwd as root_dir when stream has no name
        assert hasattr(loader, "root_dir")
        assert loader.root_dir == Path.cwd()

    def test_include_absolute_path(self, temp_dir: Path):
        """Test include with absolute path."""
        included = temp_dir / "included.yaml"
        included.write_text("value: 42", encoding="utf-8")

        main = temp_dir / "main.yaml"
        # Use absolute path
        main_content = f"test: !include {str(included.resolve())}"
        main.write_text(main_content, encoding="utf-8")

        with open(main, encoding="utf-8") as f:
            data = yaml.load(f, Loader=IncludeLoader)

        assert data["test"]["value"] == 42


class TestPageNodeEdgeCases:
    """Test PageNode edge cases for coverage."""

    def test_relative_path_fallback_to_base(self):
        """Test relative path fallback when ValueError occurs."""
        config = {"title": "Test"}
        node = PageNode("test", config)

        # Create a scenario where relative_to fails for other_dir but works for base
        other_dir = Path("/completely/different/path")
        base_dir = Path("/tmp/generated")

        # This should trigger the fallback logic
        relative_path = node.get_relative_path_from(other_dir, base_dir)
        assert isinstance(relative_path, str)

    def test_relative_path_double_fallback(self):
        """Test relative path when both relative_to calls fail."""
        config = {"title": "Test"}
        node = PageNode("test", config)

        # Create scenario where both fallbacks are triggered
        other_dir = Path("/other/path")
        base_dir = Path("/base/path")

        # Mock to raise ValueError for both relative_to calls
        with patch.object(Path, "relative_to", side_effect=ValueError("test")):
            relative_path = node.get_relative_path_from(other_dir, base_dir)
            assert isinstance(relative_path, str)


class TestGeneratorEdgeCases:
    """Test IntroligoGenerator edge cases for coverage."""

    def test_default_template_from_file(self, sample_yaml_config: Path, temp_dir: Path):
        """Test loading default template from file when it exists."""
        output_dir = temp_dir / "output"

        # Create the templates directory in introligo package
        from introligo import __main__ as introligo_module

        module_path = Path(introligo_module.__file__).parent
        templates_dir = module_path / "templates"
        templates_dir.mkdir(exist_ok=True)

        template_file = templates_dir / "default.jinja2"
        template_file.write_text("{{ title }}\n{{ '=' * 10 }}", encoding="utf-8")

        try:
            generator = IntroligoGenerator(sample_yaml_config, output_dir)
            template_content = generator.get_default_template()

            # Should read from file
            assert template_content == "{{ title }}\n{{ '=' * 10 }}"
        finally:
            # Clean up
            if template_file.exists():
                template_file.unlink()
            if templates_dir.exists() and not any(templates_dir.iterdir()):
                templates_dir.rmdir()

    def test_markdown_read_error(self, temp_dir: Path):
        """Test error handling when markdown file read fails."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        # Create the markdown file but make it fail on read
        md_file = temp_dir / "test.md"
        md_file.write_text("content", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        # Mock read_text to raise exception after exists check
        original_exists = Path.exists

        def mock_exists(self):
            if "test.md" in str(self):
                return True
            return original_exists(self)

        with ExitStack() as stack:
            stack.enter_context(patch.object(Path, "exists", mock_exists))
            stack.enter_context(patch.object(Path, "read_text", side_effect=OSError("Read error")))
            exc_info = stack.enter_context(pytest.raises(IntroligoError))
            generator.include_markdown_file("test.md")

        assert "Error reading markdown file" in str(exc_info.value)

    def test_markdown_warning_on_missing(self, temp_dir: Path):
        """Test warning when markdown include is missing."""
        md_file = temp_dir / "test.md"
        config_file = temp_dir / "config.yaml"
        config_content = f"""
modules:
  test:
    title: "Test"
    markdown_includes: "{md_file.name}"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        # This should log a warning but not fail
        node = generator.page_tree[0]
        with patch("introligo.generator.logger.warning") as mock_warning:
            generator.generate_rst_content(node, template)
            mock_warning.assert_called()

    def test_markdown_includes_as_string(self, markdown_file: Path, temp_dir: Path):
        """Test markdown_includes as a single string."""
        config_file = temp_dir / "config.yaml"
        config_content = f"""
modules:
  test:
    title: "Test"
    markdown_includes: "{markdown_file.name}"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        # Should include markdown content
        assert "Version 1.0.0" in content

    def test_generate_with_doxygen_files_conversion(self, temp_dir: Path):
        """Test doxygen_file to doxygen_files conversion."""
        config_file = temp_dir / "config.yaml"
        config_content = """
doxygen:
  xml_path: "xml"
  project_name: "test"

modules:
  test:
    title: "Test"
    language: cpp
    doxygen_file: "test.h"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        # Should convert single doxygen_file to list
        assert "test.h" in content

    def test_custom_sections_in_index(self, temp_dir: Path):
        """Test custom sections in index generation."""
        config_file = temp_dir / "config.yaml"
        config_content = """
index:
  title: "Test Docs"
  custom_sections:
    - title: "Additional Info"
      content: "Some additional content"

modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()
        generator.build_page_tree()

        index = generator.generate_index(generator.page_tree)

        assert "Additional Info" in index
        assert "Some additional content" in index


class TestMainEntryPoint:
    """Test main entry point edge cases."""

    def test_main_when_called_directly(self, sample_yaml_config: Path, temp_dir: Path):
        """Test the if __name__ == '__main__' block."""
        import sys
        from unittest.mock import patch

        output_dir = temp_dir / "output"
        test_args = ["introligo", str(sample_yaml_config), "-o", str(output_dir)]

        # Simulate running as main module
        with patch.object(sys, "argv", test_args):
            # Import and run main
            from introligo.__main__ import main

            main()

        assert output_dir.exists()


class TestIntroligoErrorCoverage:
    """Additional error coverage tests."""

    def test_error_raised_with_context(self):
        """Test raising IntroligoError with context in actual code path."""
        from io import StringIO

        import yaml

        from introligo.yaml_loader import include_constructor

        # Create a mock loader
        stream = StringIO("test: value")
        loader = IncludeLoader(stream)

        # Create a node that will cause file not found
        node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value="nonexistent.yaml")

        with pytest.raises(IntroligoError) as exc_info:
            include_constructor(loader, node)

        assert "Include file not found" in str(exc_info.value)


class TestStrictModeErrors:
    """Test strict mode error handling."""

    def test_strict_mode_with_error(self, temp_dir: Path):
        """Test strict mode raises error on generation failure."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir, strict=True)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        # Mock to cause error in strict mode
        with patch.object(generator, "generate_rst_content", side_effect=Exception("Test error")):
            with pytest.raises(IntroligoError) as exc_info:
                generator.generate_all_nodes(generator.page_tree, template, strict=True)

            assert "Strict mode" in str(exc_info.value)

    def test_non_strict_mode_continues_on_error(self, temp_dir: Path):
        """Test non-strict mode logs error but continues."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test1:
    title: "Test 1"
  test2:
    title: "Test 2"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir, strict=False)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        # Mock to cause error for first node only
        call_count = [0]

        def mock_generate(node, template):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Test error")
            return f"{node.title}\n====="

        with ExitStack() as stack:
            stack.enter_context(
                patch.object(generator, "generate_rst_content", side_effect=mock_generate)
            )
            mock_error = stack.enter_context(patch("introligo.generator.logger.error"))
            result = generator.generate_all_nodes(generator.page_tree, template, strict=False)

            # Should log error but continue
            mock_error.assert_called()
            # Should have generated for second node (or partial result)
            assert isinstance(result, dict)


class TestComplexMarkdown:
    """Test complex markdown conversion scenarios."""

    def test_markdown_with_all_features(self, temp_dir: Path):
        """Test markdown with various features."""
        md_content = """# Changelog

## Version 2.0

### New Features

```python
def new_feature():
    return True
```

#### Subsection

Some text here.

Regular paragraph.
"""
        md_file = temp_dir / "complex.md"
        md_file.write_text(md_content, encoding="utf-8")

        config_file = temp_dir / "config.yaml"
        config_content = f"""
modules:
  test:
    title: "Test"
    markdown_includes: "{md_file.name}"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_markdown_file(md_file.name)

        # Should have proper RST formatting
        assert "Version 2.0" in content
        assert ".. code-block:: python" in content
        assert "Subsection" in content
