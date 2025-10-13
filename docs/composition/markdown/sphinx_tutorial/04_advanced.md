## Autodoc for Python Projects

Automatically generate API documentation from Python docstrings.

### Basic Setup

```yaml
sphinx:
  project: "MyPythonProject"

  # Path configuration
  project_root: "."
  add_project_to_path: true

  # Enable autodoc
  extensions:
    - "sphinx.ext.autodoc"
    - "sphinx.ext.napoleon"
    - "sphinx.ext.viewcode"

  # Autodoc settings
  autodoc_default_options:
    members: true
    undoc-members: true
    member-order: "bysource"
    special-members: "__init__"
    exclude-members: "__weakref__"

modules:
  api_reference:
    title: "API Reference"
    module: "mypackage"
    description: "Complete API documentation"
```

### Docstring Styles

#### Google Style (Recommended)

```python
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers.

    This function adds two integers and returns the result.
    It's a simple example of Google-style docstrings.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        The sum of a and b

    Examples:
        >>> calculate_sum(2, 3)
        5
        >>> calculate_sum(-1, 1)
        0

    Note:
        This function works with any integers.
    """
    return a + b
```

#### NumPy Style

```python
def calculate_sum(a, b):
    """
    Calculate the sum of two numbers.

    Parameters
    ----------
    a : int
        First number to add
    b : int
        Second number to add

    Returns
    -------
    int
        The sum of a and b

    Examples
    --------
    >>> calculate_sum(2, 3)
    5
    """
    return a + b
```

### Napoleon Configuration

Control docstring processing:

```yaml
sphinx:
  napoleon_settings:
    napoleon_google_docstring: true
    napoleon_numpy_docstring: false
    napoleon_include_init_with_doc: true
    napoleon_include_private_with_doc: false
    napoleon_include_special_with_doc: true
    napoleon_use_param: true
    napoleon_use_rtype: true
    napoleon_attr_annotations: true
```

## Breathe for C/C++ Projects

Document C/C++ code using Doxygen and Breathe.

### Setup

```yaml
# Global Doxygen configuration
doxygen:
  xml_path: "../build/doxygen/xml"
  project_name: "mycpplib"

sphinx:
  project: "My C++ Library"

  extensions:
    - "breathe"

  breathe_settings:
    breathe_default_members:
      - "members"
      - "undoc-members"
    breathe_show_define_initializer: true
    breathe_show_include: true

modules:
  api:
    title: "API Reference"
    language: "cpp"

    # Document multiple files
    doxygen_files:
      - "mylib.h"
      - "mylib.cpp"
```

### Doxygen Comments

```cpp
/**
 * @brief Calculate the sum of two integers
 *
 * This function adds two integers and returns the result.
 * It's a simple example of Doxygen documentation.
 *
 * @param a First integer to add
 * @param b Second integer to add
 * @return The sum of a and b
 *
 * @note This function works with any integers
 *
 * @code
 * int result = calculate_sum(2, 3);
 * // result is now 5
 * @endcode
 */
int calculate_sum(int a, int b) {
    return a + b;
}
```

### Workflow

```bash
# 1. Generate Doxygen XML
doxygen Doxyfile

# 2. Generate Sphinx docs with Introligo
python -m introligo config.yaml -o docs

# 3. Build HTML
cd docs
sphinx-build -b html . _build/html
```

## Math Support

Include mathematical equations in your documentation.

### Enable MathJax

```yaml
sphinx:
  extensions:
    - "sphinx.ext.mathjax"

  # Optional: MathJax configuration
  custom_settings:
    mathjax3_config:
      tex:
        inlineMath: [['\\(', '\\)']]
        displayMath: [['\\[', '\\]']]
```

### Using Math

#### In Markdown/RST

```rst
The quadratic formula is:

.. math::

   x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
```

#### From LaTeX Files

```yaml
modules:
  mathematics:
    title: "Mathematical Formulas"
    latex_includes: "equations.tex"
```

**equations.tex:**
```latex
E = mc^2

\nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}

\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
```

## Multi-Language Support

### Internationalization

```yaml
sphinx:
  language: "en"  # or "es", "fr", "de", etc.
  locale_dirs: ["locale/"]
  gettext_compact: false
```

Generate translation templates:

```bash
# Extract translatable strings
sphinx-build -b gettext docs docs/_build/gettext

# Create .po files for your language
sphinx-intl update -p docs/_build/gettext -l es
```

## Custom Extensions

Add custom Sphinx extensions:

### Create Extension

**docs/_ext/my_extension.py:**
```python
def setup(app):
    """Register the extension with Sphinx"""
    app.add_directive('mydir', MyDirective)
    return {
        'version': '1.0',
        'parallel_read_safe': True,
    }

class MyDirective(Directive):
    def run(self):
        # Your custom directive logic
        pass
```

### Enable Extension

```yaml
sphinx:
  extensions:
    - "_ext.my_extension"
```

## Search Configuration

Customize documentation search:

```yaml
sphinx:
  html_search_language: "en"
  html_search_options:
    type: "default"

  custom_settings:
    html_search_scorer: "_static/scorer.js"
```

## Performance Optimization

### Parallel Building

```yaml
sphinx:
  custom_settings:
    # Use multiple CPU cores
    numjobs: "auto"
```

Build with:
```bash
sphinx-build -j auto -b html docs docs/_build/html
```

### Caching

```yaml
sphinx:
  custom_settings:
    # Enable caching
    keep_warnings: true
```

## Advanced HTML Options

### Custom HTML Output

```yaml
sphinx:
  html_title: "My Project v2.0"
  html_short_title: "MyProject"
  html_baseurl: "https://docs.myproject.io"

  html_show_sourcelink: true
  html_show_sphinx: false
  html_show_copyright: true

  html_use_index: true
  html_split_index: false
  html_copy_source: true
  html_show_sourcelink: true

  html_sidebars:
    "**": ["sidebar-nav-bs.html", "sidebar-ethical-ads.html"]
```

## PDF Generation

Generate PDF documentation:

```yaml
sphinx:
  extensions:
    - "sphinx.ext.imgmath"  # For LaTeX math in PDF

  latex_elements:
    papersize: "letterpaper"
    pointsize: "10pt"
    preamble: |
      \usepackage{amsmath}
      \usepackage{amssymb}
```

Build PDF:
```bash
sphinx-build -b latex docs docs/_build/latex
cd docs/_build/latex
make
```

## Automated Builds

### GitHub Actions

**.github/workflows/docs.yml:**
```yaml
name: Documentation

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install PyYAML jinja2 sphinx furo

      - name: Generate documentation
        run: |
          python -m introligo docs/introligo_config.yaml -o docs
          cd docs
          sphinx-build -b html . _build/html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_build/html
```

### Pre-commit Hook

**.git/hooks/pre-commit:**
```bash
#!/bin/bash

# Regenerate documentation before commit
python -m introligo docs/introligo_config.yaml -o docs
git add docs/conf.py docs/generated/
```

## Testing Documentation

### Doctest

Test code examples in docstrings:

```yaml
sphinx:
  extensions:
    - "sphinx.ext.doctest"
```

Run tests:
```bash
sphinx-build -b doctest docs docs/_build/doctest
```

### Linkcheck

Verify external links:

```bash
sphinx-build -b linkcheck docs docs/_build/linkcheck
```

### Coverage

Check documentation coverage:

```yaml
sphinx:
  extensions:
    - "sphinx.ext.coverage"
```

```bash
sphinx-build -b coverage docs docs/_build/coverage
```

## Complete Advanced Example

```yaml
index:
  title: "Advanced Project Documentation"
  description: "Full-featured documentation with all bells and whistles"

generate_index: true

# Doxygen for C++ code
doxygen:
  xml_path: "../build/doxygen/xml"
  project_name: "mylib"

sphinx:
  # Project info
  project: "Advanced Project"
  author: "Engineering Team"
  version_from_git: true
  fallback_version: "2.0.0"

  # Paths
  project_root: "."
  add_project_to_path: true

  # All the extensions
  extensions:
    - "sphinx.ext.autodoc"
    - "sphinx.ext.napoleon"
    - "sphinx.ext.viewcode"
    - "sphinx.ext.intersphinx"
    - "sphinx.ext.mathjax"
    - "sphinx.ext.doctest"
    - "sphinx.ext.coverage"
    - "breathe"

  # External docs
  intersphinx_mapping:
    python:
      - "https://docs.python.org/3"
      - null
    numpy:
      - "https://numpy.org/doc/stable"
      - null

  # Theme
  html_theme: "furo"
  palette: "celin"
  html_title: "Advanced Project v2.0"
  html_logo: "str(PROJECT_ROOT / '_assets' / 'logo.png')"

  html_theme_options:
    sidebar_hide_name: false
    navigation_with_keys: true

  # Autodoc
  autodoc_default_options:
    members: true
    undoc-members: true
    member-order: "bysource"

  # Napoleon
  napoleon_settings:
    napoleon_google_docstring: true
    napoleon_include_init_with_doc: true

  # Breathe
  breathe_settings:
    breathe_default_members: ["members"]

  # Performance
  custom_settings:
    numjobs: "auto"

modules:
  python_api:
    title: "Python API"
    module: "myproject.python"
    description: "Python API reference"

  cpp_api:
    title: "C++ API"
    language: "cpp"
    doxygen_files:
      - "mylib.h"
      - "mylib.cpp"

  mathematics:
    title: "Mathematical Formulas"
    latex_includes: "equations.tex"
```

## Best Practices

1. **Use autodoc for Python** - Don't write API docs manually
2. **Enable Napoleon** - Support modern docstring styles
3. **Add intersphinx** - Link to external documentation
4. **Include viewcode** - Users appreciate source links
5. **Test your examples** - Use doctest
6. **Check links** - Run linkcheck regularly
7. **Optimize builds** - Use parallel building
8. **Automate** - Use CI/CD for documentation builds

## Next Steps

You now know how to:
- ✅ Generate API documentation automatically
- ✅ Document C/C++ code with Breathe
- ✅ Include mathematical equations
- ✅ Customize and optimize builds
- ✅ Set up automated documentation

Start building professional documentation for your project!
