# Changelog

All notable changes to Introligo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2025-01-30

### Added
- **Rust Language Support** - Automatic documentation extraction for Rust projects
  - Integration with Rust's cargo doc system
  - Automatic detection and inclusion of Rust documentation
- **Java Language Support** - Automatic documentation generation for Java projects
  - JavaDoc integration for comprehensive Java project documentation
  - Seamless conversion to Sphinx-compatible formats
- **Go Language Support** - Automatic documentation extraction for Go projects
  - **Automatic extraction** using `go doc -all` command
  - **RST conversion** - godoc output automatically converted to reStructuredText
  - **Seamless integration** - extracted docs appear directly in Sphinx site
  - **Graceful fallback** - provides pkg.go.dev links when Go is not available
  - Automatic Go language detection from `godoc_*` fields
  - Support for `godoc_package` - single Go package documentation
  - Support for `godoc_packages` - multiple Go packages
  - Support for `godoc_path` - specify local package directory
  - New `GoDocExtractor` class for documentation extraction
  - Complete test coverage for Go documentation features
  - Example Go project configuration in `examples/go_project/`
- **Theme Examples** - Additional example configurations with multiple themes
  - Demonstrations of various Sphinx themes and their configurations
  - Enhanced examples for better user guidance
- **Enhanced Testing** - Improved test coverage
  - New test for hub mode functionality
  - Additional test cases for better code coverage

### Changed
- **Code Cleanup** - Removed unused code from generator.py for better maintainability
- **Markdown Integration** - Minor fixes in markdown integration for improved reliability

### Fixed
- **MyPy Compliance** - Fixed MyPy type checking issues
- **Workflow Fixes** - Resolved issues in GitHub Actions workflows

## [1.3.0] - 2025-01-24

### Added
- **Automated PyPI Publishing** - Complete CI/CD pipeline for releases
  - New `.github/workflows/publish-pypi.yml` workflow for automated PyPI publishing
  - Triggers automatically on version tags (e.g., `v1.3.0`)
  - Uses PyPI trusted publishing (OIDC) - no API tokens needed
  - Automatic GitHub release creation with changelog extraction
  - Multi-Python version testing (3.8, 3.9, 3.10, 3.11, 3.12) after publishing
  - Distribution artifact archiving (.tar.gz and .whl files)
- **Dynamic Version Management** - Automatic version extraction from git tags
  - Integrated `setuptools-scm` for version management
  - Version automatically extracted from git tags (format: `vX.Y.Z`)
  - Auto-generated `_version.py` file during build
  - Fallback version (`0.0.0.dev0`) for development mode
  - No manual version updates needed in code
- **Documentation Hub Architecture** - Smart documentation discovery and organization
  - New `DocumentationHub` class for auto-discovering documentation files
  - Automatic discovery of README, CHANGELOG, CONTRIBUTING, and LICENSE files
  - Smart categorization by content analysis (getting_started, guides, api, about)
  - Pattern-based markdown file discovery
  - Configurable scan paths and exclusion patterns
  - Auto-generation of module configurations from discovered docs
- **Hub Configuration Support** - YAML-driven hub mode
  - New `hub` and `discovery` configuration sections
  - `auto_include` options for readme, changelog, contributing, license
  - `markdown_docs` pattern matching for custom documentation
  - `scan_paths` for targeted directory scanning
  - `exclude_patterns` for filtering unwanted files
- **Markdown Header Demotion** - Prevent duplicate H1 headers
  - Automatic header level demotion in markdown conversion
  - `demote_headers` parameter (default: `True`) in markdown converter
  - Converts `#` → `##`, `##` → `###`, etc. when including markdown files
  - Maintains proper document hierarchy when combining files
  - Prevents conflicts with YAML-defined page titles
- **Enhanced Markdown Conversion** - Extended markdown to RST features
  - Markdown link conversion: `[text](url)` → `` `text <url>`_ ``
  - Internal document links: `[text](file.md)` → `:doc:`text <file>``
  - Anchor links: `[text](#anchor)` → `:ref:`anchor``
  - Image conversion: `![alt](path)` → `.. image:: path`
  - Markdown table to RST list-table conversion
  - Link with anchor support: `[text](file.md#section)`
  - Code block preservation (links not converted inside code)
- **Template Robustness** - Better handling of optional configurations
  - Enhanced `conf.py.jinja2` with conditional checks for optional parameters
  - Graceful handling of missing `html_theme_options`
  - Default empty lists for `templates_path` and `exclude_patterns`
  - LICENSE file recognition without file extension
  - Support for common text files (LICENSE, COPYING, AUTHORS, etc.)
- **Hub Example Project** - Comprehensive demonstration
  - New `examples/hub_project/` with hub architecture showcase
  - Python package with `ComplexNumber` class for autodoc demonstration
  - Comprehensive docstrings with examples and type hints
  - `example_usage.py` script demonstrating the API
  - Hub configuration with auto-discovery enabled
  - Integration of Python autodoc with hub mode
- **Comprehensive Documentation** - Guides and references
  - New `RELEASE.md` - Complete release process guide (97 lines)
  - New `.github/workflows/README.md` - Workflow documentation
  - New `GETTING_STARTED.md` - 5-minute quickstart guide
  - New `HUB_ARCHITECTURE.md` - Technical hub architecture documentation
  - Integrated documentation files into main Introligo docs
  - Updated examples with hub configuration patterns
- **100% Test Coverage Achievement** - Extensive testing improvements
  - Fixed 25 failing tests across the test suite
  - Added `test_coverage.py` with edge case coverage
  - Added `test_include_loader.py` for YAML loader testing
  - Added `test_markdown_link_conversion.py` for markdown features
  - Enhanced existing tests with better fixtures
  - All 207 tests passing with comprehensive coverage
  - Fixed test imports and module organization

### Changed
- **Build System** - Updated for dynamic versioning
  - Added `setuptools-scm[toml]>=8.0` to build requirements
  - Changed `version` from static to `dynamic = ["version"]`
  - Added `[tool.setuptools_scm]` configuration in `pyproject.toml`
- **Version Management** - Updated version import strategy
  - Modified `introligo/__init__.py` to import from `_version.py`
  - Added fallback for development environments
  - Removed hardcoded version string
- **Markdown Converter Defaults** - Header demotion enabled by default
  - `convert_markdown_to_rst()` now demotes headers by default
  - Updated all markdown conversion tests for new behavior
  - Better integration with existing documentation hierarchies
- **Generator Imports** - Improved module organization
  - Added direct imports for markdown conversion functions
  - Fixed duplicate method definitions
  - Better separation of concerns between modules
- **Test Organization** - Restructured test imports
  - Updated `test_utils.py` to use direct imports from `utils` module
  - Updated `test_markdown_link_conversion.py` to use converter functions
  - Fixed imports in `test_include_loader.py` and `test_coverage.py`
  - Better test module structure and clarity

### Fixed
- **Template Rendering** - Resolved configuration errors
  - Fixed `'dict object' has no attribute 'html_theme_options'` error
  - Fixed invalid Python syntax in generated conf.py
  - Fixed empty template assignments causing syntax errors
  - Added proper conditional checks for all optional Sphinx parameters
- **File Type Detection** - Enhanced LICENSE handling
  - Fixed "Unsupported file type" warning for LICENSE files
  - Added filename-based detection for files without extensions
  - Support for LICENSE, COPYING, AUTHORS, CONTRIBUTORS, NOTICE files
- **Test Infrastructure** - Resolved all test failures
  - Fixed 19 failing tests in `test_utils.py` (import errors)
  - Fixed 14 failing tests in `test_markdown_link_conversion.py` (function references)
  - Fixed 2 failing tests in `test_coverage.py` (logger mock paths)
  - Fixed mypy type annotation errors (26 files checked, 0 errors)
  - Fixed all ruff linting issues (import sorting, unused imports, undefined names)
- **Type Checking** - Resolved mypy errors
  - Added explicit type annotation in `hub.py`: `modules: Dict[str, Any]`
  - Fixed `include_constructor` import references in tests
  - Updated imports from `introligo.__main__` to correct modules
  - All type checking passes cleanly
- **Logger Mocking** - Corrected test mock paths
  - Fixed logger mock from `introligo.__main__.logger` to `introligo.generator.logger`
  - Proper test coverage for warning and error logging
  - Accurate test assertions for logging behavior

### Documentation
- Integrated `GETTING_STARTED.md` into main documentation
- Integrated `HUB_ARCHITECTURE.md` into main documentation
- Created comprehensive release process guide
- Added workflow documentation for GitHub Actions
- Enhanced hub example with Python autodoc
- Updated README with hub architecture information

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

[1.4.0]: https://github.com/JakubBrzezo/introligo/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/JakubBrzezo/introligo/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/JakubBrzezo/introligo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/JakubBrzezo/introligo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/JakubBrzezo/introligo/releases/tag/v1.0.0
