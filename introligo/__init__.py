#!/usr/bin/env python3
"""
Introligo - YAML to reStructuredText documentation generator for Sphinx.

Copyright (c) 2025 WT Tech Jakub Brzezowski

This is an open-source component of the Celin Project, freely available for use
in any project without restrictions.

Introligo streamlines the documentation process by converting structured YAML
configurations into properly formatted reStructuredText files for Sphinx.
"""

__version__ = "1.1.0"
__author__ = "Jakub Brzezowski"
__email__ = "brzezoo@gmail.com"
__license__ = "Apache-2.0"

# Import main classes for public API
from introligo.__main__ import (
    IncludeLoader,
    IntroligoError,
    IntroligoGenerator,
    PageNode,
    main,
)

__all__ = [
    "IntroligoGenerator",
    "IntroligoError",
    "PageNode",
    "IncludeLoader",
    "main",
    "__version__",
    "__author__",
    "__email__",
]
