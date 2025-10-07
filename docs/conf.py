# Configuration file for the Sphinx documentation builder.
# Introligo - Documentation Generator
#
# Copyright (c) 2025 WT Tech Jakub Brzezowski
# This is an open-source component of the Celin Project

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def read_version():
    """Read version from git tags, fallback to '1.1.0'.
    Uses `git describe --tags --exact-match` to get the exact tag if HEAD is on a tag,
    otherwise `git describe --tags --abbrev=0` to get the latest tag.
    Strips leading 'v' if present.

    Returns:
        str: The version string.
    """
    try:
        # prefer exact tag if HEAD is on a tag
        exact = (
            subprocess.check_output(
                ["git", "describe", "--tags", "--exact-match"], stderr=subprocess.DEVNULL, text=True
            )
            .lstrip("v")
            .strip()
        )
        if exact:
            return exact
    except Exception:
        pass
    try:
        # otherwise – last tag (e.g. v1.1.0)
        last = (
            subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.DEVNULL, text=True
            )
            .lstrip("v")
            .strip()
        )
        return last
    except Exception:
        return "1.1.0"


# -- Paths --------------------------------------------------------------------
DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# -- Project information -------------------------------------------------------
project = "Introligo"
author = "WT Tech Jakub Brzezowski"
copyright = f"{datetime.now().year}, WT Tech Jakub Brzezowski"
release = read_version()

# -- General configuration -----------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- Intersphinx configuration -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

# -- HTML output options -------------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_title = "Introligo Documentation"
html_logo = str(PROJECT_ROOT / "_assets" / "introligo-logo.png")
html_favicon = str(PROJECT_ROOT / "_assets" / "favicon.ico")

html_theme_options = {
    "sidebar_hide_name": False,
    # LIGHT MODE - Celin color palette
    "light_css_variables": {
        # Celin palette variables
        "--intergalactic-space-1": "#060E1D",
        "--intergalactic-space-2": "#08162C",
        "--intergalactic-space-3": "#0B1D3A",
        "--intergalactic-space-4": "#0E2448",
        "--intergalactic-space-5": "#102C57",
        "--cosmic-dawn-1": "#1D3E80",
        "--cosmic-dawn-2": "#2C5EBF",
        "--cosmic-dawn-3": "#3A7DFF",
        "--cosmic-dawn-4": "#489CFF",
        "--cosmic-dawn-5": "#57BBFF",
        "--clouds-of-uranus-1": "#167173",
        "--clouds-of-uranus-2": "#22AAAC",
        "--clouds-of-uranus-3": "#2DE2E6",
        "--clouds-of-uranus-4": "#38FFFF",
        "--clouds-of-uranus-5": "#44FFFF",
        "--pulsar-light-1": "#7A7C7D",
        "--pulsar-light-2": "#B7B9BB",
        "--pulsar-light-3": "#F4F7FA",
        "--pulsar-light-4": "#FFFFFF",
        "--pulsar-light-5": "#FFFFFF",
        "--aurora-borealis-1": "#2E793C",
        "--aurora-borealis-2": "#45B55B",
        "--aurora-borealis-3": "#5CF279",
        "--aurora-borealis-4": "#73FF97",
        "--aurora-borealis-5": "#8AFFB5",
        "--betelgeuse-flash-1": "#804826",
        "--betelgeuse-flash-2": "#BF6D3A",
        "--betelgeuse-flash-3": "#FF914D",
        "--betelgeuse-flash-4": "#FFB560",
        "--betelgeuse-flash-5": "#FFDA73",
        "--galactic-dust-1": "#795463",
        "--galactic-dust-2": "#B57D94",
        "--galactic-dust-3": "#F2A7C6",
        "--galactic-dust-4": "#FFD1F8",
        "--galactic-dust-5": "#FFFBFF",
        "--meteor-arc-1": "#7C6B2E",
        "--meteor-arc-2": "#BBA045",
        "--meteor-arc-3": "#F9D65C",
        "--meteor-arc-4": "#FFFF73",
        "--meteor-arc-5": "#FFFF8A",
        "--echo-of-mars-1": "#802636",
        "--echo-of-mars-2": "#BF3A52",
        "--echo-of-mars-3": "#FF4D6D",
        "--echo-of-mars-4": "#FF6088",
        "--echo-of-mars-5": "#FF73A3",
        # Furo theme variables mapped to Celin colors
        "color-brand-primary": "#3A7DFF",  # cosmic-dawn-3
        "color-brand-content": "#2DE2E6",  # clouds-of-uranus-3
        "color-background-primary": "#F4F7FA",  # pulsar-light-3
        "color-background-secondary": "#FFFFFF",
        "color-foreground-primary": "#0B1D3A",  # intergalactic-space-3
        "color-foreground-secondary": "#08162C",  # intergalactic-space-2
        # Sidebar colors
        "color-sidebar-background": "#F4F7FA",  # pulsar-light-3
        "color-sidebar-background-border": "#E5E5E5",
        "color-sidebar-item-background--current": "#3A7DFF",  # cosmic-dawn-3
        "color-sidebar-item-background--hover": "#1D3E80",  # cosmic-dawn-1
        "color-sidebar-link-text": "#0B1D3A",  # intergalactic-space-3
        "color-sidebar-link-text--top-level": "#0B1D3A",
        # Links and interactive elements
        "color-link": "#3A7DFF",  # cosmic-dawn-3
        "color-link--hover": "#2DE2E6",  # clouds-of-uranus-3
        "color-link-underline": "#3A7DFF",
        "color-link-underline--hover": "#2DE2E6",
        # Code blocks
        "color-inline-code-background": "#EEF2F7",
        "color-inline-code-foreground": "#0B1D3A",
        # Headers and navigation
        "color-header-background": "#F4F7FA",
        "color-header-border": "#E5E5E5",
        "color-header-text": "#0B1D3A",
        # Additional elements
        "color-admonition-background": "#EEF7FF",
        "color-admonition-title-background": "#3A7DFF",
        "color-admonition-title": "#FFFFFF",
    },
    # DARK MODE - Celin color palette
    "dark_css_variables": {
        # Same Celin palette variables (inherited)
        "--intergalactic-space-1": "#060E1D",
        "--intergalactic-space-2": "#08162C",
        "--intergalactic-space-3": "#0B1D3A",
        "--intergalactic-space-4": "#0E2448",
        "--intergalactic-space-5": "#102C57",
        "--cosmic-dawn-1": "#1D3E80",
        "--cosmic-dawn-2": "#2C5EBF",
        "--cosmic-dawn-3": "#3A7DFF",
        "--cosmic-dawn-4": "#489CFF",
        "--cosmic-dawn-5": "#57BBFF",
        "--clouds-of-uranus-1": "#167173",
        "--clouds-of-uranus-2": "#22AAAC",
        "--clouds-of-uranus-3": "#2DE2E6",
        "--clouds-of-uranus-4": "#38FFFF",
        "--clouds-of-uranus-5": "#44FFFF",
        "--pulsar-light-1": "#7A7C7D",
        "--pulsar-light-2": "#B7B9BB",
        "--pulsar-light-3": "#F4F7FA",
        "--pulsar-light-4": "#FFFFFF",
        "--pulsar-light-5": "#FFFFFF",
        "--aurora-borealis-1": "#2E793C",
        "--aurora-borealis-2": "#45B55B",
        "--aurora-borealis-3": "#5CF279",
        "--aurora-borealis-4": "#73FF97",
        "--aurora-borealis-5": "#8AFFB5",
        "--betelgeuse-flash-1": "#804826",
        "--betelgeuse-flash-2": "#BF6D3A",
        "--betelgeuse-flash-3": "#FF914D",
        "--betelgeuse-flash-4": "#FFB560",
        "--betelgeuse-flash-5": "#FFDA73",
        "--galactic-dust-1": "#795463",
        "--galactic-dust-2": "#B57D94",
        "--galactic-dust-3": "#F2A7C6",
        "--galactic-dust-4": "#FFD1F8",
        "--galactic-dust-5": "#FFFBFF",
        "--meteor-arc-1": "#7C6B2E",
        "--meteor-arc-2": "#BBA045",
        "--meteor-arc-3": "#F9D65C",
        "--meteor-arc-4": "#FFFF73",
        "--meteor-arc-5": "#FFFF8A",
        "--echo-of-mars-1": "#802636",
        "--echo-of-mars-2": "#BF3A52",
        "--echo-of-mars-3": "#FF4D6D",
        "--echo-of-mars-4": "#FF6088",
        "--echo-of-mars-5": "#FF73A3",
        # Dark mode Furo variables - deep space theme
        "color-brand-primary": "#3A7DFF",  # cosmic-dawn-3 (same for visibility)
        "color-brand-content": "#2DE2E6",  # clouds-of-uranus-3
        "color-background-primary": "#0B1D3A",  # intergalactic-space-3 (dark)
        "color-background-secondary": "#08162C",  # intergalactic-space-2 (darker)
        "color-foreground-primary": "#F4F7FA",  # pulsar-light-3 (light text)
        "color-foreground-secondary": "#DEE5EA",
        # Dark sidebar
        "color-sidebar-background": "#08162C",  # intergalactic-space-2
        "color-sidebar-background-border": "#1A2B47",
        "color-sidebar-item-background--current": "#3A7DFF",  # cosmic-dawn-3
        "color-sidebar-item-background--hover": "#102C57",  # intergalactic-space-5
        "color-sidebar-link-text": "#F4F7FA",  # pulsar-light-3
        "color-sidebar-link-text--top-level": "#F4F7FA",
        # Dark links
        "color-link": "#3A7DFF",  # cosmic-dawn-3
        "color-link--hover": "#2DE2E6",  # clouds-of-uranus-3
        "color-link-underline": "#3A7DFF",
        "color-link-underline--hover": "#2DE2E6",
        # Dark code blocks
        "color-inline-code-background": "#102953",
        "color-inline-code-foreground": "#F4F7FA",
        # Dark headers
        "color-header-background": "#08162C",
        "color-header-border": "#1A2B47",
        "color-header-text": "#F4F7FA",
        # Dark additional elements
        "color-admonition-background": "#102953",
        "color-admonition-title-background": "#3A7DFF",
        "color-admonition-title": "#FFFFFF",
    },
}
