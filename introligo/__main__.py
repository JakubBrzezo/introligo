#!/usr/bin/env python
"""
Introligo - Documentation Hub for Unified Repository Documentation.

Copyright (c) 2025 WT Tech Jakub Brzezowski

This is an open-source component of the Celin Project, freely available for use
in any project without restrictions.

Introligo automatically discovers, organizes, and unifies all documentation in your
repository into a professional Sphinx documentation site.

PRIMARY MODE - Hub Mode (Recommended):
    Automatically discover and organize documentation across your repository.
    Introligo scans for READMEs, CHANGELOGs, markdown guides, and more, then
    intelligently categorizes them into Getting Started, User Guides, API Reference,
    and About sections.

    Example Configuration::

        discovery:
          enabled: true
          auto_include:
            readme: true
            changelog: true
            markdown_docs: "docs/**/*.md"

        modules:
          api:
            module: "myproject"  # Optional: Add API docs

CLASSIC MODE (For Power Users):
    Manually define documentation structure using YAML configuration.
    Provides complete control over hierarchy and organization.

Features:
- Auto-discovery of documentation files (Hub Mode)
- Smart categorization based on content analysis
- Multi-format support (Markdown, RST, LaTeX, Text)
- Beautiful themes with auto-generated conf.py
- Python autodoc integration
- C/C++ Doxygen/Breathe support
- Hierarchical organization
- Automatic toctree generation
- ASCII-safe folder naming
- File inclusion with !include directive
- Template customization
- Hybrid mode (mix auto-discovery with manual control)

Include Directive Usage:
    Split your configuration across multiple files using the !include directive.

    Main config file (introligo_config.yaml)::

        modules:
          utils: !include utils/utils_config.yaml
          build_tools: !include build/build_config.yaml

    Module config file (utils/utils_config.yaml)::

        title: "Utility Scripts"
        description: "Collection of utilities"
        features:
          - Feature 1
          - Feature 2

    Or include entire module sections::

        modules: !include modules/all_modules.yaml

    Paths are resolved relative to the file containing the !include directive.

Language Support:
    Introligo automatically detects the project type and adds the appropriate
    Sphinx extensions. No manual extension configuration needed!

    For Python modules::

        modules:
          my_module:
            title: "My Module"
            language: python  # Optional - auto-detected from 'module' field
            module: my_package.my_module

    Auto-adds: sphinx.ext.autodoc, sphinx.ext.napoleon, sphinx.ext.viewcode

    For C/C++ with Doxygen::

        # Global Doxygen configuration
        doxygen:
          xml_path: "path/to/doxygen/xml"
          project_name: "myproject"

        modules:
          my_header:
            title: "My Header"
            language: cpp  # Auto-detected from doxygen_file
            doxygen_file: myheader.h

          my_component:
            title: "Component"
            language: cpp
            doxygen_files:
              - file1.h
              - file2.h

    Auto-adds: breathe extension with proper configuration

Palette Support:
    Define color palettes for consistent theming across your documentation.

    palette:
      colors:
        primary:
          light: "#e3f2fd"
          main: "#2196f3"
          dark: "#1976d2"
        accent:
          light: "#fff3e0"
          main: "#ff9800"
          dark: "#f57c00"

    Then reference colors using @palette syntax::

        sphinx:
          html_theme_options:
            primary_color: "@palette.primary.main"
            accent_color: "@palette.accent.main"

    Built-in palettes:
    - celin: Beautiful cosmic color scheme
    - default: Simple grayscale palette

Usage:
    python -m introligo config.yaml -o docs/
    python -m introligo config.yaml -o docs/ --dry-run
    python -m introligo config.yaml -o docs/ -t custom.jinja2 --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

# Support both direct execution and package import
if __name__ == "__main__" and __package__ is None:
    # Direct execution - add parent directory to path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from introligo.errors import IntroligoError
    from introligo.generator import IntroligoGenerator
else:
    # Package import
    from .errors import IntroligoError
    from .generator import IntroligoGenerator

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the Introligo command-line tool.

    Parses command-line arguments and executes the documentation generation.
    """
    parser = argparse.ArgumentParser(
        description="Introligo - Generate rich Sphinx RST documentation from YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s config.yaml -o docs
  %(prog)s config.yaml -o docs --dry-run
  %(prog)s config.yaml -o docs -t custom_template.jinja2
        """,
    )
    parser.add_argument("config", type=Path, help="YAML configuration file")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("docs"), help="Output directory (default: docs)"
    )
    parser.add_argument("-t", "--template", type=Path, help="Custom Jinja2 template file")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be generated without creating files"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Fail immediately if any page fails to generate"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    try:
        generator = IntroligoGenerator(
            config_file=args.config,
            output_dir=args.output,
            template_file=args.template,
            dry_run=args.dry_run,
            strict=args.strict,
        )
        generated_files = generator.generate_all()
        generator.write_files(generated_files)

        # Generate and write Breathe configuration if Doxygen is configured
        breathe_config = generator.generate_breathe_config()
        if breathe_config and not args.dry_run:
            generator.generated_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py to make it a package
            init_path = generator.generated_dir / "__init__.py"
            init_content = '''"""AUTO-GENERATED documentation files by Introligo.

WARNING: This directory and all files within are AUTO-GENERATED.
DO NOT EDIT manually - changes will be OVERWRITTEN.

To modify the documentation:
1. Edit your introligo YAML configuration file
2. Regenerate using: python -m introligo <config.yaml> -o <output_dir>
"""
'''
            init_path.write_text(init_content, encoding="utf-8")

            breathe_config_path = generator.generated_dir / "breathe_config.py"
            breathe_config_path.write_text(breathe_config, encoding="utf-8")
            logger.info(f"Generated Breathe configuration: {breathe_config_path}")
            logger.info("Import this in your conf.py: from generated.breathe_config import *")

        # Generate and write conf.py if Sphinx configuration is present
        conf_py_content = generator.generate_conf_py()
        if conf_py_content:
            if args.dry_run:
                logger.info("Would generate conf.py")
            else:
                conf_py_path = generator.output_dir / "conf.py"
                conf_py_path.write_text(conf_py_content, encoding="utf-8")
                logger.info(f"Generated Sphinx configuration: {conf_py_path}")
                logger.info(
                    "Your conf.py has been auto-generated. "
                    "To modify it, edit your introligo config and regenerate."
                )

        if not args.dry_run:
            logger.info(f"Successfully generated {len(generated_files)} RST files!")
            logger.info(f"Output directory: {args.output}")
            logger.info("Run 'sphinx-build' or your preview script to build HTML")
        else:
            logger.info(f"Dry run complete - would generate {len(generated_files)} files")

    except IntroligoError as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
