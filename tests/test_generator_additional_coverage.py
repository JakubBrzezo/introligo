"""Additional tests to improve generator.py coverage."""

import tempfile
from pathlib import Path

import pytest

from introligo.generator import IntroligoGenerator


class TestGeneratorDiagramIncludes:
    """Tests for diagram inclusion features."""

    def test_include_mermaid_diagram(self, temp_dir):
        """Test including Mermaid diagram."""
        # Create a Mermaid diagram file
        mermaid_file = temp_dir / "flow.mmd"
        mermaid_file.write_text("""graph TD
    A[Start] --> B[Process]
    B --> C[End]
""")

        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
    diagram_includes:
      - path: flow.mmd
        title: Flow Diagram
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_include_graphviz_diagram(self, temp_dir):
        """Test including GraphViz diagram."""
        # Create a GraphViz diagram file
        graphviz_file = temp_dir / "graph.dot"
        graphviz_file.write_text("""digraph G {
    A -> B;
    B -> C;
}
""")

        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
    diagram_includes:
      - path: graph.dot
        title: Graph Diagram
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_include_unknown_diagram_type(self, temp_dir):
        """Test including diagram with unknown extension."""
        # Create a file with unknown extension
        unknown_file = temp_dir / "diagram.xyz"
        unknown_file.write_text("Unknown diagram content")

        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
    diagram_includes:
      - path: diagram.xyz
        title: Unknown Diagram
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_include_diagram_with_error(self, temp_dir):
        """Test error handling when including non-existent diagram."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
    diagram_includes:
      - path: nonexistent.puml
        title: Missing Diagram
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        # Should handle error gracefully
        assert result is not None

    def test_include_diagram_as_string(self, temp_dir):
        """Test including diagram specified as string."""
        # Create a diagram file
        diagram_file = temp_dir / "simple.puml"
        diagram_file.write_text("@startuml\nA -> B\n@enduml")

        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
    diagram_includes:
      - simple.puml
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None


class TestGeneratorGoDocFeatures:
    """Tests for Go documentation features."""

    def test_generate_with_manual_godoc(self, temp_dir):
        """Test generation with manual Go documentation."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  go_api:
    title: Go API
    language: go
    manual_godoc: |
      This is manual Go documentation.

      Package main provides the entry point.
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_generate_with_godoc_path(self, temp_dir):
        """Test generation with godoc_path specified."""
        # Create a Go source directory
        go_dir = temp_dir / "src"
        go_dir.mkdir()

        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  go_api:
    title: Go API
    language: go
    godoc_path: src
    godoc_package: main
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_generate_with_multiple_godoc_packages(self, temp_dir):
        """Test generation with multiple Go packages."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  go_api:
    title: Go API
    language: go
    godoc_packages:
      - main
      - utils
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None


class TestGeneratorJavaDocFeatures:
    """Tests for Java documentation features."""

    def test_generate_with_manual_javadoc(self, temp_dir):
        """Test generation with manual Java documentation."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  java_api:
    title: Java API
    language: java
    java_manual_content: |
      This is manual Java documentation.

      **class User**

      Represents a user in the system.
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None


class TestGeneratorRustDocFeatures:
    """Tests for Rust documentation features."""

    def test_generate_with_manual_rustdoc(self, temp_dir):
        """Test generation with manual Rust documentation."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  rust_api:
    title: Rust API
    language: rust
    manual_rustdoc: |
      This is manual Rust documentation.

      ## Crate: my_crate

      A sample Rust crate.
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None


class TestGeneratorPaletteHandling:
    """Tests for color palette handling."""

    def test_flatten_palette_with_nested_dict(self, temp_dir):
        """Test palette flattening with nested dictionary."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )

        palette = {
            "primary": {"light": "#aabbcc", "main": "#112233", "dark": "#001122"},
            "secondary": {"light": "#ddeeff", "main": "#445566"},
        }

        result = generator.flatten_palette_colors(palette)

        assert "primary-light" in result
        assert "primary-main" in result
        assert "primary-dark" in result
        assert "secondary-light" in result
        assert "secondary-main" in result
        assert result["primary-light"] == "#aabbcc"

    def test_flatten_palette_with_simple_colors(self, temp_dir):
        """Test palette flattening with simple color values."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  test_module:
    title: Test Module
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )

        palette = {"background": "#ffffff", "foreground": "#000000", "accent": {"main": "#ff0000"}}

        result = generator.flatten_palette_colors(palette)

        # Simple colors are not flattened
        assert "accent-main" in result
        assert result["accent-main"] == "#ff0000"


class TestGeneratorLanguageDetection:
    """Tests for language detection features."""

    def test_detect_python_from_module_field(self, temp_dir):
        """Test detecting Python from module field."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  my_package:
    title: My Package
    module: my_package.module_name
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )

        languages = generator.detect_project_languages()

        assert "python" in languages


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
