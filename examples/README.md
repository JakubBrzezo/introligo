# Introligo Examples

**Learn by example.** This directory contains configurations demonstrating Hub Mode and Classic Mode usage.

## 🚀 Start Here: Hub Mode

### Recommended First Example

**[hub_project/](hub_project/)** - Complete realistic project showing Hub Mode in action.

This is the example to start with! It demonstrates:
- Auto-discovery of README, CHANGELOG, CONTRIBUTING, LICENSE
- Smart categorization of documentation
- Mixing auto-discovered docs with manual API documentation
- Professional Sphinx output

**Run it:**
```bash
cd examples/hub_project
python -m introligo introligo_config.yaml -o /tmp/hub_output -v
cd /tmp/hub_output
sphinx-build -b html . _build/html
```

## Hub Mode Examples

Hub Mode automatically discovers and organizes your documentation. **Use this for most projects.**

### [hub_example.yaml](hub_example.yaml)
Minimal hub configuration showing the essentials.

**What it shows:**
- Minimal configuration (just discovery section)
- Auto-include common files
- Scan paths and exclusions

**Perfect for:** Understanding Hub Mode basics

### [hub_project/](hub_project/)
Complete realistic project with actual documentation files.

**What it shows:**
- Real README, CHANGELOG, CONTRIBUTING, LICENSE
- Markdown guides (tutorial, user guide)
- How auto-discovered docs are categorized
- Mixing auto-discovery with manual modules

**Perfect for:** Seeing Hub Mode in a real project structure

## Classic Mode Examples

Classic Mode gives you complete manual control. **Use this when you need precise organization.**

### [python_project/](python_project/)
Python project with autodoc.

**What it shows:**
- Sphinx autodoc for Python modules
- Auto-detected Python extensions
- Manual module organization

**When to use:** API-heavy Python libraries needing specific structure

### [c_project/](c_project/)
C library with Doxygen integration.

**What it shows:**
- Doxygen XML integration
- Breathe extension auto-detection
- C code documentation

**When to use:** C/C++ projects with existing Doxygen setup

### [latex_project/](latex_project/)
LaTeX mathematical content.

**What it shows:**
- LaTeX file inclusion
- Math formulas in docs
- MathJax auto-detection

**When to use:** Mathematical or scientific documentation

### [rst_project/](rst_project/)
Existing RST files inclusion.

**What it shows:**
- Native RST file inclusion
- No conversion needed
- Mixed RST and YAML

**When to use:** Existing RST documentation you want to integrate

## Quick Reference

### Hub Mode Minimal Config

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
```

### Hub Mode Recommended Config

```yaml
index:
  title: "My Docs"

discovery:
  enabled: true
  scan_paths: ["."]
  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true
    markdown_docs: "docs/**/*.md"

sphinx:
  project: "My Project"
  html_theme: "furo"
  palette: "celin"
```

### Hybrid Mode (Hub + Manual)

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true

modules:
  api:
    title: "API"
    module: "myproject"
```

### Classic Mode

```yaml
modules:
  getting_started:
    title: "Getting Started"
    file_includes: "README.md"

  api:
    title: "API Reference"
    module: "myproject"
```

## Decision Guide

### Use Hub Mode When:
- ✅ You have existing documentation scattered around
- ✅ You want automatic organization
- ✅ You prefer convention over configuration
- ✅ You're starting fresh and want it simple

### Use Classic Mode When:
- ✅ You need precise hierarchical control
- ✅ You have complex parent-child relationships
- ✅ You're building docs from scratch with specific structure
- ✅ Auto-categorization doesn't fit your needs

### Use Hybrid Mode When:
- ✅ You want auto-discovery for common files
- ✅ But need manual control for specific sections
- ✅ **This is the sweet spot for most projects!**

## Using the Preview Script

The `docs/preview.py` script makes testing examples easy:

```bash
# List all available examples
python docs/preview.py --list-examples

# Run a specific example
python docs/preview.py --example python_project

# Run example without serving (build only)
python docs/preview.py --example python_project --no-serve

# Run example on custom port
python docs/preview.py --example python_project --port 8080
```

## Example Structure

Each example follows this structure:

```
example_name/
├── introligo_config.yaml    # Introligo configuration
├── README.md                # Step-by-step guide
├── source files...          # Python, C, or other source files
└── docs/                    # Generated after running (auto-created)
    ├── index.rst
    ├── generated/
    └── _build/html/         # Built HTML documentation
```

## Requirements

### Basic (Hub Mode)
```bash
pip install PyYAML jinja2 sphinx furo
```

### With Python Autodoc
```bash
pip install PyYAML jinja2 sphinx furo
```

### With C/C++ Support
```bash
# Python packages
pip install PyYAML jinja2 sphinx furo breathe

# System packages
# Ubuntu/Debian:
sudo apt-get install doxygen

# macOS:
brew install doxygen
```

## Documentation Workflow

### Hub Mode Workflow (Recommended)

1. **Prepare** - Ensure you have README.md, CHANGELOG.md, and docs/
2. **Configure** - Create minimal `introligo_config.yaml` with discovery
3. **Generate** - Run `python -m introligo config.yaml -o docs -v`
4. **Preview** - Build with Sphinx and view
5. **Refine** - Add manual modules as needed

### Classic Mode Workflow

1. **Prepare** - Write source code with documentation
2. **Configure** - Create detailed `introligo_config.yaml` with all modules
3. **Generate** - Run Introligo
4. **Preview** - View at http://localhost:8000
5. **Iterate** - Edit and rebuild as needed

## Tips

### For Hub Mode
- **Keep docs where they are** - Don't reorganize for Introligo
- **Start minimal** - Add `readme: true` first, then expand
- **Use verbose mode** - See what's being discovered with `-v`
- **Override when needed** - Add manual modules for special cases

### For Classic Mode
- **Python projects**: Use docstrings with type hints for best results
- **C/C++ projects**: Run `doxygen` before Introligo to generate XML
- **Organization**: Use parent-child relationships in YAML for hierarchy
- **Examples**: Add `usage_examples` in YAML for better documentation

## Troubleshooting

### Hub Mode

**Problem**: No docs discovered
- **Solution**: Check `discovery.enabled: true` is set
- **Solution**: Verify file patterns with `-v` flag
- **Solution**: Check `exclude_patterns` isn't too aggressive

**Problem**: Wrong categorization
- **Solution**: Override with manual modules
- **Solution**: Adjust file content keywords

### Classic Mode

**Problem**: Python module not found
- **Solution**: Ensure the module is in PYTHONPATH
- **Solution**: Check module name in config

**Problem**: C documentation empty
- **Solution**: Run `doxygen Doxyfile` first to generate XML files

## Next Steps

1. **Start with** [hub_project/](hub_project/) to see Hub Mode in action
2. **Try** hub_example.yaml for your own project
3. **Explore** Classic Mode examples for specific use cases
4. **Read** [EXAMPLES.md](EXAMPLES.md) for comprehensive documentation

## Learn More

- **Getting Started:** See [../GETTING_STARTED.md](../GETTING_STARTED.md)
- **Full Documentation:** See [../README.md](../README.md)
- **Technical Details:** See [../HUB_ARCHITECTURE.md](../HUB_ARCHITECTURE.md)
- **All Examples Explained:** See [EXAMPLES.md](EXAMPLES.md)

---

**Most users should start with Hub Mode!** It's simpler and handles 90% of use cases automatically.
