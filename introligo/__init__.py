#!/usr/bin/env python
"""
Introligo - YAML to reStructuredText documentation generator for Sphinx.

Copyright (c) 2025 WT Tech Jakub Brzezowski

This is an open-source component of the Celin Project, freely available for use
in any project without restrictions.

Introligo streamlines the documentation process by converting structured YAML
configurations into properly formatted reStructuredText files for Sphinx.
"""

# Try to import version from setuptools_scm generated file, fallback to default
try:
    from introligo._version import __version__  # type: ignore[import-not-found]
except ImportError:
    # Fallback version when not installed from git (e.g., development mode)
    __version__ = "0.0.0.dev0"

__author__ = "Jakub Brzezowski"
__email__ = "brzezoo@gmail.com"
__license__ = "Apache-2.0"

# Import main classes for public API
from introligo.__main__ import main
from introligo.errors import IntroligoError
from introligo.generator import IntroligoGenerator
from introligo.markdown_converter import (
    convert_markdown_links_to_rst,
    convert_markdown_table_to_rst,
    convert_markdown_to_rst,
)
from introligo.page_node import PageNode
from introligo.utils import count_display_width, slugify
from introligo.yaml_loader import IncludeLoader, include_constructor

__all__ = [
    "IntroligoGenerator",
    "IntroligoError",
    "PageNode",
    "IncludeLoader",
    "include_constructor",
    "main",
    "slugify",
    "count_display_width",
    "convert_markdown_to_rst",
    "convert_markdown_links_to_rst",
    "convert_markdown_table_to_rst",
    "__version__",
    "__author__",
    "__email__",
]
