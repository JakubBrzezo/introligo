"""Tests for Sphinx configuration and palette features."""

from pathlib import Path

import pytest

from introligo.__main__ import IntroligoError, IntroligoGenerator


class TestPaletteFunctions:
    """Test palette loading and color resolution."""

    def test_load_palette_builtin(self, sample_yaml_config: Path, temp_dir: Path):
        """Test loading a built-in palette."""
        # Create config with palette reference
        config_content = """
index:
  title: "Test"
  description: "Test"
generate_index: true

sphinx:
  project: "Test"
  author: "Test"
  palette: "celin"
  html_theme: "furo"

modules:
  test:
    title: "Test"
    description: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        # Palette should be loaded
        assert generator.palette_data is not None
        assert "colors" in generator.palette_data or "light_mode" in generator.palette_data

    def test_load_palette_not_found(self, sample_yaml_config: Path, temp_dir: Path):
        """Test error when palette is not found."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  palette: "nonexistent_palette"
  html_theme: "furo"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        # Should raise IntroligoError
        with pytest.raises(IntroligoError, match="Palette not found"):
            generator.load_sphinx_config()

    def test_load_palette_inline(self, sample_yaml_config: Path, temp_dir: Path):
        """Test loading an inline palette definition."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"
  palette:
    name: "Inline Test"
    colors:
      primary:
        1: "#FF0000"
        2: "#00FF00"
    light_mode:
      color-brand-primary: "{primary.1}"
    dark_mode:
      color-brand-primary: "{primary.2}"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        # Inline palette should be loaded
        assert generator.palette_data is not None
        assert generator.palette_data["name"] == "Inline Test"

    def test_resolve_color_references(self, sample_yaml_config: Path, temp_dir: Path):
        """Test color reference resolution."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("")

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )

        palette_colors = {
            "primary": {
                "1": "#FF0000",
                "2": "#00FF00",
                "3": "#0000FF",
            },
            "secondary": {
                "1": "#FFFF00",
            },
        }

        theme_mapping = {
            "color-brand-primary": "{primary.1}",
            "color-brand-secondary": "{secondary.1}",
            "color-link": "#123456",  # Direct color
            "color-invalid": "{nonexistent.1}",  # Invalid reference
            "color-bad-format": "{primary}",  # Bad format
        }

        resolved = generator.resolve_color_references(palette_colors, theme_mapping)

        assert resolved["color-brand-primary"] == "#FF0000"
        assert resolved["color-brand-secondary"] == "#FFFF00"
        assert resolved["color-link"] == "#123456"
        # Invalid references should keep original value
        assert resolved["color-invalid"] == "{nonexistent.1}"
        assert resolved["color-bad-format"] == "{primary}"

    def test_flatten_palette_colors(self, sample_yaml_config: Path, temp_dir: Path):
        """Test flattening of nested palette colors."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("")

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )

        palette_colors = {
            "primary": {
                "1": "#FF0000",
                "2": "#00FF00",
            },
            "secondary": {
                "1": "#0000FF",
            },
        }

        flattened = generator.flatten_palette_colors(palette_colors)

        assert flattened["primary-1"] == "#FF0000"
        assert flattened["primary-2"] == "#00FF00"
        assert flattened["secondary-1"] == "#0000FF"


class TestLanguageDetection:
    """Test project language detection."""

    def test_detect_python_language(self, temp_dir: Path):
        """Test detection of Python language from module field."""
        config_content = """
modules:
  test:
    title: "Test"
    module: "mypackage.mymodule"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "python" in languages

    def test_detect_c_language(self, temp_dir: Path):
        """Test detection of C language from doxygen fields."""
        config_content = """
modules:
  test:
    title: "Test"
    doxygen_file: "test.h"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "c" in languages

    def test_detect_explicit_language(self, temp_dir: Path):
        """Test detection of explicitly specified language."""
        config_content = """
modules:
  test:
    title: "Test"
    language: "cpp"
    doxygen_class: "MyClass"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "cpp" in languages
        assert "c" not in languages  # Should not add default C for doxygen

    def test_detect_default_language(self, temp_dir: Path):
        """Test default Python language when no language detected."""
        config_content = """
modules:
  test:
    title: "Test"
    description: "Just a description"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "python" in languages


class TestExtensionAutoConfiguration:
    """Test automatic Sphinx extension configuration."""

    def test_auto_add_python_extensions(self, temp_dir: Path):
        """Test automatic addition of Python extensions."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  extensions: []

modules:
  test:
    title: "Test"
    module: "mypackage"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        extensions = generator.sphinx_config["extensions"]
        assert "sphinx.ext.autodoc" in extensions
        assert "sphinx.ext.napoleon" in extensions
        assert "sphinx.ext.viewcode" in extensions

    def test_auto_add_breathe_extension(self, temp_dir: Path):
        """Test automatic addition of Breathe extension for C/C++."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  extensions: []

modules:
  test:
    title: "Test"
    language: "c"
    doxygen_file: "test.h"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        extensions = generator.sphinx_config["extensions"]
        assert "breathe" in extensions

    def test_auto_add_mathjax_extension(self, temp_dir: Path):
        """Test automatic addition of MathJax extension for LaTeX."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  extensions: []

modules:
  test:
    title: "Test"
    latex_includes: "equations.tex"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        extensions = generator.sphinx_config["extensions"]
        assert "sphinx.ext.mathjax" in extensions

    def test_preserve_existing_extensions(self, temp_dir: Path):
        """Test that existing extensions are preserved."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  extensions:
    - "sphinx.ext.intersphinx"
    - "sphinx.ext.todo"

modules:
  test:
    title: "Test"
    module: "mypackage"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        extensions = generator.sphinx_config["extensions"]
        assert "sphinx.ext.intersphinx" in extensions
        assert "sphinx.ext.todo" in extensions
        assert "sphinx.ext.autodoc" in extensions  # Auto-added


class TestSphinxConfigGeneration:
    """Test Sphinx configuration generation."""

    def test_generate_conf_py_basic(self, temp_dir: Path):
        """Test basic conf.py generation."""
        config_content = """
sphinx:
  project: "Test Project"
  author: "Test Author"
  html_theme: "furo"
  extensions:
    - "sphinx.ext.autodoc"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        conf_py = generator.generate_conf_py()

        assert conf_py is not None
        assert "Test Project" in conf_py
        assert "Test Author" in conf_py
        assert "furo" in conf_py
        assert "AUTO-GENERATED" in conf_py

    def test_generate_conf_py_with_palette(self, temp_dir: Path):
        """Test conf.py generation with color palette."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"
  palette: "celin"
  html_theme_options:
    sidebar_hide_name: false

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        conf_py = generator.generate_conf_py()

        assert conf_py is not None
        assert "light_css_variables" in conf_py
        assert "dark_css_variables" in conf_py

    def test_generate_conf_py_with_breathe(self, temp_dir: Path):
        """Test conf.py generation with Breathe configuration."""
        config_content = """
doxygen:
  xml_path: "output/xml"
  project_name: "myproject"

sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"

modules:
  test:
    title: "Test"
    doxygen_file: "test.h"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        conf_py = generator.generate_conf_py()

        assert conf_py is not None
        assert "generated.breathe_config" in conf_py

    def test_generate_conf_py_no_sphinx_config(self, temp_dir: Path):
        """Test that no conf.py is generated without sphinx config."""
        config_content = """
modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        conf_py = generator.generate_conf_py()

        assert conf_py is None


class TestLatexErrorHandling:
    """Test LaTeX error handling."""

    def test_latex_include_file_not_found(self, temp_dir: Path):
        """Test error handling when LaTeX file is not found."""
        config_content = """
modules:
  test:
    title: "Test"
    latex_includes: "nonexistent.tex"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        # Should raise IntroligoError
        with pytest.raises(IntroligoError, match="LaTeX file not found"):
            generator.include_latex_file("nonexistent.tex")

    def test_latex_include_read_error(self, temp_dir: Path):
        """Test error handling when LaTeX file cannot be read."""
        # Create a file that exists but is not readable (simulate)
        latex_file = temp_dir / "equations.tex"
        latex_file.write_text("E = mc^2")

        config_content = """
modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        # Test with path that exists
        content = generator.include_latex_file(str(latex_file))
        assert "E = mc^2" in content
        assert ".. math::" in content

    def test_latex_single_string_conversion(self, temp_dir: Path):
        """Test conversion of single LaTeX string (not list)."""
        latex_file = temp_dir / "equations.tex"
        latex_file.write_text("a^2 + b^2 = c^2")

        config_content = f"""
modules:
  test:
    title: "Test"
    latex_includes: "{latex_file}"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        # Generate RST content
        node = generator.page_tree[0]
        rst_content = generator.generate_rst_content(node, template)

        assert "a^2 + b^2 = c^2" in rst_content
        assert ".. math::" in rst_content

    def test_latex_error_in_generation_loop(self, temp_dir: Path, caplog):
        """Test LaTeX error handling during RST generation."""
        config_content = """
modules:
  test:
    title: "Test"
    description: "Test"
    latex_includes:
      - "nonexistent1.tex"
      - "nonexistent2.tex"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        # Generate RST content - should log warnings but not fail
        import logging

        with caplog.at_level(logging.WARNING):
            node = generator.page_tree[0]
            rst_content = generator.generate_rst_content(node, template)

        # Should have warning messages
        assert any("LaTeX file not found" in record.message for record in caplog.records)
        # RST content should still be generated
        assert "Test" in rst_content


class TestPaletteEdgeCases:
    """Test edge cases in palette handling."""

    def test_palette_without_colors(self, temp_dir: Path):
        """Test palette with only theme mappings (no colors section)."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"
  palette:
    name: "Simple"
    light_mode:
      color-brand-primary: "#FF0000"
    dark_mode:
      color-brand-primary: "#00FF00"
  html_theme_options:
    sidebar_hide_name: false

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        conf_py = generator.generate_conf_py()

        assert conf_py is not None
        assert "#FF0000" in conf_py
        assert "#00FF00" in conf_py

    def test_palette_color_resolution_warnings(self, temp_dir: Path, caplog):
        """Test color resolution with invalid shade."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("")

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )

        palette_colors = {
            "primary": {
                "1": "#FF0000",
            },
        }

        theme_mapping = {
            "color-brand-primary": "{primary.99}",  # Invalid shade
        }

        import logging

        with caplog.at_level(logging.WARNING):
            resolved = generator.resolve_color_references(palette_colors, theme_mapping)

        # Should have warning about shade not found
        assert any("not found" in record.message for record in caplog.records)
        # Should keep original value
        assert resolved["color-brand-primary"] == "{primary.99}"

    def test_palette_relative_to_config(self, temp_dir: Path):
        """Test loading palette file relative to config file."""
        # Create a palette file
        palette_dir = temp_dir / "palettes"
        palette_dir.mkdir()
        palette_file = palette_dir / "custom.yaml"
        palette_content = """
name: "Custom Palette"
colors:
  test:
    1: "#123456"
light_mode:
  color-brand-primary: "{test.1}"
dark_mode:
  color-brand-primary: "{test.1}"
"""
        palette_file.write_text(palette_content)

        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"
  palette: "palettes/custom.yaml"
  html_theme_options:
    sidebar_hide_name: false

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()
        generator.load_sphinx_config()

        # Palette should be loaded
        assert generator.palette_data is not None
        assert generator.palette_data["name"] == "Custom Palette"


class TestMainFunctionCoverage:
    """Test main function for coverage."""

    def test_main_dry_run_with_conf_py(self, temp_dir: Path, monkeypatch, caplog):
        """Test main function in dry-run mode with conf.py generation."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        # Mock command line arguments
        import logging
        import sys

        monkeypatch.setattr(
            sys,
            "argv",
            ["introligo", str(config_file), "-o", str(temp_dir), "--dry-run", "-v"],
        )

        # Import and run main
        from introligo.__main__ import main

        with caplog.at_level(logging.INFO):
            main()

        # Check that conf.py dry-run message was logged
        assert any("Would generate conf.py" in record.message for record in caplog.records)

    def test_main_with_actual_conf_py_generation(self, temp_dir: Path, monkeypatch):
        """Test main function with actual conf.py generation (not dry-run)."""
        config_content = """
sphinx:
  project: "Test"
  author: "Test"
  html_theme: "furo"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        # Mock command line arguments (no --dry-run)
        import sys

        monkeypatch.setattr(
            sys,
            "argv",
            ["introligo", str(config_file), "-o", str(temp_dir), "-v"],
        )

        # Import and run main
        from introligo.__main__ import main

        main()

        # Check that conf.py was actually generated
        conf_py_path = temp_dir / "conf.py"
        assert conf_py_path.exists()
        content = conf_py_path.read_text()
        assert "AUTO-GENERATED" in content


class TestUsageExamplesProcessing:
    """Test usage examples processing with different input types."""

    def test_process_usage_examples_string_in_list(self, temp_dir: Path):
        """Test processing of string example in list."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("")

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )

        examples = ["print('hello')", "print('world')"]
        processed = generator.process_usage_examples(examples)

        assert len(processed) == 2
        assert processed[0]["code"] == "print('hello')"
        assert processed[0]["language"] == "python"
        assert processed[0]["title"] == "Example"

    def test_process_usage_examples_single_dict(self, temp_dir: Path):
        """Test processing of single dict example."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("")

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )

        examples = {
            "title": "Test Example",
            "description": "Test description",
            "language": "bash",
            "code": "echo hello",
        }
        processed = generator.process_usage_examples(examples)

        assert len(processed) == 1
        assert processed[0]["title"] == "Test Example"
        assert processed[0]["language"] == "bash"
        assert processed[0]["code"] == "echo hello"

    def test_process_usage_examples_single_string(self, temp_dir: Path):
        """Test processing of single string example."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("")

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )

        examples = "print('single example')"
        processed = generator.process_usage_examples(examples)

        assert len(processed) == 1
        assert processed[0]["code"] == "print('single example')"
        assert processed[0]["language"] == "python"


class TestBreatheConfig:
    """Test Breathe configuration generation."""

    def test_generate_breathe_config_absolute_path(self, temp_dir: Path):
        """Test Breathe config generation with absolute XML path."""
        xml_dir = temp_dir / "output" / "xml"
        xml_dir.mkdir(parents=True)

        config_content = f"""
doxygen:
  xml_path: "{xml_dir}"
  project_name: "myproject"

modules:
  test:
    title: "Test"
    doxygen_file: "test.h"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        breathe_config = generator.generate_breathe_config()

        assert breathe_config is not None
        assert str(xml_dir) in breathe_config
        assert "myproject" in breathe_config

    def test_load_palette_file_read_error(self, temp_dir: Path):
        """Test error handling when palette file cannot be read (lines 1633-1634)."""
        # Create a directory instead of a file to cause read error
        palette_dir = temp_dir / "bad_palette.yaml"
        palette_dir.mkdir()

        config_content = f"""
sphinx:
  theme:
    name: "furo"
    palette: "{palette_dir}"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        with pytest.raises(IntroligoError, match="Error loading palette"):
            generator.load_palette(str(palette_dir))

    def test_generate_conf_py_missing_template(self, temp_dir: Path):
        """Test conf.py generation when template is missing (lines 1830-1831)."""
        import shutil

        import introligo.__main__

        config_content = """
sphinx:
  project: "Test Project"
  author: "Test Author"

modules:
  test:
    title: "Test"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir,
        )
        generator.load_config()

        # Physically move the template file to make it not found
        from pathlib import Path as PathlibPath

        template_path = (
            PathlibPath(introligo.__main__.__file__).parent / "templates" / "conf.py.jinja2"
        )
        backup_path = template_path.parent / ".conf.py.jinja2.backup"

        try:
            # Move template file away
            if template_path.exists():
                shutil.move(str(template_path), str(backup_path))

            # Should return None and log warning when template not found
            result = generator.generate_conf_py()
            assert result is None
        finally:
            # Restore template file
            if backup_path.exists():
                shutil.move(str(backup_path), str(template_path))
