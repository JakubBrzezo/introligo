# Python Language Support

Introligo provides seamless integration with Sphinx's autodoc extension for automatic Python API documentation extraction.

## Overview

Python is Introligo's native language and has first-class support through Sphinx's powerful autodoc extension. Documentation is automatically extracted from Python docstrings, supporting multiple docstring formats including Google, NumPy, and standard Sphinx styles.

## Features

✅ **Automatic Extraction** - Uses Sphinx autodoc to extract from docstrings
✅ **Multiple Formats** - Google, NumPy, and Sphinx docstring styles
✅ **Full Integration** - Complete Sphinx autodoc feature set
✅ **Source Links** - Direct links to source code with viewcode
✅ **Inheritance Tree** - Automatic class hierarchy documentation
✅ **Type Hints** - Native Python type annotation support

## Basic Usage

### Minimal Configuration

```yaml
modules:
  my_module:
    title: "My Python Module"
    module: "mypackage.mymodule"
    description: "Core functionality"
```

### Configuration Fields

| Field | Description | Required |
|-------|-------------|----------|
| `module` | Python module path (e.g., `mypackage.submodule`) | Yes |
| `language` | Can be set to `python` (auto-detected from `module`) | No |
| `description` | Brief module description | Recommended |

## How It Works

### Automatic Detection

Introligo automatically detects Python modules:

```yaml
modules:
  utils:
    module: "myproject.utils"  # ← Automatically detected as Python
    title: "Utilities"
```

### Autodoc Integration

1. **Detection**: Introligo detects the `module` field
2. **Configuration**: Auto-adds Sphinx autodoc extensions
3. **Template**: Generates RST with `.. automodule::` directive
4. **Extraction**: Sphinx autodoc extracts docstrings at build time
5. **Documentation**: Beautiful API docs in your site!

### Generated RST

```rst
.. automodule:: myproject.utils
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:
   :special-members: __init__
```

## Complete Example

```yaml
sphinx:
  project: "My Python Project"
  html_theme: "furo"

  # Python-specific configuration
  add_project_to_path: true  # Add project to sys.path

  autodoc_default_options:
    members: true
    undoc-members: true
    special-members: "__init__"
    show-inheritance: true

modules:
  api_reference:
    title: "API Reference"
    description: "Complete Python API documentation"

  utils_module:
    parent: "api_reference"
    title: "Utilities Module"
    module: "myproject.utils"
    description: "Utility functions and helpers"

    overview: |
      The utilities module provides common helper functions
      used throughout the project.

    usage_examples:
      - title: "Basic Usage"
        language: "python"
        code: |
          from myproject.utils import slugify

          result = slugify("Hello World!")
          print(result)  # Output: hello-world

  models_module:
    parent: "api_reference"
    title: "Data Models"
    module: "myproject.models"
    description: "Core data structures"
```

## Docstring Formats

### Google Style (Recommended)

```python
def calculate(value: int, multiplier: float = 2.0) -> float:
    """Calculate the result of value * multiplier.

    Args:
        value: The base value to multiply
        multiplier: The multiplication factor (default: 2.0)

    Returns:
        The calculated result

    Raises:
        ValueError: If value is negative

    Example:
        >>> calculate(5, 2.5)
        12.5
    """
    if value < 0:
        raise ValueError("Value must be non-negative")
    return value * multiplier
```

### NumPy Style

```python
def process_data(data, threshold=0.5):
    """Process input data with threshold filtering.

    Parameters
    ----------
    data : array_like
        Input data to process
    threshold : float, optional
        Filtering threshold (default is 0.5)

    Returns
    -------
    processed : ndarray
        Processed data array

    Notes
    -----
    This function applies threshold filtering to the input data.

    Examples
    --------
    >>> process_data([1, 2, 3], threshold=1.5)
    array([2, 3])
    """
    return [x for x in data if x > threshold]
```

### Sphinx Style

```python
def connect(host, port=8080):
    """Connect to a server.

    :param str host: Server hostname
    :param int port: Server port (default: 8080)
    :return: Connection object
    :rtype: Connection
    :raises ConnectionError: If connection fails
    """
    pass
```

## Sphinx Configuration

### Auto-Configuration

Introligo automatically adds these extensions when Python modules are detected:

```yaml
sphinx:
  extensions:  # Auto-added by Introligo
    - "sphinx.ext.autodoc"      # API documentation
    - "sphinx.ext.napoleon"     # Google/NumPy style
    - "sphinx.ext.viewcode"     # Source code links
```

### Manual Configuration

You can customize autodoc behavior:

```yaml
sphinx:
  # Add project to Python path
  add_project_to_path: true
  project_root: "."

  # Autodoc options
  autodoc_default_options:
    members: true              # Document all members
    undoc-members: true        # Include undocumented
    private-members: false     # Exclude private (_name)
    special-members: "__init__"  # Include __init__
    inherited-members: true    # Show inherited
    show-inheritance: true     # Show base classes

  # Napoleon (Google/NumPy style)
  napoleon_google_docstring: true
  napoleon_numpy_docstring: true
  napoleon_include_init_with_doc: true
  napoleon_include_private_with_doc: false
  napoleon_use_param: true
  napoleon_use_rtype: true
```

## Advanced Features

### Type Hints

Python type annotations are automatically included:

```python
from typing import List, Optional, Dict

def process_items(
    items: List[str],
    config: Optional[Dict[str, int]] = None
) -> List[str]:
    """Process a list of items with optional configuration.

    Args:
        items: List of items to process
        config: Optional configuration dictionary

    Returns:
        Processed items
    """
    return items
```

**Generated documentation shows:**
- `items` (List[str]) – List of items to process
- `config` (Optional[Dict[str, int]]) – Optional configuration dictionary
- **Returns:** List[str]

### Class Documentation

```python
class DataProcessor:
    """Process data with configurable options.

    Args:
        threshold: Processing threshold
        verbose: Enable verbose output

    Attributes:
        threshold (float): Current threshold value
        count (int): Number of items processed
    """

    def __init__(self, threshold: float = 0.5, verbose: bool = False):
        self.threshold = threshold
        self.verbose = verbose
        self.count = 0

    def process(self, data: list) -> list:
        """Process the input data.

        Args:
            data: Input data to process

        Returns:
            Processed data
        """
        self.count += len(data)
        return [x for x in data if x > self.threshold]
```

### Multiple Modules

Document several related modules:

```yaml
modules:
  api:
    title: "API Reference"

  core_module:
    parent: "api"
    module: "myproject.core"
    title: "Core Module"

  utils_module:
    parent: "api"
    module: "myproject.utils"
    title: "Utilities"

  models_module:
    parent: "api"
    module: "myproject.models"
    title: "Data Models"
```

## Best Practices

### 1. Use Google Style Docstrings

```python
def good_function(param1, param2):
    """One-line summary.

    Detailed description here.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    pass
```

### 2. Add Type Hints

```python
def typed_function(value: int, name: str) -> dict:
    """Function with type hints."""
    return {"value": value, "name": name}
```

### 3. Document All Public APIs

```python
class MyClass:
    """Class docstring is required."""

    def public_method(self):
        """All public methods need docstrings."""
        pass

    def _private_method(self):
        # Private methods can have regular comments
        pass
```

### 4. Use Examples

```python
def slugify(text: str) -> str:
    """Convert text to URL-friendly slug.

    Args:
        text: Text to convert

    Returns:
        URL-friendly slug

    Example:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("Python 3.10")
        'python-3-10'
    """
    pass
```

### 5. Organize with Parents

```yaml
modules:
  api:
    title: "API Reference"

  core:
    parent: "api"
    module: "myproject.core"
    title: "Core"

  core_auth:
    parent: "core"
    module: "myproject.core.auth"
    title: "Authentication"
```

## Troubleshooting

### Module Not Found

**Problem:** `WARNING: autodoc: failed to import module 'mymodule'`

**Solution:**
```yaml
sphinx:
  add_project_to_path: true
  project_root: "."
```

Or set `PYTHONPATH` before building:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
sphinx-build -b html docs docs/_build/html
```

### Missing Documentation

**Problem:** Functions appear but have no documentation

**Solution:** Add docstrings to your Python code:
```python
def my_function():
    """Add this docstring!"""
    pass
```

### Private Members Showing

**Problem:** Private methods (`_method`) appear in docs

**Solution:**
```yaml
sphinx:
  autodoc_default_options:
    private-members: false
```

### Import Errors

**Problem:** Module imports fail during doc build

**Solution:** Install dependencies or mock them:
```yaml
sphinx:
  autodoc_mock_imports:
    - "numpy"
    - "pandas"
    - "torch"
```

## Example Project Structure

```
myproject/
├── myproject/
│   ├── __init__.py
│   ├── core.py       # Core functionality
│   ├── utils.py      # Utilities
│   └── models.py     # Data models
├── docs/
│   ├── introligo_config.yaml
│   └── (generated RST files)
└── setup.py
```

**Configuration:**
```yaml
sphinx:
  project: "My Project"
  add_project_to_path: true
  project_root: ".."

modules:
  api:
    title: "API"

  core:
    parent: "api"
    module: "myproject.core"
    title: "Core"

  utils:
    parent: "api"
    module: "myproject.utils"
    title: "Utilities"
```

## Comparison with Other Languages

| Feature | Python | C/C++ | Go |
|---------|--------|-------|-----|
| **Source** | Docstrings | Comments | Comments |
| **Tool** | autodoc | Doxygen | go doc |
| **Build Time** | Sphinx | Doxygen + Sphinx | go doc + Introligo |
| **Type Hints** | ✅ Native | ⚠️ Limited | ✅ Native |
| **Examples** | ✅ In docstrings | ⚠️ External | ✅ In comments |
| **Inheritance** | ✅ Automatic | ✅ Automatic | N/A |

## See Also

- [Sphinx autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
- [Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [Google Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 – Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Type Hints (PEP 484)](https://www.python.org/dev/peps/pep-0484/)

## Summary

Introligo's Python support provides:

✅ **Zero-configuration** autodoc integration
✅ **Multiple docstring styles** (Google, NumPy, Sphinx)
✅ **Type hint support** for modern Python
✅ **Complete Sphinx features** (inheritance, source links, etc.)
✅ **Easy organization** with parent-child hierarchy

Python documentation in Introligo is as simple as specifying the module name!
