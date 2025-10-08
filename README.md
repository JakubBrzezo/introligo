# Introligo - Documentation Generator

[![Tests](https://github.com/JakubBrzezo/introligo/actions/workflows/tests.yml/badge.svg)](https://github.com/JakubBrzezo/introligo/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/JakubBrzezo/introligo/branch/main/graph/badge.svg)](https://codecov.io/gh/JakubBrzezo/introligo)

YAML to reStructuredText documentation generator for Sphinx with hierarchical page organization and rich content support.

> **Note**: Introligo is one of the open-source components of the Celin Project, available for free use in any project.

## Overview

Introligo streamlines the documentation process by converting structured YAML configurations into properly formatted reStructuredText files for Sphinx. It supports hierarchical page organization, automatic toctree generation, and rich content features including code examples, API documentation, and custom sections.

## Features

- 📝 **YAML to RST conversion** - Write documentation in simple YAML, generate complex RST
- 🌳 **Hierarchical organization** - Parent-child relationships for logical structure
- 🔄 **Automatic toctree generation** - Navigation built automatically from structure
- 📦 **Sphinx autodoc integration** - Seamless API documentation from Python modules
- 🔬 **Breathe/Doxygen support** - Document C/C++ code with single or multiple files
- 🎨 **Rich content support** - Features, examples, installation guides, and more
- 🏷️ **ASCII-safe naming** - Automatic slug generation for filesystem compatibility
- 📁 **File includes** - Modular configuration with `!include` directive
- 📝 **Markdown includes** - Include markdown files in your documentation
- 🎯 **Template customization** - Use Jinja2 templates for custom output formats
- 🚀 **Dry-run mode** - Preview changes before generating files

## Installation

```bash
# Install required packages
pip install PyYAML jinja2

# For building the generated docs
pip install sphinx sphinx_rtd_theme

# For C/C++ documentation support (optional)
pip install breathe
sudo apt-get install doxygen  # or brew install doxygen on macOS
```

## Quick Start

```bash
# Generate RST files in docs directory
python modules/introligo/introligo.py config.yaml -o docs

# Preview what would be generated (dry run)
python modules/introligo/introligo.py config.yaml -o docs --dry-run

# Use verbose output for debugging
python modules/introligo/introligo.py config.yaml -o docs -v
```

## Basic Configuration

```yaml
# config.yaml
index:
  title: "My Project Documentation"
  description: "Comprehensive documentation for my project"

generate_index: true

modules:
  utilities:
    title: "Utility Scripts"
    description: "Collection of utility scripts"

  my_tool:
    parent: "utilities"
    module: "myproject.tools.my_tool"
    title: "My Tool"
    description: "A useful tool for processing data"
    features:
      - "Fast processing"
      - "Easy to use"
      - "Well documented"
```

## C/C++ Documentation

```yaml
# Global Doxygen configuration
doxygen:
  xml_path: "../output/xml"
  project_name: "myproject"

modules:
  my_component:
    title: "My Component"
    language: c
    description: "Component description"
    doxygen_files:
      - mycomponent.h
      - mycomponent.c
```

## Including Markdown Files

```yaml
modules:
  my_module:
    title: "My Module"
    description: "Module with markdown documentation"
    module: "myproject.my_module"

    # Include markdown files (list or single file)
    markdown_includes:
      - "docs/user_guide.md"
      - "README.md"
```

Paths are resolved relative to the configuration file.

## Requirements

- Python 3.8 or higher
- PyYAML >= 6.0
- Jinja2 >= 3.0
- Sphinx >= 4.0 (for building documentation)
- Breathe >= 4.0 (optional, for C/C++ documentation)
- Doxygen (optional, for C/C++ documentation)

## Documentation

Introligo has comprehensive documentation built with Sphinx and the Furo theme, using the Celin color palette.

### Building the Documentation

**Quick Start - Using preview.py (Recommended):**

```bash
# Navigate to the docs directory
cd docs/

# Build and serve documentation (one command)
python preview.py
# Opens at http://localhost:8000

# Build only (no server)
python preview.py --no-serve

# Custom port
python preview.py --port 8080

# Skip Introligo generation (use existing RST files)
python preview.py --skip-introligo
```

**Using Make commands:**

```bash
# Install documentation dependencies
make install
# or manually: pip install -r requirements.txt

# Build HTML documentation
make html

# Serve documentation locally
make serve
# Then open http://localhost:8000 in your browser

# Live rebuild (auto-refresh on changes)
make livehtml
```

The generated documentation will be in `docs/_build/html/`.

### Documentation Features

- **Furo Theme** - Modern, responsive Sphinx theme
- **Celin Color Palette** - Consistent branding with light and dark modes
- **Logo and Favicon** - Custom branding assets from `_assets/`
- **Comprehensive Guide** - Installation, usage, configuration, and examples
- **API Reference** - Auto-generated from source code
- **Search Functionality** - Full-text search across all documentation

## Claude AI Integration

Introligo integrates seamlessly with Claude AI to automatically generate documentation. Add this prompt to your `.claude/claude.md` file:

````markdown
# Introligo Documentation Auto-Generation

When creating new Python scripts or modules, automatically generate an Introligo YAML documentation file alongside the code.

## Template

For each new Python file, create a corresponding `_doc.yaml` file:

```yaml
# Documentation for <module_name>
# Copyright (c) <year> <Your Name>

parent: "<parent_category>"
module: "<python.module.path>"
title: "📝 <Module Title>"
description: |
  Brief one-line description

overview: |
  Detailed overview of the module's purpose and functionality.

features:
  - "🎯 Feature 1 - Description"
  - "📦 Feature 2 - Description"
  - "⚡ Feature 3 - Description"

requirements:
  - "Python 3.8 or higher"
  - "Required dependency 1"

installation: |
  Installation instructions:

  .. code-block:: bash

     pip install <package-name>

usage_examples:
  - title: "Basic Usage"
    description: "Simple example"
    language: "python"
    code: |
      from <module> import <Class>

      # Example code
      obj = <Class>()
      result = obj.method()

notes: |
  .. tip::

     Helpful tips for users

see_also:
  - ":doc:`related_module` - Related documentation"
  - "https://example.com - External reference"

changelog: |
  **Version 1.0.0** (<date>)
    - 🎉 Initial release
```

## Rules

1. Always generate `_doc.yaml` when creating new Python files
2. Use exact YAML structure shown above
3. Fill sections based on code content and docstrings
4. Use emojis in features and changelog
5. Include practical usage examples
6. Set correct parent category and module path
````

See the [full documentation](docs/_build/html/index.html) for more details on Claude AI integration.

## License

Copyright (c) 2025 WT Tech Jakub Brzezowski

Introligo is one of the open-source components of the Celin Project. It is freely available for use in any project, commercial or non-commercial, without restrictions. While the full Celin framework is proprietary, Introligo is released as an independent, open-source tool that can be used standalone.

## Author

Jakub Brzezowski (WT Tech Jakub Brzezowski)

## Links

- Full documentation: See `introligo_doc.yaml` for comprehensive examples
- GitHub: https://jakubbrzezo.github.io/introligo
