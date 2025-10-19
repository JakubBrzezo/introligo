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


@pytest.fixture
def latex_file(temp_dir: Path) -> Path:
    """Create a sample LaTeX file."""
    latex_file = temp_dir / "equations.tex"
    latex_content = r"""E = mc^2

\frac{d}{dx} \int_a^x f(t) dt = f(x)

\sum_{i=1}^{n} i = \frac{n(n+1)}{2}"""
    latex_file.write_text(latex_content, encoding="utf-8")
    return latex_file


@pytest.fixture
def latex_file_with_document(temp_dir: Path) -> Path:
    """Create a LaTeX file with document wrapper."""
    latex_file = temp_dir / "document.tex"
    latex_content = r"""\documentclass{article}
\usepackage{amsmath}

\begin{document}

E = mc^2

\frac{d}{dx} \int_a^x f(t) dt = f(x)

\end{document}"""
    latex_file.write_text(latex_content, encoding="utf-8")
    return latex_file


@pytest.fixture
def config_with_latex(temp_dir: Path, latex_file: Path) -> Path:
    """Create configuration that includes LaTeX files."""
    config_file = temp_dir / "latex_config.yaml"
    config_content = f"""
modules:
  module_with_latex:
    title: "Module with LaTeX"
    description: "Module that includes LaTeX equations"
    latex_includes: "{latex_file.name}"
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


@pytest.fixture
def rst_file(temp_dir: Path) -> Path:
    """Create a sample RST file."""
    rst_file = temp_dir / "architecture.rst"
    rst_content = """Architecture Overview
=====================

System Components
-----------------

The system consists of the following components:

* Component A: Handles data processing
* Component B: Manages user interactions
* Component C: Provides storage layer

Code Example
~~~~~~~~~~~~

.. code-block:: python

   class SystemComponent:
       def __init__(self, name):
           self.name = name

       def process(self, data):
           return f"Processing {data}"
"""
    rst_file.write_text(rst_content, encoding="utf-8")
    return rst_file


@pytest.fixture
def text_file(temp_dir: Path) -> Path:
    """Create a sample text file."""
    txt_file = temp_dir / "notes.txt"
    txt_content = """Important Notes:

1. Remember to update configuration
2. Check compatibility with Python 3.8+
3. Run tests before deployment
4. Update documentation"""
    txt_file.write_text(txt_content, encoding="utf-8")
    return txt_file


@pytest.fixture
def config_with_rst(temp_dir: Path, rst_file: Path) -> Path:
    """Create configuration that includes RST files."""
    config_file = temp_dir / "rst_config.yaml"
    config_content = f"""
modules:
  module_with_rst:
    title: "Module with RST"
    description: "Module that includes RST documentation"
    rst_includes: "{rst_file.name}"
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


@pytest.fixture
def config_with_file_includes(
    temp_dir: Path, rst_file: Path, markdown_file: Path, latex_file: Path, text_file: Path
) -> Path:
    """Create configuration that uses file_includes with auto-detection."""
    config_file = temp_dir / "file_includes_config.yaml"
    config_content = f"""
modules:
  module_with_files:
    title: "Module with Multiple Files"
    description: "Module that includes multiple file types"
    file_includes:
      - "{rst_file.name}"
      - "{markdown_file.name}"
      - "{latex_file.name}"
      - "{text_file.name}"
"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file
