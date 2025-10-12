# C Project Example - Calculator Library

This example demonstrates how to use Introligo to document a C project using Doxygen and Breathe.

## Project Structure

```
c_project/
├── calculator.h          # Header file with function declarations
├── calculator.c          # Implementation file
├── Doxyfile             # Doxygen configuration
├── introligo_config.yaml # Introligo configuration
├── README.md            # This file
├── docs/
│   └── conf.py          # Sphinx configuration
└── output/              # Doxygen output (after running doxygen)
```

## Prerequisites

Before running this example, ensure you have:

1. **Doxygen** installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install doxygen

   # macOS
   brew install doxygen
   ```

2. **Python dependencies**:
   ```bash
   pip install introligo sphinx sphinx_rtd_theme breathe
   ```

## Quick Start (Recommended)

The easiest way to build and preview this example:

```bash
# From the introligo project root directory:

# 1. Generate Doxygen XML (required for C projects)
cd examples/c_project
doxygen Doxyfile
cd ../..

# 2. Build and serve the documentation
python docs/preview.py --example c_project
# Opens at http://localhost:8000
```

## Step-by-Step Guide (Manual)

If you prefer to run each step manually:

### 1. Generate Doxygen XML

First, run Doxygen to generate XML documentation from the C source files:

```bash
cd examples/c_project
doxygen Doxyfile
cd ../..
```

This creates an `output/` directory with:
- `output/html/` - HTML documentation from Doxygen
- `output/xml/` - XML files that Introligo will use

### 2. Generate RST Documentation with Introligo

Run Introligo to convert the YAML configuration into RST files:

```bash
# From project root
python -m introligo examples/c_project/introligo_config.yaml -o examples/c_project/docs
```

This generates:
- `docs/index.rst` - Main documentation index
- `docs/generated/` - RST files for each module

### 3. Build Sphinx Documentation

The `docs/conf.py` file is already configured:

```bash
cd examples/c_project/docs
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

### Doxyfile

The Doxygen configuration includes:
- `GENERATE_XML = YES` - Required for Breathe integration
- `INPUT = calculator.h calculator.c` - Files to document
- `EXTRACT_ALL = YES` - Document all entities

### introligo_config.yaml

Key settings:
- `doxygen.xml_path: "output/xml"` - Points to Doxygen XML output
- `language: c` - Specifies C language documentation
- `doxygen_files:` - Lists files to include in documentation

## What Gets Generated

Introligo creates hierarchical documentation:

1. **Index page** - Overview with navigation
2. **API Reference** - Parent category page
3. **Calculator Functions** - Detailed API documentation with:
   - Overview and features
   - Code examples
   - Doxygen-generated API reference from comments

## Customization

You can customize the documentation by:

1. **Adding more modules** to `introligo_config.yaml`
2. **Enhancing Doxygen comments** in source files
3. **Adding usage examples** in the YAML configuration
4. **Creating parent-child relationships** for better organization

## Troubleshooting

**Issue**: Breathe can't find XML files
- **Solution**: Make sure `doxygen.xml_path` points to the correct directory
- Check that `output/xml/` exists and contains `.xml` files

**Issue**: Functions not appearing in documentation
- **Solution**: Ensure Doxygen comments are properly formatted with `/** */`
- Set `EXTRACT_ALL = YES` in Doxyfile

**Issue**: Build warnings about missing references
- **Solution**: Run `doxygen Doxyfile` before running Introligo
