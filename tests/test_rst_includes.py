"""Comprehensive tests for RST file inclusion functionality."""

from pathlib import Path

import pytest

from introligo.__main__ import IntroligoError, IntroligoGenerator


class TestRSTIncludes:
    """Test cases for RST file inclusion."""

    def test_single_rst_include(self, config_with_rst: Path, temp_dir: Path):
        """Test including a single RST file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_with_rst, output_dir)

        # Test the include_rst_file method directly
        rst_file = temp_dir / "architecture.rst"
        content = generator.include_rst_file(rst_file.name)

        assert "Architecture Overview" in content
        assert "System Components" in content
        assert "Component A" in content
        assert ".. code-block:: python" in content

    def test_multiple_rst_includes(self, temp_dir: Path):
        """Test including multiple RST files."""
        # Create multiple RST files
        rst1 = temp_dir / "part1.rst"
        rst1.write_text(
            """Part One
========

This is the first part.
""",
            encoding="utf-8",
        )

        rst2 = temp_dir / "part2.rst"
        rst2.write_text(
            """Part Two
========

This is the second part.
""",
            encoding="utf-8",
        )

        # Create config with multiple includes
        config_file = temp_dir / "config.yaml"
        config_content = f"""
modules:
  multi_rst:
    title: "Multiple RST Includes"
    description: "Module with multiple RST files"
    rst_includes:
      - "{rst1.name}"
      - "{rst2.name}"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        # Process both files
        content1 = generator.include_rst_file(rst1.name)
        content2 = generator.include_rst_file(rst2.name)

        assert "Part One" in content1
        assert "first part" in content1
        assert "Part Two" in content2
        assert "second part" in content2

    def test_rst_with_complex_directives(self, temp_dir: Path):
        """Test RST file with complex directives."""
        rst_file = temp_dir / "complex.rst"
        rst_content = """Complex Documentation
=====================

.. note::

   This is a note directive.

.. warning::

   This is a warning directive.

.. code-block:: python
   :linenos:
   :emphasize-lines: 2,3

   def example():
       # This line is emphasized
       return True

.. list-table:: Features
   :header-rows: 1
   :widths: 30 70

   * - Feature
     - Description
   * - Feature A
     - Does something useful
   * - Feature B
     - Does something else

.. image:: /path/to/image.png
   :alt: Example image
   :width: 400px

.. seealso::

   :doc:`related_doc`
   `External Link <https://example.com>`_
"""
        rst_file.write_text(rst_content, encoding="utf-8")

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_rst_file(rst_file.name)

        # Verify all directives are preserved
        assert ".. note::" in content
        assert ".. warning::" in content
        assert ".. code-block:: python" in content
        assert ":linenos:" in content
        assert ":emphasize-lines:" in content
        assert ".. list-table::" in content
        assert ".. image::" in content
        assert ".. seealso::" in content

    def test_rst_include_missing_file(self, temp_dir: Path):
        """Test error handling when RST file doesn't exist."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.include_rst_file("nonexistent.rst")

        assert "RST file not found" in str(exc_info.value)

    def test_rst_include_with_subdirectory(self, temp_dir: Path):
        """Test including RST file from subdirectory."""
        # Create subdirectory with RST file
        subdir = temp_dir / "docs"
        subdir.mkdir()

        rst_file = subdir / "guide.rst"
        rst_file.write_text(
            """User Guide
==========

Welcome to the user guide.
""",
            encoding="utf-8",
        )

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_rst_file("docs/guide.rst")

        assert "User Guide" in content
        assert "Welcome to the user guide" in content

    def test_rst_include_with_unicode(self, temp_dir: Path):
        """Test RST file with Unicode characters."""
        rst_file = temp_dir / "unicode.rst"
        rst_content = """Documentation Internationale
============================

Exemples de caractères spéciaux:

- Français: café, naïve, Noël
- Deutsch: Müller, Größe, Äpfel
- Español: niño, mañana, señor
- 中文: 你好世界
- 日本語: こんにちは
- Emoji: 🚀 📝 ✨

.. code-block:: python

   # Unicode in code
   greeting = "Hello 世界! 🌍"
   print(greeting)
"""
        rst_file.write_text(rst_content, encoding="utf-8")

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_rst_file(rst_file.name)

        # Verify Unicode content is preserved
        assert "café" in content
        assert "Müller" in content
        assert "niño" in content
        assert "你好世界" in content
        assert "こんにちは" in content
        assert "🚀" in content

    def test_rst_include_empty_file(self, temp_dir: Path):
        """Test including an empty RST file."""
        rst_file = temp_dir / "empty.rst"
        rst_file.write_text("", encoding="utf-8")

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_rst_file(rst_file.name)

        assert content == ""

    def test_rst_include_with_whitespace_only(self, temp_dir: Path):
        """Test including RST file with only whitespace."""
        rst_file = temp_dir / "whitespace.rst"
        rst_file.write_text("   \n\n  \n  ", encoding="utf-8")

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_rst_file(rst_file.name)

        assert content.strip() == ""

    def test_generate_rst_with_rst_includes(self, temp_dir: Path):
        """Test full RST generation with RST includes."""
        # Create RST file to include
        rst_file = temp_dir / "technical.rst"
        rst_file.write_text(
            """Technical Details
=================

API Reference
-------------

.. code-block:: python

   class APIClient:
       def __init__(self, api_key: str):
           self.api_key = api_key

       def get_data(self):
           '''Retrieve data from the API.'''
           pass

Performance Notes
-----------------

.. tip::

   For best performance, enable caching.
""",
            encoding="utf-8",
        )

        # Create config
        config_file = temp_dir / "config.yaml"
        config_content = f"""
index:
  title: "Test Documentation"
  description: "Test RST includes"

generate_index: true

modules:
  technical_docs:
    title: "Technical Documentation"
    description: "Technical details and API reference"
    rst_includes: "{rst_file.name}"

    features:
      - "Comprehensive API"
      - "Performance optimized"

    notes: |
      .. note::

         This documentation is auto-generated.
"""
        config_file.write_text(config_content, encoding="utf-8")

        # Generate documentation
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        # Generate and write files
        generated_files = generator.generate_all()
        generator.write_files(generated_files)

        # Verify output structure was created
        assert output_dir.exists()

        # The file is named based on the title (technical_documentation.rst)
        output_file = output_dir / "generated" / "technical_documentation.rst"
        assert output_file.exists()

        # Read and verify content
        content = output_file.read_text(encoding="utf-8")

        # Should contain both YAML content and included RST
        assert "Technical Documentation" in content  # Title from YAML
        assert "Technical details and API reference" in content  # Description
        assert "Technical Details" in content  # From included RST
        assert "API Reference" in content  # From included RST
        assert "class APIClient:" in content  # From included RST
        assert "Comprehensive API" in content  # Features from YAML
        assert "Performance optimized" in content  # Features from YAML

    def test_rst_include_absolute_path_error(self, temp_dir: Path):
        """Test that absolute paths work correctly."""
        rst_file = temp_dir / "absolute.rst"
        rst_file.write_text(
            """Absolute Path Test
==================

This file is referenced by absolute path.
""",
            encoding="utf-8",
        )

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        # Use absolute path
        content = generator.include_rst_file(str(rst_file.resolve()))

        assert "Absolute Path Test" in content
        assert "referenced by absolute path" in content

    def test_rst_include_preserves_indentation(self, temp_dir: Path):
        """Test that indentation in RST is preserved."""
        rst_file = temp_dir / "indented.rst"
        rst_content = """Indentation Test
================

.. code-block:: python

   def function():
       if True:
           for i in range(10):
               if i % 2 == 0:
                   print(i)

Nested Lists
------------

1. First level

   * Second level

     * Third level
     * Third level item 2

   * Second level item 2

2. First level item 2
"""
        rst_file.write_text(rst_content, encoding="utf-8")

        config_file = temp_dir / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        content = generator.include_rst_file(rst_file.name)

        # Verify indentation is preserved
        assert "       if True:" in content
        assert "           for i in range(10):" in content
        assert "               if i % 2 == 0:" in content
        assert "                   print(i)" in content
        assert "   * Second level" in content
        assert "     * Third level" in content
