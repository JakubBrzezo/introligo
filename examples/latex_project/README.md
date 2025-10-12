# LaTeX Project Example - Mathematical Formulas

This example demonstrates how to use Introligo to include LaTeX mathematical equations in your documentation using Sphinx's math directive.

## Project Structure

```
latex_project/
├── equations.tex         # Physics equations in LaTeX
├── calculus.tex         # Calculus formulas in LaTeX
├── introligo_config.yaml # Introligo configuration
├── README.md            # This file
└── docs/
    └── conf.py          # Sphinx configuration with MathJax
```

## Prerequisites

Before running this example, ensure you have:

```bash
pip install introligo sphinx sphinx_rtd_theme
```

No LaTeX installation is required for HTML output as MathJax renders the equations in the browser.

## Quick Start (Recommended)

The easiest way to build and preview this example:

```bash
# From the introligo project root directory:
python docs/preview.py --example latex_project
# Opens at http://localhost:8000
```

## Step-by-Step Guide (Manual)

If you prefer to run each step manually:

### 1. Understand the LaTeX Files

The example includes two LaTeX files with mathematical content:

**`equations.tex`** - Physics equations:
- Einstein's mass-energy equivalence (E=mc²)
- Maxwell's equations
- Schrödinger equation
- Fourier transform

**`calculus.tex`** - Calculus formulas:
- Fundamental theorem of calculus
- Integration by parts
- Chain rule
- Taylor series
- Sum formulas

### 2. Generate RST Documentation with Introligo

Run Introligo to convert the YAML configuration into RST files:

```bash
# From project root
python -m introligo examples/latex_project/introligo_config.yaml -o examples/latex_project/docs
```

This generates:
- `docs/index.rst` - Main documentation index
- `docs/generated/` - RST files with LaTeX equations

### 3. Build Sphinx Documentation

The `docs/conf.py` file is already configured with MathJax support:

```bash
cd examples/latex_project/docs
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

### introligo_config.yaml

Key settings:
- `latex_includes: "equations.tex"` - Single file inclusion
- Or list format for multiple files:
  ```yaml
  latex_includes:
    - "equations.tex"
    - "calculus.tex"
  ```

### LaTeX File Format

LaTeX files should contain **only mathematical content**, not full document structure:

**Good** (content only):
```latex
E = mc^2

\frac{d}{dx} \int_a^x f(t) dt = f(x)
```

**Also supported** (with document wrapper - automatically stripped):
```latex
\documentclass{article}
\usepackage{amsmath}

\begin{document}

E = mc^2

\end{document}
```

### docs/conf.py

The Sphinx configuration includes:
- `sphinx.ext.mathjax` - For rendering LaTeX equations
- MathJax configuration for proper rendering
- No LaTeX installation needed for HTML output

## What Gets Generated

Introligo converts LaTeX files to RST math directives:

**Input** (`equations.tex`):
```latex
E = mc^2
```

**Generated RST**:
```rst
.. math::

   E = mc^2
```

**Rendered HTML**: Beautiful mathematical equations rendered by MathJax

## Features Demonstrated

- **LaTeX inclusion** - Include external .tex files
- **Multiple files** - Include multiple LaTeX files per module
- **Automatic conversion** - LaTeX → RST math directive
- **Document stripping** - Automatic removal of document preambles
- **MathJax rendering** - Browser-based equation rendering
- **No LaTeX required** - Works without LaTeX installation for HTML

## Use Cases

This feature is perfect for:

1. **Scientific documentation** - Include complex mathematical formulas
2. **Educational materials** - Document equations and theorems
3. **Technical specifications** - Include mathematical definitions
4. **Research documentation** - Keep equations in separate LaTeX files

## Advanced Usage

### Multiple Files

```yaml
modules:
  advanced_math:
    title: "Advanced Mathematics"
    latex_includes:
      - "linear_algebra.tex"
      - "differential_equations.tex"
      - "statistics.tex"
```

### Mixed Content

Combine LaTeX with other documentation:

```yaml
modules:
  physics_module:
    title: "Physics"
    overview: |
      This module covers fundamental physics concepts.

    latex_includes: "equations.tex"

    usage_examples:
      - title: "Example Code"
        code: |
          # Python code here
```

## PDF Output

For PDF generation, you'll need a LaTeX installation:

```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-extra

# macOS
brew install mactex

# Build PDF
sphinx-build -b latex docs docs/_build/latex
cd docs/_build/latex
make
```

## Troubleshooting

**Issue**: Equations not rendering in HTML
- **Solution**: Ensure `sphinx.ext.mathjax` is in extensions list
- Check browser console for MathJax errors
- Try a different browser

**Issue**: LaTeX syntax errors
- **Solution**: Validate your LaTeX syntax
- Test equations in a standalone LaTeX document first
- Check for unescaped special characters

**Issue**: Document preamble showing in output
- **Solution**: This should be automatic. If not, remove `\documentclass`, `\usepackage`, `\begin{document}`, and `\end{document}` from your .tex files

## Learn More

- Sphinx Math Directive: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#math
- MathJax Documentation: https://docs.mathjax.org/
- LaTeX Math Symbols: https://en.wikibooks.org/wiki/LaTeX/Mathematics
