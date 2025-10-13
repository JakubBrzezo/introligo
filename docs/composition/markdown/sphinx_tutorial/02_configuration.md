## Overview

The `sphinx` section in your Introligo YAML configuration controls how `conf.py` is generated. Instead of manually writing Python configuration, you define everything in YAML, and Introligo creates a properly formatted `conf.py` for you.

## Basic Configuration Structure

```yaml
sphinx:
  # Project information
  project: "My Project"
  author: "Your Name"
  copyright_year: "2025"

  # Version management
  version_from_git: true
  fallback_version: "1.0.0"

  # Extensions
  extensions:
    - "sphinx.ext.autodoc"
    - "sphinx.ext.napoleon"

  # Theme
  html_theme: "furo"
  palette: "celin"
```

## Project Information

Define your project's metadata:

```yaml
sphinx:
  project: "My Amazing Project"
  author: "Jane Developer"
  copyright_year: "2025"  # Or omit for current year
  release: "2.1.0"
  version: "2.1"
```

**What each field does:**
- `project` - Appears in page titles and headers
- `author` - Shows in copyright notice
- `copyright_year` - Year for copyright (defaults to current year)
- `release` - Full version string (e.g., "2.1.0")
- `version` - Short version (e.g., "2.1")

## Version Management

### Automatic from Git Tags

```yaml
sphinx:
  version_from_git: true
  fallback_version: "1.0.0"
```

Introligo will:
1. Try to read the current git tag (`git describe --tags`)
2. Use the fallback version if git isn't available
3. Strip leading 'v' from tags (v1.0.0 → 1.0.0)

### Manual Version

```yaml
sphinx:
  version_from_git: false
  release: "1.5.2"
  version: "1.5"
```

## Path Configuration

Tell Sphinx where your code lives:

```yaml
sphinx:
  project_root: "."  # Relative to docs directory
  add_project_to_path: true  # Add to sys.path for imports
```

**Example directory structure:**
```
myproject/
├── mypackage/          # Your Python code
│   ├── __init__.py
│   └── module.py
└── docs/
    ├── conf.py         # Auto-generated
    └── introligo_config.yaml
```

With this configuration:
- `project_root: "."` means `docs/../` (parent directory)
- Code at `myproject/mypackage` is importable

## Extensions

Extensions add features to Sphinx:

```yaml
sphinx:
  extensions:
    - "sphinx.ext.autodoc"      # Python API docs from docstrings
    - "sphinx.ext.napoleon"     # Google/NumPy style docstrings
    - "sphinx.ext.viewcode"     # Add [source] links
    - "sphinx.ext.intersphinx"  # Link to other docs
    - "sphinx.ext.mathjax"      # Math equations
    - "breathe"                 # C/C++ via Doxygen
```

### Common Extensions

**For Python Projects:**
- `sphinx.ext.autodoc` - Generate API docs from docstrings
- `sphinx.ext.napoleon` - Support Google/NumPy docstring styles
- `sphinx.ext.viewcode` - Add source code links
- `sphinx.ext.coverage` - Check documentation coverage

**For All Projects:**
- `sphinx.ext.intersphinx` - Link to Python/Sphinx docs
- `sphinx.ext.todo` - TODO notes
- `sphinx.ext.ifconfig` - Conditional content

**For C/C++:**
- `breathe` - Integrate Doxygen documentation

**For Math:**
- `sphinx.ext.mathjax` - Render LaTeX equations (HTML)
- `sphinx.ext.imgmath` - Render as images (PDF)

## Build Settings

Control what gets built:

```yaml
sphinx:
  templates_path: ["_templates"]
  exclude_patterns: ["_build", "Thumbs.db", ".DS_Store"]
  language: "en"
```

## Intersphinx Mapping

Link to external documentation:

```yaml
sphinx:
  intersphinx_mapping:
    python:
      - "https://docs.python.org/3"
      - null
    numpy:
      - "https://numpy.org/doc/stable"
      - null
    requests:
      - "https://requests.readthedocs.io/en/latest"
      - null
```

Now you can link like:
- `:py:class:`python:pathlib.Path``
- `:py:func:`requests:requests.get``

## HTML Output Options

Configure HTML generation:

```yaml
sphinx:
  html_theme: "furo"
  html_static_path: ["_static"]
  html_title: "My Project Documentation"
  html_logo: "str(PROJECT_ROOT / '_assets' / 'logo.png')"
  html_favicon: "str(PROJECT_ROOT / '_assets' / 'favicon.ico')"
```

## Complete Example

Here's a comprehensive configuration:

```yaml
index:
  title: "Complete Example"
  description: "Full-featured documentation"

generate_index: true

sphinx:
  # Project info
  project: "MyProject"
  author: "Development Team"
  copyright_year: "2025"

  # Version from git
  version_from_git: true
  fallback_version: "1.0.0"

  # Paths
  project_root: "."
  add_project_to_path: true

  # Extensions
  extensions:
    - "sphinx.ext.autodoc"
    - "sphinx.ext.napoleon"
    - "sphinx.ext.viewcode"
    - "sphinx.ext.intersphinx"
    - "sphinx.ext.mathjax"

  # Build settings
  templates_path: ["_templates"]
  exclude_patterns: ["_build", "Thumbs.db", ".DS_Store"]
  language: "en"

  # External docs
  intersphinx_mapping:
    python:
      - "https://docs.python.org/3"
      - null

  # HTML output
  html_theme: "furo"
  html_static_path: ["_static"]
  html_title: "MyProject Documentation"

  # Theme with colors
  palette: "celin"
  html_theme_options:
    sidebar_hide_name: false

  # Autodoc settings
  autodoc_default_options:
    members: true
    undoc-members: true
    member-order: "bysource"

  # Napoleon settings
  napoleon_settings:
    napoleon_google_docstring: true
    napoleon_numpy_docstring: false
    napoleon_include_init_with_doc: true

modules:
  api:
    title: "API Reference"
    module: "myproject"
    description: "Complete API documentation"
```

## What Gets Generated

From this YAML, Introligo generates a complete `conf.py`:

```python
# Configuration file for Sphinx documentation
# Auto-generated by Introligo from introligo_config.yaml

import subprocess
import sys
from pathlib import Path

# Paths
DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Project information
project = "MyProject"
author = "Development Team"
copyright = "2025, Development Team"
release = read_version()  # From git

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    # ... etc
]

# Theme
html_theme = "furo"
html_theme_options = {
    "light_css_variables": {
        # Celin color palette
        # ... 100+ lines of colors
    }
}
```

All automatically, no manual editing needed!

## Best Practices

1. **Use version_from_git** - Keeps version in sync with releases
2. **Enable intersphinx** - Better cross-references
3. **Choose a modern theme** - Furo, ReadTheDocs, or Book
4. **Use color palettes** - Professional appearance instantly
5. **Group related extensions** - Add comments in YAML

## Troubleshooting

### conf.py not generated?
Check that you have a `sphinx:` section in your YAML.

### Import errors in generated conf.py?
Verify `project_root` and `add_project_to_path` are correct.

### Theme not working?
Install it: `pip install sphinx-theme-name`

### Colors not applying?
Some themes don't support CSS variables. Use Furo for full support.

## Next Steps

Now that you understand configuration, learn about:
- **Themes and Colors** - Make your docs beautiful
- **Extensions** - Add powerful features
- **Autodoc** - Generate API documentation
