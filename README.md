# Introligo - Documentation Generator

[![Tests](https://github.com/JakubBrzezo/introligo/actions/workflows/tests.yml/badge.svg)](https://github.com/JakubBrzezo/introligo/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/JakubBrzezo/introligo/branch/main/graph/badge.svg)](https://codecov.io/gh/JakubBrzezo/introligo)

YAML to reStructuredText documentation generator for Sphinx with hierarchical page organization and rich content support.

> **Note**: Introligo is one of the open-source components of the Celin Project, available for free use in any project.

## Overview

Introligo streamlines the documentation process by converting structured YAML configurations into properly formatted reStructuredText files for Sphinx. It supports hierarchical page organization, automatic toctree generation, and rich content features including code examples, API documentation, and custom sections.

## Features

- 📝 **YAML to RST conversion** - Write documentation in simple YAML, generate complex RST
- ⚙️ **Sphinx auto-configuration** - Auto-generate `conf.py` from YAML (NEW!)
- 🎨 **Color palettes** - Built-in themes (Celin, Default) or create custom palettes (NEW!)
- 🌳 **Hierarchical organization** - Parent-child relationships for logical structure
- 🔄 **Automatic toctree generation** - Navigation built automatically from structure
- 📦 **Sphinx autodoc integration** - Seamless API documentation from Python modules
- 🔬 **Breathe/Doxygen support** - Document C/C++ code with single or multiple files
- 🎯 **Rich content support** - Features, examples, installation guides, and more
- 🏷️ **ASCII-safe naming** - Automatic slug generation for filesystem compatibility
- 📁 **File includes** - Modular configuration with `!include` directive
- 📝 **Markdown includes** - Include markdown files in your documentation
- 📐 **LaTeX support** - Include mathematical equations from .tex files
- 🖼️ **Template customization** - Use Jinja2 templates for custom output formats
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

**NEW!** Markdown links are automatically converted to reStructuredText format:
- External links: `[text](https://url)` → `` `text <https://url>`_ ``
- Links with anchors: `[Guide](./setup.md#install)` → `:doc:`Guide (Install) <setup>``
- Images, anchors, and more are supported

**Documentation:**
- [Quick Reference](docs/MARKDOWN_LINK_QUICK_REFERENCE.md) - Cheat sheet & common patterns
- [Complete Examples](docs/MARKDOWN_LINK_EXAMPLES.md) - 6 real-world examples
- [Technical Details](docs/MARKDOWN_LINK_CONVERSION.md) - Full feature documentation

## Sphinx Configuration Auto-Generation

**NEW!** Introligo can automatically generate `conf.py` for Sphinx from your YAML configuration. No more manual Python configuration files!

### Automatic Extension Detection

**NEW!** Introligo automatically detects your project type and adds the appropriate Sphinx extensions:

- **Python projects** → Automatically adds `sphinx.ext.autodoc`, `sphinx.ext.napoleon`, `sphinx.ext.viewcode`
- **C/C++ projects** → Automatically adds `breathe` extension
- **LaTeX/Math content** → Automatically adds `sphinx.ext.mathjax`

You no longer need to manually specify common extensions!

### Basic Sphinx Configuration

```yaml
sphinx:
  project: "My Project"
  author: "Your Name"
  html_theme: "furo"
  palette: "celin"  # Built-in cosmic color palette

  # Extensions are now OPTIONAL - auto-detected from your modules!
  # You can still add custom extensions if needed:
  # extensions:
  #   - "sphinx.ext.intersphinx"
  #   - "custom_extension"
```

When you run Introligo, it automatically generates a complete `conf.py` file with:
- **Auto-detected extensions** based on project type
- Project metadata and version management
- Theme configuration with color palettes
- Autodoc and Napoleon settings
- Intersphinx mappings
- And much more!

### Built-in Color Palettes

Choose from professional color palettes:

- **`celin`** - Cosmic-inspired theme with deep space colors
- **`default`** - Clean, simple colors for general documentation

Or create your own custom palette!

### Complete Example

```yaml
index:
  title: "My Project Documentation"
  description: "Beautiful documentation"

generate_index: true

sphinx:
  project: "My Project"
  author: "Your Name"

  # Auto-read version from git tags
  version_from_git: true
  fallback_version: "1.0.0"

  # Theme with colors
  html_theme: "furo"
  palette: "celin"
  html_title: "My Project Docs"

  # Extensions are now AUTO-DETECTED!
  # Only add custom extensions if needed:
  extensions:
    - "sphinx.ext.intersphinx"  # Custom extension

  # Intersphinx (link to other docs)
  intersphinx_mapping:
    python:
      - "https://docs.python.org/3"
      - null

  # Autodoc settings
  autodoc_default_options:
    members: true
    undoc-members: true

modules:
  api:
    title: "API Reference"
    module: "myproject"  # Python module detected → autodoc, napoleon, viewcode added!
    description: "Complete API documentation"
```

### What You Get

Running `python -m introligo config.yaml -o docs` generates:
- ✅ All RST files for your documentation
- ✅ `conf.py` with full Sphinx configuration
- ✅ Color palette integrated into theme
- ✅ All extensions properly configured
- ✅ Ready to build with `sphinx-build`

No manual `conf.py` editing needed!

### Learn More

See the **Sphinx Configuration Tutorial** in the documentation for:
- Complete configuration reference
- Theme customization
- Creating custom color palettes
- Advanced features (autodoc, Breathe, math support)
- Best practices

## Requirements

- Python 3.8 or higher
- PyYAML >= 6.0
- Jinja2 >= 3.0
- Sphinx >= 4.0 (for building documentation)
- Breathe >= 4.0 (optional, for C/C++ documentation)
- Doxygen (optional, for C/C++ documentation)

## Development Environment

Introligo includes a pre-configured development container (devcontainer) for a consistent development environment across all platforms.

### Using Devcontainer (Recommended)

The devcontainer provides:
- Python 3.11 with all dependencies pre-installed
- VS Code extensions (Python, Ruff, Mypy, etc.)
- System tools (git, doxygen, graphviz)
- Automatic project setup

**Quick Start:**
1. Install Docker and VS Code with Dev Containers extension
2. Open project in VS Code
3. Click "Reopen in Container" when prompted
4. Start developing immediately!

**Documentation:**
- [Running Code in Devcontainer](docs/devcontainer_usage.md) - Complete guide for using the devcontainer
- [Setting Up Devcontainer in Your Project](docs/devcontainer_setup.md) - Configure devcontainers for your own projects

### Manual Setup

If you prefer not to use devcontainers:

```bash
# Install dependencies
pip install -e .[dev,docs,cpp]

# Install development tools
pip install pytest pytest-cov ruff mypy

# For C++ documentation support
sudo apt-get install doxygen graphviz  # Linux
brew install doxygen graphviz          # macOS
```

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
