# Configuration file for Sphinx documentation for LaTeX project example

# -- Project information -----------------------------------------------------
project = "Mathematical Formulas"
copyright = "2025, Example Project"
author = "Example Project"
version = "1.0"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.mathjax",  # For rendering LaTeX equations
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "alabaster"
html_static_path = []

# -- MathJax configuration ---------------------------------------------------
# MathJax is used by default for rendering math in HTML
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"

# Configure MathJax options
mathjax3_config = {
    "tex": {
        "inlineMath": [["\\(", "\\)"]],
        "displayMath": [["\\[", "\\]"]],
    }
}
