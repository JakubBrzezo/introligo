# Introligo - Documentation Hub

[![Tests](https://github.com/JakubBrzezo/introligo/actions/workflows/tests.yml/badge.svg)](https://github.com/JakubBrzezo/introligo/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/JakubBrzezo/introligo/branch/main/graph/badge.svg)](https://codecov.io/gh/JakubBrzezo/introligo)

**Your repository's documentation, unified.** Automatically discover, organize, and combine all your docs—READMEs, Changelogs, Markdown guides, API docs—into one beautiful Sphinx site.

> **Note**: Introligo is an open-source component of the Celin Project, freely available for any project.

## The Problem

Your documentation is scattered:
- 📄 README.md in the root
- 📝 User guides in `docs/`
- 📋 CHANGELOG.md tracking history
- 🤝 CONTRIBUTING.md for contributors
- 📦 Python docstrings in code
- 🔧 Example READMEs in subdirectories

**Each file is useful, but together they're a mess.**

## The Solution: Introligo Hub

```yaml
# Create hub_config.yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
    markdown_docs: "docs/**/*.md"
```

```bash
python -m introligo hub_config.yaml -o docs -v
cd docs && sphinx-build -b html . _build/html
```

**Result:** Professional Sphinx documentation, automatically organized. ✨

## How It Works

### 1. Auto-Discovery
Introligo scans your repository and finds all documentation:
- README files (root and subdirectories)
- CHANGELOG.md
- CONTRIBUTING.md
- LICENSE
- Markdown guides
- RST files

### 2. Smart Organization
Documents are intelligently categorized:
- **Getting Started** → READMEs, installation guides
- **User Guides** → Tutorials, how-tos
- **API Reference** → Code documentation
- **About** → Changelog, contributing, license

### 3. Beautiful Output
Everything combines into a professional Sphinx site with:
- Automatic navigation (toctree)
- Searchable content
- Mobile-responsive design
- Light/dark mode
- Your choice of theme

## Quick Start (3 Steps)

### Step 1: Install

```bash
pip install PyYAML jinja2 sphinx furo
```

### Step 2: Create Configuration

Create `introligo_config.yaml` in your project root:

```yaml
index:
  title: "📚 My Project Docs"

discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true
    markdown_docs: "docs/**/*.md"

sphinx:
  project: "My Project"
  html_theme: "furo"
  palette: "celin"  # Beautiful cosmic theme
```

### Step 3: Generate

```bash
python -m introligo introligo_config.yaml -o docs_output -v
cd docs_output
sphinx-build -b html . _build/html
python -m http.server 8000 --directory _build/html
```

Open http://localhost:8000 — your docs are ready! 🎉

## Features

### 🔍 Auto-Discovery
- Finds README, CHANGELOG, CONTRIBUTING, LICENSE automatically
- Scans for markdown files by pattern
- Discovers documentation anywhere in your repo

### 🧠 Smart Categorization
- Analyzes content to determine correct section
- Keywords-based classification
- Location-aware organization
- Handles multiple READMEs intelligently

### 📚 Multi-Format Support
- **Markdown** → Converted to RST with smart link handling
- **RST** → Included natively
- **LaTeX** → Mathematical formulas
- **Text** → Literal blocks
- **Python** → Sphinx autodoc (automatic API extraction)
- **C/C++** → Doxygen/Breathe integration (automatic API extraction)
- **Go** → Automatic extraction via `go doc` (when Go is installed)

### 🎨 Beautiful Themes
- Built-in Celin palette (cosmic colors)
- Built-in Default palette
- Custom palette support
- Furo, RTD, Alabaster themes
- Auto-generated `conf.py`

### 🎯 Flexible Configuration
- Hub Mode (automatic) - Recommended
- Classic Mode (manual control) - Power users
- Hybrid (mix both) - Best of both worlds

## Real-World Example

Here's what Introligo finds in a typical project:

```
my-project/
├── README.md                  → Getting Started
├── CHANGELOG.md               → About
├── CONTRIBUTING.md            → About
├── LICENSE                    → About
├── docs/
│   ├── tutorial.md           → User Guides
│   ├── user-guide.md         → User Guides
│   └── advanced.md           → User Guides
└── src/
    ├── myproject/            → API Reference (autodoc)
    └── examples/
        └── README.md         → User Guides
```

One command generates complete, organized documentation from all of this.

## Configuration Guide

### Minimal Configuration

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
```

That's it! Introligo finds and organizes your READMEs and changelog.

### Recommended Configuration

```yaml
index:
  title: "📚 My Project Documentation"
  description: "Complete documentation hub"

discovery:
  enabled: true
  scan_paths:
    - "."
    - "docs/"
  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true
    markdown_docs: "docs/**/*.md"
  exclude_patterns:
    - "node_modules"
    - ".venv"

sphinx:
  project: "My Project"
  author: "Your Name"
  html_theme: "furo"
  palette: "celin"
```

### Advanced: Mix Auto + Manual

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true

# Manually add API docs and custom sections
modules:
  api:
    title: "📖 API Reference"
    module: "myproject"  # Python autodoc

  architecture:
    title: "🏗️ Architecture"
    file_includes:
      - "docs/design.md"
      - "docs/decisions.md"
```

## Use Cases

### ✅ Open Source Projects
**Perfect for:** Projects with established docs scattered across README files and markdown guides.

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true
```

### ✅ Python Libraries
**Perfect for:** Libraries needing API docs combined with guides.

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    markdown_docs: "docs/**/*.md"

modules:
  api:
    module: "mylib"  # Auto-generates API docs
```

### ✅ Documentation Migration
**Perfect for:** Moving from markdown to Sphinx.

```yaml
discovery:
  enabled: true
  scan_paths: ["."]
  auto_include:
    markdown_docs: "**/*.md"  # Find everything
```

### ✅ Multi-Language Projects
**Perfect for:** C++/Python projects with Doxygen and Sphinx.

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true

doxygen:
  xml_path: "build/doxygen/xml"

modules:
  cpp_api:
    language: cpp
    doxygen_files: ["mylib.h"]
  python_api:
    module: "mylib"
```

## Classic Mode (For Power Users)

If you need complete control over documentation structure:

```yaml
# No discovery - manually define everything
modules:
  getting_started:
    title: "Getting Started"
    file_includes: "README.md"

  user_guide:
    title: "User Guide"
    parent: "getting_started"
    file_includes: "docs/guide.md"

  api:
    title: "API Reference"
    module: "myproject"
```

**When to use Classic Mode:**
- Complex hierarchical requirements
- Precise control needed
- Building docs from scratch
- Custom organization beyond categories

**Most users should use Hub Mode.**

## Installation

### Basic Installation

```bash
pip install PyYAML jinja2
```

### With Sphinx (for building docs)

```bash
pip install PyYAML jinja2 sphinx furo
```

### With C/C++ Support

```bash
pip install PyYAML jinja2 sphinx breathe
sudo apt-get install doxygen  # or: brew install doxygen
```

### With Go Support

Go documentation is extracted automatically when Go is installed:

```bash
pip install PyYAML jinja2 sphinx furo
# Install Go from https://go.dev/dl/ for automatic doc extraction
```

**Note:** Go documentation is extracted using `go doc`. If Go is not installed, Introligo gracefully falls back to providing links to pkg.go.dev.

### Development Installation

```bash
git clone https://github.com/JakubBrzezo/introligo.git
cd introligo
pip install -e .[dev,docs]
```

## Documentation

### Examples

- [Hub Example](examples/hub_project/) - Complete realistic project
- [Python Example](examples/python_project/) - Python autodoc
- [C Example](examples/c_project/) - Doxygen integration
- [Go Example](examples/go_project/) - Go package documentation
- [LaTeX Example](examples/latex_project/) - Math formulas
- [RST Example](examples/rst_project/) - RST includes

### Guides

- [Examples Guide](examples/EXAMPLES.md) - All examples explained
- [Hub Architecture](HUB_ARCHITECTURE.md) - Technical details
- [Migration Guide](#migrating-to-hub-mode) - From Classic to Hub

## Command Line

```bash
# Generate documentation
python -m introligo config.yaml -o output/

# Preview (dry-run)
python -m introligo config.yaml -o output/ --dry-run

# Verbose output
python -m introligo config.yaml -o output/ -v

# Custom template
python -m introligo config.yaml -o output/ -t custom.jinja2

# Strict mode (fail on errors)
python -m introligo config.yaml -o output/ --strict
```

## Migrating to Hub Mode

### From Scattered Docs

If you have READMEs and markdown files:

**Before:** Multiple disconnected files
**After:** One command to unite them

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    markdown_docs: "docs/**/*.md"
```

### From Classic Introligo

If you're using the old YAML approach:

**Before:**
```yaml
modules:
  getting_started:
    title: "Getting Started"
    file_includes: "README.md"
  changelog:
    title: "Changelog"
    file_includes: "CHANGELOG.md"
```

**After:**
```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
```

Much simpler! And you can still add manual modules.

## FAQ

### Q: Do I have to move my documentation files?

**No!** Introligo finds documentation wherever it is. READMEs, guides, and other files can stay in their current locations.

### Q: What if auto-categorization gets it wrong?

Use manual modules to override:

```yaml
discovery:
  enabled: true
  auto_include:
    markdown_docs: "docs/**/*.md"

modules:
  architecture:  # Manually control this
    title: "Architecture"
    file_includes: "docs/architecture.md"
```

### Q: Can I customize the organization?

Yes! Use hybrid mode—auto-discover common files, manually organize complex sections.

### Q: Does it work with existing Sphinx projects?

Yes! Introligo generates RST files that work with any Sphinx setup.

### Q: What about my existing conf.py?

Introligo can auto-generate `conf.py`, but if you have a custom one, just don't enable the `sphinx` section.

## Requirements

- Python 3.8 or higher
- PyYAML >= 6.0
- Jinja2 >= 3.0
- Sphinx >= 4.0 (for building)

**Optional:**
- Breathe >= 4.0 (C/C++ documentation)
- Doxygen (C/C++ documentation)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Running tests
- Code style
- Submitting PRs

## License

Copyright (c) 2025 WT Tech Jakub Brzezowski

Introligo is an open-source component of the Celin Project. Free for any use, commercial or non-commercial.

## Links

- **Documentation:** [Full docs](https://jakubbrzezo.github.io/introligo)
- **Issues:** [GitHub Issues](https://github.com/JakubBrzezo/introligo/issues)
- **Examples:** [`examples/`](examples/)

---

**Made with ❤️ by WT Tech Jakub Brzezowski**

*Part of the [Celin Project](https://github.com/JakubBrzezo) ecosystem*
