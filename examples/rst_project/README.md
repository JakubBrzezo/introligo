# RST Project Example - Including reStructuredText Files

This example demonstrates how to use Introligo to include existing reStructuredText (RST) files in your documentation.

## Project Structure

```
rst_project/
├── architecture.rst       # Architecture documentation
├── api_details.rst       # API reference documentation
├── tutorial.rst          # Getting started tutorial
├── introligo_config.yaml # Introligo configuration
├── README.md            # This file
└── docs/
    └── (generated files)
```

## Prerequisites

Before running this example, ensure you have:

```bash
pip install introligo sphinx sphinx_rtd_theme
```

## Quick Start (Recommended)

The easiest way to build and preview this example:

```bash
# From the introligo project root directory:
cd docs
python preview.py --example rst_project
# Opens at http://localhost:8000
```

## Step-by-Step Guide (Manual)

If you prefer to run each step manually:

### 1. Understand the RST Files

This example includes three RST documentation files:

**`architecture.rst`** - System architecture documentation:
- Core components description
- Component interaction diagrams
- Design patterns
- Scalability considerations

**`api_details.rst`** - API reference documentation:
- Authentication methods
- API endpoints with examples
- Error handling
- Rate limiting information

**`tutorial.rst`** - Getting started tutorial:
- Installation instructions
- Quick start examples
- Step-by-step guides
- Common usage patterns
- Troubleshooting

### 2. Generate Documentation with Introligo

Run Introligo to convert the YAML configuration into RST files:

```bash
# From project root
python -m introligo examples/rst_project/introligo_config.yaml -o examples/rst_project/docs
```

This generates:
- `docs/index.rst` - Main documentation index
- `docs/generated/` - RST files with included content
- `docs/conf.py` - Sphinx configuration (if sphinx section is present)

### 3. Build Sphinx Documentation

```bash
cd examples/rst_project/docs
sphinx-build -b html . _build/html
```

### 4. View the Documentation

Open the generated documentation:

```bash
# Linux
xdg-open _build/html/index.html

# macOS
open _build/html/index.html

# Or use Python's built-in server
python -m http.server 8000 --directory _build/html
# Then visit http://localhost:8000
```

## Configuration Highlights

### introligo_config.yaml

The configuration shows different ways to include RST files:

**Single file inclusion:**
```yaml
modules:
  architecture_guide:
    title: "Architecture Guide"
    rst_includes: "architecture.rst"  # Single file
```

**Multiple files inclusion:**
```yaml
modules:
  advanced_topics:
    title: "Advanced Topics"
    rst_includes:  # Multiple files as list
      - "architecture.rst"
      - "api_details.rst"
```

### RST File Format

RST files should be standard reStructuredText format:

```rst
Section Title
=============

This is a paragraph with **bold** and *italic* text.

Subsection
----------

.. code-block:: python

   # Python code example
   print("Hello, World!")

.. note::

   This is a note directive.
```

## What Gets Generated

Introligo includes RST files directly in the generated documentation:

**Input** (`architecture.rst`):
```rst
System Architecture
===================

Core Components
---------------

...content...
```

**Generated RST** (includes the file as-is):
```rst
Architecture Guide
==================

[Your YAML content here]

System Architecture
===================

Core Components
---------------

...content...
```

## Features Demonstrated

- **RST inclusion** - Include external .rst files
- **Single file** - Include one RST file per module
- **Multiple files** - Include multiple RST files per module
- **Mixed content** - Combine RST includes with other documentation features
- **Hierarchical organization** - Organize included RST files in documentation structure
- **Native format** - RST files included as-is (no conversion needed)

## Use Cases

This feature is perfect for:

1. **Migrating existing docs** - Include existing RST documentation in Introligo
2. **Separate maintenance** - Keep technical docs in separate files
3. **Team collaboration** - Different team members can work on different RST files
4. **Version control** - Track changes to documentation separately
5. **Reusable content** - Include the same RST file in multiple modules

## Advanced Usage

### Combining Different Include Types

You can mix RST includes with other content types:

```yaml
modules:
  my_module:
    title: "My Module"

    # Regular Introligo content
    description: "Module description"
    features:
      - "Feature 1"
      - "Feature 2"

    # Include RST files
    rst_includes: "detailed_docs.rst"

    # Include markdown files (converted to RST)
    markdown_includes: "user_guide.md"

    # Include LaTeX equations
    latex_includes: "formulas.tex"
```

### Path Resolution

All paths in `rst_includes` are resolved relative to the configuration file:

```yaml
# If config is at: /project/docs/config.yaml
# And you specify: rst_includes: "content/api.rst"
# Introligo looks for: /project/docs/content/api.rst
```

### Organizing Large Projects

For large projects with many RST files:

```
project/
├── docs/
│   ├── rst_files/
│   │   ├── architecture/
│   │   │   ├── overview.rst
│   │   │   └── components.rst
│   │   └── api/
│   │       ├── endpoints.rst
│   │       └── authentication.rst
│   └── introligo_config.yaml
```

```yaml
modules:
  architecture:
    title: "Architecture"
    rst_includes:
      - "rst_files/architecture/overview.rst"
      - "rst_files/architecture/components.rst"
```

## When to Use RST Includes

**Use RST includes when:**
- ✅ You have existing RST documentation to integrate
- ✅ You want to maintain documentation in separate files
- ✅ Multiple people are editing different doc sections
- ✅ You need fine-grained control over RST formatting
- ✅ You're migrating from another Sphinx project

**Use Introligo's built-in features when:**
- ⚡ You're starting fresh documentation
- ⚡ You want simpler YAML-based configuration
- ⚡ You need automatic Python API documentation (autodoc)
- ⚡ You prefer managing everything in one config file

## Comparison with Other Include Types

| Feature | RST Includes | Markdown Includes | LaTeX Includes |
|---------|-------------|------------------|----------------|
| File format | `.rst` | `.md` | `.tex` |
| Conversion | None (native) | MD → RST | Wrapped in math directive |
| Best for | Technical docs | General content | Mathematical formulas |
| Directives | Full RST support | Converted to RST | Math equations only |

## Troubleshooting

**Issue**: RST file not found
- **Solution**: Check that the path is correct relative to the config file
- Verify the file exists and has correct permissions

**Issue**: RST syntax errors in generated docs
- **Solution**: Validate your RST files using `rst2html` or similar tools
- Check for proper indentation and directive syntax

**Issue**: Content not appearing in output
- **Solution**: Ensure the RST file is not empty
- Check Introligo output for warnings
- Run with `-v` flag for verbose output: `python -m introligo config.yaml -o docs -v`

**Issue**: Duplicate headings
- **Solution**: Be mindful of heading levels in included RST files
- Adjust heading levels to fit within the generated document structure

## Learn More

- reStructuredText Primer: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
- Sphinx Directives: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
- reStructuredText Specification: https://docutils.sourceforge.io/rst.html

## Contributing

If you have suggestions for improving this example or find issues, please:
1. Check existing issues on GitHub
2. Create a new issue with details
3. Submit a pull request with improvements
