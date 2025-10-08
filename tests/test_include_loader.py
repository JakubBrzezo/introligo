"""Tests for IncludeLoader YAML loader class."""

from pathlib import Path

import pytest
import yaml

from introligo import IncludeLoader, IntroligoError


class TestIncludeLoader:
    """Test cases for IncludeLoader."""

    def test_load_simple_yaml(self, temp_dir: Path):
        """Test loading a simple YAML file."""
        yaml_file = temp_dir / "simple.yaml"
        yaml_file.write_text("key: value\nlist:\n  - item1\n  - item2", encoding="utf-8")

        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.load(f, Loader=IncludeLoader)

        assert data["key"] == "value"
        assert data["list"] == ["item1", "item2"]

    def test_load_with_include(self, sample_include_config: Path):
        """Test loading YAML with !include directive."""
        with open(sample_include_config, encoding="utf-8") as f:
            data = yaml.load(f, Loader=IncludeLoader)

        assert "modules" in data
        assert "included_module" in data["modules"]
        assert data["modules"]["included_module"]["title"] == "Included Module"
        assert "Feature 1" in data["modules"]["included_module"]["features"]

    def test_include_missing_file(self, temp_dir: Path):
        """Test that missing include file raises IntroligoError."""
        main_file = temp_dir / "main.yaml"
        main_file.write_text("modules:\n  test: !include missing.yaml", encoding="utf-8")

        with pytest.raises(IntroligoError) as exc_info:
            with open(main_file, encoding="utf-8") as f:
                yaml.load(f, Loader=IncludeLoader)

        assert "Include file not found" in str(exc_info.value)

    def test_include_invalid_yaml(self, temp_dir: Path):
        """Test that invalid YAML in included file raises IntroligoError."""
        included_file = temp_dir / "invalid.yaml"
        included_file.write_text("invalid: yaml: syntax: error:", encoding="utf-8")

        main_file = temp_dir / "main.yaml"
        main_file.write_text("modules:\n  test: !include invalid.yaml", encoding="utf-8")

        with pytest.raises(IntroligoError) as exc_info:
            with open(main_file, encoding="utf-8") as f:
                yaml.load(f, Loader=IncludeLoader)

        assert "Invalid YAML" in str(exc_info.value)

    def test_nested_includes(self, temp_dir: Path):
        """Test nested !include directives."""
        # Create deeply nested file
        level2 = temp_dir / "level2.yaml"
        level2.write_text("title: Level 2\nvalue: deep", encoding="utf-8")

        # Create first level include
        level1 = temp_dir / "level1.yaml"
        level1.write_text(f"nested: !include {level2.name}", encoding="utf-8")

        # Create main file
        main = temp_dir / "main.yaml"
        main.write_text(f"modules:\n  test: !include {level1.name}", encoding="utf-8")

        with open(main, encoding="utf-8") as f:
            data = yaml.load(f, Loader=IncludeLoader)

        assert data["modules"]["test"]["nested"]["title"] == "Level 2"
        assert data["modules"]["test"]["nested"]["value"] == "deep"

    def test_include_with_subdirectory(self, temp_dir: Path):
        """Test !include with files in subdirectories."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        included = subdir / "config.yaml"
        included.write_text("title: Subdir Config", encoding="utf-8")

        main = temp_dir / "main.yaml"
        main.write_text(f"modules:\n  test: !include subdir/{included.name}", encoding="utf-8")

        with open(main, encoding="utf-8") as f:
            data = yaml.load(f, Loader=IncludeLoader)

        assert data["modules"]["test"]["title"] == "Subdir Config"

    def test_loader_tracks_file_path(self, temp_dir: Path):
        """Test that IncludeLoader tracks current file path."""
        yaml_file = temp_dir / "test.yaml"
        yaml_file.write_text("key: value", encoding="utf-8")

        with open(yaml_file, encoding="utf-8") as f:
            loader = IncludeLoader(f)
            assert hasattr(loader, "_root_dir")
            assert loader._root_dir == temp_dir

    def test_include_with_relative_path_fallback(self, temp_dir: Path):
        """Test include with path resolution when loader has no _root_dir attribute."""
        # Create included file
        included = temp_dir / "included.yaml"
        included.write_text("value: 42", encoding="utf-8")

        # Create main file with include
        temp_dir / "main.yaml"

        # Write and read without using file handle with name attribute
        from io import StringIO

        import yaml

        # Simulate include_constructor being called without _root_dir
        from introligo.__main__ import include_constructor

        stream = StringIO("test: value")
        loader = IncludeLoader(stream)

        # Manually remove _root_dir to test fallback
        delattr(loader, "_root_dir")

        # Create a scalar node with absolute path
        node = yaml.ScalarNode(tag="tag:yaml.org,2002:str", value=str(included.resolve()))

        # This should use Path(include_path).resolve() as fallback
        result = include_constructor(loader, node)
        assert result["value"] == 42

    def test_include_error_handling(self, temp_dir: Path):
        """Test error handling when included file has issues."""
        included = temp_dir / "error.yaml"
        # Create a file that will cause an error when reading
        included.write_text("test: value", encoding="utf-8")
        included.chmod(0o000)  # Make it unreadable

        main = temp_dir / "main.yaml"
        main.write_text(f"modules:\n  test: !include {included.name}", encoding="utf-8")

        try:
            with pytest.raises(IntroligoError) as exc_info:
                with open(main, encoding="utf-8") as f:
                    yaml.load(f, Loader=IncludeLoader)

            assert "Error loading included file" in str(exc_info.value)
        finally:
            # Restore permissions for cleanup
            included.chmod(0o644)
