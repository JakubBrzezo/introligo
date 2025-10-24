# Documentation Hub Architecture

## Overview

Introligo has been transformed from a "YAML → RST generator" into a **Documentation Hub** that can automatically discover, organize, and combine documentation from multiple formats scattered throughout your repository.

## Core Concept

**"One place to unite all your docs"** - Introligo now serves as a central hub that:

- **Discovers** README files, CHANGELOGs, markdown guides, and other documentation
- **Organizes** them intelligently using content analysis
- **Combines** multiple formats (Markdown, RST, LaTeX, text) seamlessly
- **Generates** a coherent Sphinx documentation site

## Architecture

### 1. DocumentationHub Class (`introligo/hub.py`)

The `DocumentationHub` class is the core of the new architecture:

```python
class DocumentationHub:
    """Hub for discovering and organizing documentation across a repository."""
```

**Key Features:**

- **Auto-discovery**: Automatically finds documentation files
- **Smart categorization**: Analyzes content to determine logical sections
- **Module generation**: Creates Sphinx modules from discovered docs

**Document Types Supported:**
- README files (project overviews)
- CHANGELOG files (version history)
- CONTRIBUTING files (contribution guidelines)
- LICENSE files (license information)
- Generic markdown/RST documentation
- User guides and tutorials

### 2. Smart Categorization

Documents are automatically categorized into logical sections:

- **Getting Started** - README files, installation guides, quick starts
- **User Guides** - Tutorials, how-tos, guides
- **API Reference** - API documentation, technical references
- **About** - Changelog, contributing guidelines, license

**Categorization Logic:**

1. **README files**: Categorized based on location
   - Root README → Getting Started
   - Examples/tutorials directories → User Guides

2. **Content analysis**: Keyword-based classification
   - "installation", "setup" → Getting Started
   - "tutorial", "how to" → User Guides
   - "api", "reference", "class" → API Reference

3. **Special files**: Predefined categories
   - CHANGELOG, CONTRIBUTING, LICENSE → About

### 3. Configuration Structure

#### Conservative Discovery (Opt-in)

Discovery is **disabled by default** and must be explicitly enabled:

```yaml
discovery:
  enabled: true  # Must be set to true

  scan_paths:
    - "."          # Directories to scan
    - "docs/"
    - "examples/"

  auto_include:
    readme: true          # Auto-discover README.md
    changelog: true       # Auto-discover CHANGELOG.md
    contributing: true    # Auto-discover CONTRIBUTING.md
    license: true         # Auto-discover LICENSE
    markdown_docs: "docs/**/*.md"  # Glob patterns

  exclude_patterns:
    - "node_modules"
    - ".venv"
```

#### Hybrid Approach

You can mix auto-discovered and manually-defined modules:

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true

modules:
  # Manually defined modules
  api_reference:
    title: "API Reference"
    module: "myproject"

  # Auto-discovered modules will be added here
```

### 4. Integration with Existing Architecture

The hub integrates seamlessly with the existing IntroligoGenerator:

```python
class IntroligoGenerator:
    def __init__(self, ...):
        # ...
        self.hub: Optional[DocumentationHub] = None

    def load_config(self) -> None:
        # Initialize hub if configured
        if self.config.get("hub") or self.config.get("discovery"):
            self.hub = DocumentationHub(self.config_file, self.config)

            # Discover and generate modules
            if self.hub.is_enabled():
                discovered = self.hub.discover_documentation()
                hub_modules = self.hub.generate_hub_modules()
                self.config["modules"].update(hub_modules)
```

## Backward Compatibility

### Soft Migration Path

- ✅ **All existing configs work as-is** - No breaking changes
- ✅ **Hub features are opt-in** - Disabled by default
- ℹ️ **Future**: Deprecation warnings will guide users to new structure
- ℹ️ **Migration tools**: Planned for future versions

### Compatibility Strategy

1. **Existing configs without hub/discovery**: Work exactly as before
2. **New configs with discovery**: Get hub benefits
3. **Mixed configs**: Can use both old and new approaches

## Special Document Handlers

### README Handler

- Preserves markdown formatting
- Converts links to RST references
- Categorizes based on location

### CHANGELOG Handler

- Skips first H1 heading (typically "Changelog")
- Preserves version structure
- Automatically placed in "About" section

### LICENSE Handler

- Wraps content in literal code block
- Preserves exact formatting
- Placed in "About" section

### CONTRIBUTING Handler

- Standard markdown conversion
- Placed in "About" section

## Usage Examples

### Example 1: Basic Hub Mode

```yaml
index:
  title: "Project Documentation Hub"

discovery:
  enabled: true
  scan_paths: ["."]
  auto_include:
    readme: true
    changelog: true
    license: true
```

**Result**: Auto-discovers README.md, CHANGELOG.md, LICENSE and organizes them into appropriate sections.

### Example 2: Comprehensive Discovery

```yaml
discovery:
  enabled: true
  scan_paths:
    - "."
    - "docs/"
    - "examples/"

  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true
    markdown_docs: "docs/**/*.md"

modules:
  # Still manually define API docs
  api:
    title: "API Reference"
    module: "myproject"
```

**Result**: Combines auto-discovered documentation with manually defined API reference.

### Example 3: Repository-wide Documentation

```yaml
discovery:
  enabled: true
  scan_paths: ["."]
  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true
    markdown_docs: "**/*.md"

  exclude_patterns:
    - "node_modules"
    - ".venv"
    - "build"
```

**Result**: Scans entire repository for documentation, intelligently organizing everything.

## Testing

Comprehensive test coverage ensures hub functionality works correctly:

- `test_hub.py`: 5 tests for hub discovery and categorization
- All 205 existing tests pass
- 100% backward compatibility maintained

### Key Tests

1. **Discovery disabled by default** - Hub respects opt-in model
2. **Discovery enabled** - Correctly finds all document types
3. **Smart categorization** - Documents placed in correct sections
4. **Module generation** - Proper Sphinx module structure created
5. **Generator integration** - Hub works seamlessly with main generator

## Benefits

### For Users

✅ **Less configuration** - Auto-discover instead of manual setup
✅ **Better organization** - Smart categorization
✅ **Unified documentation** - All formats in one place
✅ **Flexibility** - Mix auto and manual approaches

### For Maintainers

✅ **Backward compatible** - No breaking changes
✅ **Well tested** - Comprehensive test coverage
✅ **Extensible** - Easy to add new document types
✅ **Clean architecture** - Separate concerns

## Future Enhancements

Potential improvements for future versions:

1. **AI-powered categorization** - Use LLMs for better classification
2. **Cross-reference detection** - Automatically link related docs
3. **Duplicate detection** - Warn about redundant content
4. **Documentation metrics** - Coverage reports, freshness tracking
5. **Migration tool** - Automated conversion from old to new config
6. **Plugin system** - Custom document type handlers

## Implementation Details

### File Structure

```
introligo/
├── __main__.py          # Main generator (enhanced with hub support)
├── hub.py               # New: Documentation hub implementation
├── templates/           # RST templates
└── palettes/           # Color palettes

tests/
└── test_hub.py         # New: Hub functionality tests

examples/
└── hub_example.yaml    # New: Hub configuration example
```

### Key Code Paths

1. **Configuration Loading** (`__main__.py:load_config`)
   - Checks for hub/discovery configuration
   - Initializes DocumentationHub if present
   - Merges auto-discovered modules with manual ones

2. **Discovery** (`hub.py:discover_documentation`)
   - Scans specified paths
   - Filters by document type
   - Excludes unwanted directories

3. **Categorization** (`hub.py:_categorize_by_content`)
   - Analyzes file content
   - Keywords-based classification
   - Location-based overrides

4. **Module Generation** (`hub.py:generate_hub_modules`)
   - Creates category parent modules
   - Generates child modules for each document
   - Maintains proper parent-child relationships

## Migration Guide

### For Existing Users

No action required! Your existing configurations work as-is.

### To Enable Hub Features

Add a `discovery` section to your config:

```yaml
# Your existing config
index:
  title: "My Docs"

modules:
  api:
    title: "API"
    module: "myproject"

# Add this to enable hub
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
```

### Best Practices

1. **Start small** - Enable one or two document types first
2. **Review output** - Check auto-discovered structure
3. **Customize** - Add manual modules as needed
4. **Iterate** - Refine scan paths and exclusions

## Summary

The Documentation Hub architecture transforms Introligo into a powerful documentation aggregator while maintaining full backward compatibility. It provides:

- **Smart auto-discovery** of documentation files
- **Intelligent categorization** based on content analysis
- **Flexible configuration** mixing auto and manual approaches
- **Special handlers** for common file types (README, CHANGELOG, etc.)
- **Comprehensive testing** ensuring reliability
- **Clean integration** with existing architecture

This architecture positions Introligo as the central hub for all repository documentation, regardless of format or location.
