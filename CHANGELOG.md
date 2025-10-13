# Changelog

All notable changes to Introligo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-10-13

### Added
- **Sphinx conf.py Auto-generation** - Major rework to automatically generate Sphinx configuration
  - New `conf.py.jinja2` template for generating Sphinx configuration files
  - Automatic conf.py generation from introligo config
  - Removed need for manual conf.py maintenance in docs directory
  - Configuration-driven Sphinx setup
- **LaTeX Inclusions Support** - Include external LaTeX files in documentation
  - `latex_includes` configuration option for including LaTeX files
  - Automatic LaTeX to RST math directive conversion
  - Relative path resolution from config file location
  - Support for mathematical equations and formulas in documentation
- **Color Palette System** - Customizable color schemes for Sphinx themes
  - New palette system with YAML-based color definitions
  - Built-in `celin` palette with custom color scheme
  - Built-in `default` palette for standard Sphinx colors
  - Support for custom palette creation
  - Automatic theme color application to Sphinx configuration
- **Comprehensive Testing Infrastructure**
  - Full unit test suite with extensive coverage
  - Tests for generator, page nodes, include loader, and utilities
  - Sphinx palette tests with color validation
  - Coverage reporting integration
  - Test fixtures and utilities for test setup
- **GitHub Actions CI/CD** - Automated testing workflow
  - `.github/workflows/tests.yml` for running tests on push and PR
  - Automated linting with ruff
  - Code coverage reporting with codecov integration
- **Example Projects** - Real-world usage examples
  - Python project example with full documentation setup
  - C project example with Doxygen integration
  - LaTeX project example with mathematical documentation
  - Example configurations for different palette usage
  - Comprehensive EXAMPLES.md documentation
- **Enhanced Documentation**
  - Extensive Sphinx tutorial split across 4 chapters:
    - Introduction to Sphinx and introligo
    - Configuration and setup
    - Themes and colors customization
    - Advanced features and techniques
  - Reorganized markdown tutorial into dedicated directory
  - Enhanced README with detailed feature descriptions

### Changed
- **Template System** - Restructured template organization
  - Moved from `default.jinja2` to `conf.py.jinja2` for configuration generation
  - Updated template to generate complete Sphinx conf.py files
  - Enhanced template with palette and theme support
- **Documentation Preview** - Improved preview.py functionality
  - Updated to work with auto-generated conf.py files
  - Enhanced error handling and logging
  - Better integration with new configuration system
- Updated API exports in `__init__.py` for better module interface
- Enhanced pyproject.toml with additional development dependencies

### Fixed
- Fixed API import problems with module structure
- Fixed ruff linting issues across codebase
- Fixed codecov integration for proper coverage reporting
- Code formatting consistency improvements

## [1.1.0] - 2025-10-06

### Added
- **PyPI Package Structure** - Restructured as a proper Python package
  - Created `introligo/` package directory with proper module structure
  - Added `pyproject.toml` for modern Python packaging (PEP 621)
  - Added `setup.py` for backwards compatibility
  - Added `MANIFEST.in` for including non-Python files
  - Extracted Jinja2 template to `introligo/templates/default.jinja2`
  - Created `__init__.py` with public API exports
  - Added command-line entry point: `introligo` command
  - Added optional dependencies groups: docs, cpp, dev
  - Created `PUBLISHING.md` with PyPI publishing guide
  - Created `PACKAGE_STRUCTURE.md` documenting package structure
- **GitHub Actions CI/CD** - Automated deployment workflows
  - Added `.github/workflows/deploy-docs.yml` for GitHub Pages deployment after tagging.
  - Documentation auto-deploys to GitHub Pages on tag push
- **Markdown file inclusion support** - Include external markdown files in documentation
  - Automatic markdown to RST conversion
  - Support for headers (H1-H4), code blocks, and text formatting
  - Relative path resolution from config file location
  - Single file or multiple files support
  - Proper emoji support in markdown content
  - Auto-skip first H1 "Changelog" header to prevent duplication with YAML title
- Enhanced emoji support with improved display width calculation for RST underlines
- Comprehensive markdown includes documentation with subpages:
  - Basic Usage examples
  - Best Practices guide
  - Real-world Use Cases (8 scenarios)
  - Troubleshooting guide

### Changed
- **Package Structure** - Reorganized for PyPI distribution
  - Moved main code from `introligo.py` to `introligo/__main__.py`
  - Template now loads from `introligo/templates/default.jinja2`
  - Kept original `introligo.py` for backwards compatibility
  - Updated `docs/preview.py` to use `python -m introligo` instead of script path
- Improved `get_relative_path_from()` method for correct toctree path generation
- Enhanced `count_display_width()` function with comprehensive emoji range coverage
- Updated YAML configuration reference to clarify `markdown_includes` usage for Changelog

### Fixed
- Fixed toctree paths to be relative to parent directory instead of base directory
- Corrected subpage navigation in hierarchical documentation structures
- Fixed duplicate "Changelog" header when including CHANGELOG.md via `markdown_includes`

## [1.0.0] - 2025-10-05

### Added
- Initial release
- **!include directive** for modular configuration files
- Support for splitting documentation across multiple files
- Relative path resolution for included files
- Nested include support
- Rich content support:
  - Features lists
  - Usage examples with syntax highlighting
  - Installation guides
  - Configuration sections
  - API reference
  - Notes and see also sections
- Custom sections support for flexible documentation structure
- Enhanced error handling and logging
- Hierarchical page organization with parent-child relationships
- Automatic toctree generation
- Python autodoc integration
- C/C++ documentation support via Doxygen/Breathe
- Template-based RST generation with Jinja2
- ASCII-safe folder naming with automatic slugification
- Dry-run mode for previewing changes
- Support for multiple documentation sections
- YAML-based configuration for easy maintenance

### Features
- Support for hierarchical module organization
- Custom page titles and descriptions
- Automatic directory structure generation
- Rich content blocks (overview, features, installation, etc.)
- Multiple usage examples per module
- See also and references sections
- Changelog tracking per module
- Examples directory support
- Custom sections for flexibility

---

## Unreleased

### Planned
- Support for additional markdown features (tables, links, images)
- Multi-language documentation support
- Additional template customization options
- Enhanced metadata support
- Search optimization features

---

[1.2.0]: https://github.com/JakubBrzezo/introligo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/JakubBrzezo/introligo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/JakubBrzezo/introligo/releases/tag/v1.0.0
