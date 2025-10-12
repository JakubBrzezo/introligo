# Configuration file for Sphinx documentation for C project example

# -- Project information -----------------------------------------------------
project = "Calculator Library"
copyright = "2025, Example Project"
author = "Example Project"
version = "1.0"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "breathe",  # For integrating Doxygen XML output
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "alabaster"
html_static_path = []

# -- Breathe configuration ---------------------------------------------------
# Point Breathe to the Doxygen XML output directory
breathe_projects = {"calculator": "../output/xml"}
breathe_default_project = "calculator"

# Breathe configuration options
breathe_default_members = ("members", "undoc-members")
breathe_show_define_initializer = True
breathe_show_enumvalue_initializer = True
