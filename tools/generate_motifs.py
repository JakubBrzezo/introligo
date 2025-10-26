#!/usr/bin/env python3
"""
Generate motif examples from palettes.json
Creates both palette YAML files and example configuration files.
"""

import json
from pathlib import Path
from typing import Any

import yaml


def create_palette_yaml(theme_name: str, colors: dict[str, Any]) -> dict[str, Any]:
    """Create a palette YAML structure from theme colors."""
    # Convert color lists to dictionaries with numeric string keys (1, 2, 3, 4, 5)
    # This matches the format expected by Introligo (like celin.yaml)
    colors_as_dicts = {}
    for color_name, color_list in colors.items():
        colors_as_dicts[color_name] = {
            str(i + 1): color_value for i, color_value in enumerate(color_list)
        }

    palette: dict[str, Any] = {"colors": colors_as_dicts, "light_mode": {}, "dark_mode": {}}

    # Get color groups
    color_groups = list(colors_as_dicts.keys())

    if len(color_groups) >= 3:
        # Map colors for light mode (using lighter shades)
        # Using 1-indexed references (1, 2, 3, 4, 5) to match dict keys
        palette["light_mode"] = {
            "--color-background-primary": f"{{{color_groups[0]}.1}}",
            "--color-background-secondary": f"{{{color_groups[0]}.2}}",
            "--color-foreground-primary": f"{{{color_groups[-1]}.5}}",
            "--color-foreground-secondary": f"{{{color_groups[-1]}.4}}",
            "--color-brand-primary": f"{{{color_groups[1]}.4}}",
            "--color-brand-content": f"{{{color_groups[1]}.5}}",
            "--color-api-background": f"{{{color_groups[2]}.1}}",
            "--color-api-border": f"{{{color_groups[2]}.3}}",
            "--color-link": f"{{{color_groups[1]}.4}}",
            "--color-link--hover": f"{{{color_groups[1]}.5}}",
            "--color-sidebar-background": f"{{{color_groups[0]}.2}}",
            "--color-sidebar-foreground": f"{{{color_groups[-1]}.4}}",
        }

        # Map colors for dark mode (using darker shades)
        palette["dark_mode"] = {
            "--color-background-primary": f"{{{color_groups[-1]}.5}}",
            "--color-background-secondary": f"{{{color_groups[-1]}.4}}",
            "--color-foreground-primary": f"{{{color_groups[0]}.1}}",
            "--color-foreground-secondary": f"{{{color_groups[0]}.2}}",
            "--color-brand-primary": f"{{{color_groups[1]}.3}}",
            "--color-brand-content": f"{{{color_groups[1]}.2}}",
            "--color-api-background": f"{{{color_groups[2]}.5}}",
            "--color-api-border": f"{{{color_groups[2]}.3}}",
            "--color-link": f"{{{color_groups[1]}.3}}",
            "--color-link--hover": f"{{{color_groups[1]}.2}}",
            "--color-sidebar-background": f"{{{color_groups[-1]}.4}}",
            "--color-sidebar-foreground": f"{{{color_groups[0]}.2}}",
        }

    return palette


def create_example_yaml(theme_name: str) -> dict[str, Any]:
    """Create an example configuration YAML for a theme."""
    # Convert theme name to title case for display
    theme_title = theme_name.replace("-", " ").title()

    return {
        "index": {
            "title": f"{theme_title} Theme Documentation",
            "description": f"Example documentation using the {theme_title} color palette",
        },
        "generate_index": True,
        "sphinx": {
            "project": f"{theme_title} Example",
            "author": "Introligo",
            "copyright_year": "2025",
            "version_from_git": True,
            "fallback_version": "1.0.0",
            "project_root": ".",
            "add_project_to_path": True,
            "extensions": ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode"],
            "templates_path": ["_templates"],
            "exclude_patterns": ["_build", "Thumbs.db", ".DS_Store"],
            "language": "en",
            "html_theme": "furo",
            "html_static_path": ["_static"],
            "html_title": f"{theme_title} Documentation",
            "palette": theme_name,
            "html_theme_options": {"sidebar_hide_name": False},
        },
        "modules": {
            "getting_started": {
                "title": "Getting Started",
                "description": f"Introduction to {theme_title} themed documentation",
                "overview": f"Welcome! This example demonstrates the {theme_title} color palette.\n"
                f"The palette features beautiful colors designed for readability and aesthetics.",
            },
            "features": {"title": "Features", "description": "Key features of this theme"},
        },
    }


def main() -> None:
    """Generate motif examples from palettes.json"""
    # Read palettes.json from introligo/palettes/ directory
    # Get the project root (parent of tools directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    palettes_json = project_root / "introligo" / "palettes" / "palettes.json"

    if not palettes_json.exists():
        print(f"Error: {palettes_json} not found!")
        return

    with open(palettes_json) as f:
        themes = json.load(f)

    # Create directories relative to project root
    palettes_dir = project_root / "introligo" / "palettes"
    examples_dir = project_root / "examples"
    palettes_dir.mkdir(parents=True, exist_ok=True)
    examples_dir.mkdir(exist_ok=True)

    print(f"Generating motif examples for {len(themes)} themes...")

    for theme_name, colors in themes.items():
        print(f"\n  - {theme_name}")

        # Create palette YAML
        palette = create_palette_yaml(theme_name, colors)
        palette_file = palettes_dir / f"{theme_name}.yaml"

        with open(palette_file, "w") as f:
            yaml.dump(palette, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"    ✓ Created palette: {palette_file}")

        # Create example configuration YAML
        example = create_example_yaml(theme_name)
        example_file = examples_dir / f"introligo_with_{theme_name}_theme.yaml"

        with open(example_file, "w") as f:
            yaml.dump(example, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"    ✓ Created example: {example_file}")

    print(f"\n✓ Generated {len(themes)} motif examples successfully!")
    print(f"\nPalette files: {palettes_dir}/")
    print(f"Example files: {examples_dir}/")


if __name__ == "__main__":
    main()
