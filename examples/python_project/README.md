# Python Project Example - String Utils

This example demonstrates how to use Introligo to document a Python project using Sphinx autodoc.

## Project Structure

```
python_project/
├── string_utils.py       # Python module with utility functions
├── introligo_config.yaml # Introligo configuration
├── README.md            # This file
└── docs/
    └── conf.py          # Sphinx configuration
```

## Prerequisites

Before running this example, ensure you have:

```bash
pip install introligo sphinx sphinx_rtd_theme
```

## Quick Start (Recommended)

The easiest way to build and preview this example:

```bash
# From the introligo project root directory:
python docs/preview.py --example python_project
# Opens at http://localhost:8000
```

## Step-by-Step Guide (Manual)

If you prefer to run each step manually:

### 1. Understand the Module Structure

The `string_utils.py` module contains well-documented functions with:
- **Docstrings** - Detailed documentation for each function
- **Type hints** - Modern Python typing for better IDE support
- **Examples** - Doctest-compatible examples in docstrings

### 2. Generate RST Documentation with Introligo

Run Introligo to convert the YAML configuration into RST files:

```bash
# From project root
python -m introligo examples/python_project/introligo_config.yaml -o examples/python_project/docs
```

This generates:
- `docs/index.rst` - Main documentation index
- `docs/generated/` - RST files for each module

### 3. Build Sphinx Documentation

The `docs/conf.py` file is already configured with:
- Python path setup for module imports
- Autodoc and Napoleon extensions
- Proper autodoc settings

```bash
cd examples/python_project/docs
sphinx-build -b html . _build/html
```

### 4. View the Documentation

Open the generated documentation:

```bash
# Linux
xdg-open _build/html/index.html

# macOS
open _build/html/index.html

# Or use Python's built-in server
python -m http.server 8000 --directory _build/html
# Then visit http://localhost:8000
```

## Configuration Highlights

### string_utils.py

Key features:
- **Google-style docstrings** - Compatible with Napoleon extension
- **Type hints** - `str`, `int`, `bool` for parameters and returns
- **Doctest examples** - Runnable examples in docstrings

### introligo_config.yaml

Key settings:
- `module: "string_utils"` - Python module to document
- `usage_examples:` - Code examples in the documentation
- `features:` - Bullet points highlighting capabilities

## What Gets Generated

Introligo creates hierarchical documentation:

1. **Index page** - Overview with navigation
2. **Utility Functions** - Parent category page
3. **String Utilities** - Detailed documentation with:
   - Overview and features
   - Installation instructions
   - Usage examples
   - Sphinx autodoc-generated API reference from docstrings

## Testing the Module

You can test the module's docstring examples:

```bash
python -m doctest string_utils.py -v
```

Or use it interactively:

```python
python3
>>> from string_utils import capitalize_words, is_palindrome
>>> capitalize_words("hello world")
'Hello World'
>>> is_palindrome("racecar")
True
```

## Customization

You can customize the documentation by:

1. **Adding more functions** to `string_utils.py` with docstrings
2. **Enhancing examples** in the YAML configuration
3. **Adding more modules** to document
4. **Creating parent-child relationships** for organization

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'string_utils'`
- **Solution**: Make sure Python can find your module:
  - Add `sys.path.insert(0, os.path.abspath('..'))` to `conf.py`
  - Or set `PYTHONPATH` before building

**Issue**: Autodoc doesn't generate documentation
- **Solution**:
  - Verify `sphinx.ext.autodoc` is in the `extensions` list in `conf.py`
  - Check that docstrings are properly formatted
  - Ensure the module can be imported without errors

**Issue**: Type hints not showing in documentation
- **Solution**: Add `sphinx.ext.napoleon` to extensions for better type hint display

## Advanced: Napoleon Extension

For better rendering of Google/NumPy style docstrings, add Napoleon to `conf.py`:

```python
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',  # Add source code links
]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
```
