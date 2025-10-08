"""Pytest configuration and fixtures for introligo tests."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_yaml_config(temp_dir: Path) -> Path:
    """Create a sample YAML configuration file."""
    config_file = temp_dir / "config.yaml"
    config_content = """
modules:
  my_module:
    title: "My Module"
    description: "A sample module"
    module: my_package.my_module
  parent_module:
    title: "Parent Module"
    description: "A parent module"
  child_module:
    title: "Child Module"
    description: "A child module"
    parent: parent_module
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


@pytest.fixture
def sample_include_config(temp_dir: Path) -> Path:
    """Create configuration files with !include directive."""
    # Create included file
    included_file = temp_dir / "included.yaml"
    included_content = """
title: "Included Module"
description: "This is included"
features:
  - Feature 1
  - Feature 2
"""
    included_file.write_text(included_content, encoding="utf-8")

    # Create main config
    main_config = temp_dir / "main.yaml"
    main_content = """
modules:
  included_module: !include included.yaml
  regular_module:
    title: "Regular Module"
    description: "A regular module"
"""
    main_config.write_text(main_content, encoding="utf-8")
    return main_config


@pytest.fixture
def doxygen_config(temp_dir: Path) -> Path:
    """Create a configuration with Doxygen settings."""
    config_file = temp_dir / "doxygen_config.yaml"
    config_content = """
doxygen:
  xml_path: "doxygen/xml"
  project_name: "test_project"

modules:
  cpp_module:
    title: "C++ Module"
    language: cpp
    doxygen_file: test.h
  c_module:
    title: "C Module"
    language: c
    doxygen_files:
      - test1.c
      - test2.h
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


@pytest.fixture
def markdown_file(temp_dir: Path) -> Path:
    """Create a sample markdown file."""
    md_file = temp_dir / "README.md"
    md_content = """# Changelog

## Version 1.0.0

### Features
- Feature 1
- Feature 2

### Code Example

```python
def hello():
    print("Hello, World!")
```

### Notes
Some important notes here.
"""
    md_file.write_text(md_content, encoding="utf-8")
    return md_file


@pytest.fixture
def config_with_markdown(temp_dir: Path, markdown_file: Path) -> Path:
    """Create configuration that includes markdown files."""
    config_file = temp_dir / "md_config.yaml"
    config_content = f"""
modules:
  module_with_md:
    title: "Module with Markdown"
    description: "Module that includes markdown"
    markdown_includes: "{markdown_file.name}"
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file
