# Changelog

All notable changes to Introligo will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-06

### Added
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

[1.1.0]: https://github.com/JakubBrzezo/introligo/compare/1.0.0...v1.1.0
[1.0.0]: https://github.com/JakubBrzezo/introligo/releases/tag/v1.0.0
