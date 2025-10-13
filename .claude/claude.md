# Introligo Project - Claude AI Configuration

## Project Overview

**Introligo** is a YAML to reStructuredText (RST) documentation generator for Sphinx. It streamlines the documentation process by converting structured YAML configurations into properly formatted RST files, supporting hierarchical page organization, automatic toctree generation, and rich content features.

**Key Features:**
- YAML to RST conversion with template-based generation
- Hierarchical module organization with parent-child relationships
- Automatic toctree generation
- Python autodoc integration
- C/C++ documentation support via Doxygen/Breathe
- Markdown file inclusion with automatic conversion to RST
- File inclusion support with !include directive for modular configuration
- Custom templates and sections
- Dry-run mode for previewing changes

**Technology Stack:**
- Python 3.8+
- PyYAML for configuration parsing
- Jinja2 for template rendering
- Sphinx for documentation building
- Breathe for C/C++ integration (optional)

## Project Structure

```
introligo/
├── introligo.py              # Main script
├── README.md                 # Project readme
├── CHANGELOG.md              # Version history
├── docs/                     # Documentation
│   ├── conf.py              # Sphinx configuration
│   ├── preview.py           # Preview server script
│   ├── composition/         # Documentation source
│   │   ├── introligo_config.yaml  # Main config
│   │   └── markdown/        # Markdown documentation files
│   │       ├── basic_usage.md
│   │       ├── best_practices.md
│   │       ├── use_cases.md
│   │       └── troubleshooting.md
│   └── generated/           # Generated RST files (auto-generated)
└── .claude/                 # Claude AI configuration
    └── claude.md            # This file
```

## Development Guidelines

### Code Quality Standards

**All generated code must pass the following checks:**

1. **Ruff Linter**: `ruff check .`
   - No linting errors allowed
   - Follow all PEP 8 conventions
   - Use proper import ordering
   - Avoid complexity issues

2. **Ruff Formatter**: `ruff format --check .`
   - All code must be properly formatted
   - Consistent style across the codebase

3. **MyPy Type Checker**: `mypy introligo`
   - No type errors allowed
   - All type hints must be correct
   - Use proper type annotations

4. **Python 3.8+ Compatibility**
   - Code must be compatible with Python 3.8 and higher
   - Use `contextlib.ExitStack` for combining context managers (not parenthesized `with` syntax which requires Python 3.9+)

**Before committing code:**
```bash
# Run all checks (same as CI/CD pipeline in .github/workflows/tests.yml)
ruff check .
ruff format --check .
mypy introligo
pytest tests/ --cov=introligo --cov-report=term-missing --cov-report=xml
```

**All checks must pass without errors.**

### Code Style
- Follow PEP 8 conventions for Python code
- Use type hints where appropriate
- Write comprehensive docstrings for all public functions and classes
- Keep functions focused and modular
- Use meaningful variable and function names
- Maximum line length: 100 characters

### Documentation
- All new features must be documented in the YAML configuration
- Update CHANGELOG.md for all user-facing changes
- Add usage examples for new features
- Keep documentation up-to-date with code changes

### Testing

**Test Coverage Requirements:**
- **Target Coverage**: Test coverage should oscillate around **100%**
- **Minimum Coverage**: Never drop below 95%
- All new features must include comprehensive tests
- Test both happy paths and edge cases

**Running Tests:**
```bash
# Run all tests with coverage report
pytest tests/ --cov=introligo --cov-report=term-missing --cov-report=xml

# The coverage report will show which lines are not covered
# Example output:
# Name                    Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# introligo/__init__.py       5      0   100%
# introligo/__main__.py     450      0   100%
# -----------------------------------------------------
# TOTAL                     455      0   100%
```

**Test Best Practices:**
- Test all changes with both dry-run and actual generation
- Verify RST output builds correctly with Sphinx
- Test with different configuration scenarios
- Ensure backward compatibility
- Test error handling and edge cases
- Use fixtures for common test setup

## Working with Introligo

### Running Introligo

```bash
# Generate documentation
python introligo.py config.yaml -o docs

# Dry run (preview without creating files)
python introligo.py config.yaml -o docs --dry-run

# Verbose output
python introligo.py config.yaml -o docs -v

# Custom template
python introligo.py config.yaml -o docs -t custom_template.jinja2
```

### Building Documentation

```bash
# Navigate to docs directory
cd docs

# Generate RST files with Introligo
python ../introligo.py composition/introligo_config.yaml -o .

# Build and serve documentation
python preview.py

# Or build without serving
python preview.py --no-serve
```

### Adding New Features

When adding new features to Introligo:

1. **Implement the feature** in `introligo.py`
2. **Update the template** if needed (DEFAULT_TEMPLATE variable)
3. **Add configuration examples** to `docs/composition/introligo_config.yaml`
4. **Document the feature** with usage examples and best practices
5. **Update CHANGELOG.md** with the new feature
6. **Test thoroughly** with various configurations

### Configuration File Format

Introligo uses YAML configuration files with the following structure:

```yaml
index:
  title: "Documentation Title"
  description: "Brief description"
  overview: |
    Detailed overview with RST formatting

generate_index: true

doxygen:  # Optional, for C/C++ projects
  xml_path: "../output/xml"
  project_name: "myproject"

modules:
  module_id:
    title: "Module Title"
    parent: "parent_id"  # Optional, for hierarchy
    module: "python.module.path"  # For autodoc
    language: "python"  # python, c, cpp
    description: "Brief description"
    overview: "Detailed overview"

    # Markdown inclusion
    markdown_includes:
      - "path/to/doc.md"
      - "path/to/another.md"

    # Rich content
    features:
      - "Feature description"

    requirements:
      - "Requirement"

    installation: |
      Installation instructions

    usage_examples:
      - title: "Example Title"
        description: "Description"
        language: "python"
        code: |
          # Code here

    notes: |
      Additional notes

    see_also:
      - "Related links"

    changelog: |
      Included markdown Changelog with version history.

    custom_sections:
      - title: "Section Title"
        content: "Section content"
```

## File Naming Conventions

- Configuration files: `*_config.yaml` or `introligo_config.yaml`
- Documentation files: `*_doc.yaml` (when placing alongside code)
- Markdown files: `*.md` (for markdown includes)
- Generated files: Go into `generated/` directory
- Templates: `*.jinja2` or `*.j2`

## Important Notes

### Markdown Inclusion Feature

The markdown inclusion feature supports:
- Automatic markdown to RST conversion
- Headers (H1-H4) converted to RST section titles
- Code blocks with language syntax highlighting
- Proper emoji support
- Relative path resolution from config file location

When writing markdown for inclusion:
- Avoid H1 headers (page title comes from YAML)
- Use clean, simple markdown syntax
- Test the conversion by building docs
- Keep markdown files focused and modular

### Path Resolution

- **!include directive**: Paths are relative to the file containing the directive
- **markdown_includes**: Paths are relative to the main configuration file
- **doxygen xml_path**: Can be relative or absolute

### Emoji Support

Introligo has enhanced emoji support:
- Emojis work in titles, descriptions, and content
- Display width calculation handles emoji rendering
- Emojis are preserved through markdown to RST conversion
- Use emojis for visual appeal in features and sections

### Toctree Generation

- Automatically generates toctree directives
- Handles hierarchical page structures
- Paths are calculated relative to parent pages
- Supports maxdepth and titlesonly options

## Common Tasks

### Adding a New Documentation Page

1. Add entry to `docs/composition/introligo_config.yaml`:
```yaml
new_page:
  parent: "parent_id"  # Optional
  title: "New Page"
  description: "Description"
  overview: "Content here"
```

2. Regenerate documentation:
```bash
cd docs
python ../introligo.py composition/introligo_config.yaml -o .
python preview.py
```

### Including Markdown Documentation

1. Create markdown file in `docs/composition/markdown/`
2. Add to configuration:
```yaml
my_module:
  title: "My Module"
  markdown_includes:
    - "markdown/my_documentation.md"
```

3. Regenerate docs

### Updating the Template

1. Edit DEFAULT_TEMPLATE in `introligo.py`
2. Test with dry-run first
3. Verify RST output is valid
4. Document any new template variables

## Troubleshooting

### Issue: RST Build Errors
- Check generated RST files in `generated/` directory
- Verify RST syntax is correct
- Look for emoji-related underline issues
- Use Sphinx's verbose mode for details

### Issue: Toctree Not Showing Subpages
- Verify parent-child relationships in YAML
- Check that paths are correctly calculated
- Rebuild documentation completely

### Issue: Markdown Not Converting Properly
- Ensure markdown syntax is clean and simple
- Avoid complex markdown features
- Check that emojis are properly supported
- Test markdown conversion separately

### Issue: Import Errors
- Verify all dependencies are installed
- Check Python path configuration
- Ensure module paths are correct in YAML

## Contact and Support

- **Author**: WT Tech Jakub Brzezowski
- **GitHub**: https://github.com/JakubBrzezo/introligo
- **License**: Apache License 2.0
- **Part of**: Celin Project (open-source component)

## Special Instructions for Claude AI

When working with this project:

1. **Always run code quality checks** before completing any task (matching CI/CD pipeline in `.github/workflows/tests.yml`):
   - `ruff check .` - Must pass with no errors
   - `ruff format --check .` - Must pass with no errors
   - `mypy introligo` - Must pass with no errors
   - `pytest tests/ --cov=introligo --cov-report=term-missing` - All tests must pass, coverage ~100%
2. **Always test changes** with both dry-run and actual generation
3. **Update documentation** when modifying features
4. **Follow existing code style** and patterns
5. **Add examples** for new configuration options
6. **Update CHANGELOG.md** for user-facing changes
7. **Be mindful of RST syntax** when generating output
8. **Test emoji support** when adding new features
9. **Verify toctree generation** for hierarchical structures
10. **Check markdown conversion** when modifying that feature
11. **Use the preview server** to verify documentation builds correctly
12. **Update CHANGELOG.md file** in next tag according to convention. Do not creates new paragraph until changes in last tags are not released (by tagging)
13. **Ensure Python 3.8 compatibility** - Use `contextlib.ExitStack` for combining context managers instead of parenthesized `with` statements

When creating or modifying documentation:
- Use the existing YAML structure as a template
- Include practical usage examples
- Add tips, notes, and warnings where helpful
- Ensure proper hierarchy with parent-child relationships
- Test that generated RST builds without errors
