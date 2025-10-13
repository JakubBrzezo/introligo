## What is Sphinx?

**Sphinx** is a powerful documentation generator that converts reStructuredText (RST) files into beautiful HTML, PDF, and other formats. It's the standard tool for Python documentation and is used by thousands of projects.

**Introligo** makes Sphinx even easier by:
- Auto-generating complex RST structures from simple YAML
- Automatically creating `conf.py` configuration files
- Managing themes and color palettes
- Organizing hierarchical documentation

## Why Use Introligo with Sphinx?

### Traditional Sphinx Workflow
```bash
1. Write RST files manually
2. Create and maintain conf.py
3. Manage toctree directives
4. Keep navigation in sync
5. Update theme configuration
```

### Introligo Workflow
```bash
1. Write simple YAML configuration
2. Run: python -m introligo config.yaml -o docs
3. Run: sphinx-build -b html docs docs/_build/html
```

**That's it!** Introligo handles:
- ✅ RST file generation
- ✅ conf.py creation
- ✅ Theme configuration
- ✅ Navigation structure
- ✅ Color palette management

## What You'll Learn

In this tutorial, you'll learn how to:

1. **Set Up Sphinx with Introligo**
   - Install dependencies
   - Create your first configuration
   - Generate documentation

2. **Configure Sphinx Settings**
   - Project information
   - Extensions and features
   - Build options

3. **Work with Themes and Colors**
   - Choose and configure themes
   - Use built-in color palettes
   - Create custom palettes

4. **Advanced Features**
   - Autodoc for Python API docs
   - Breathe for C/C++ documentation
   - Custom extensions
   - Multi-language support

## Prerequisites

Before starting, you should have:
- Python 3.8 or higher installed
- Basic understanding of YAML syntax
- Familiarity with command-line tools
- (Optional) Knowledge of reStructuredText

## Installation

Install Introligo and Sphinx:

```bash
# Install required packages
pip install PyYAML jinja2 sphinx furo

# Optional: For C/C++ documentation
pip install breathe
```

## Your First Documentation

Let's create a minimal documentation project:

### Step 1: Create Configuration

Create `introligo_config.yaml`:

```yaml
index:
  title: "My Project Documentation"
  description: "A simple documentation project"

generate_index: true

sphinx:
  project: "My Project"
  author: "Your Name"
  html_theme: "furo"
  palette: "celin"

  extensions:
    - "sphinx.ext.autodoc"

modules:
  getting_started:
    title: "Getting Started"
    description: "Introduction to my project"
    overview: |
      Welcome to my project! This documentation will help you get started.
```

### Step 2: Generate Documentation

```bash
# Generate RST files and conf.py
python -m introligo introligo_config.yaml -o docs

# Build HTML
cd docs
sphinx-build -b html . _build/html
```

### Step 3: View Your Documentation

```bash
# Serve locally
python -m http.server 8000 --directory _build/html
```

Open http://localhost:8000 in your browser!

## What Just Happened?

When you ran Introligo:

1. **Generated RST files** - Created structured documentation pages
2. **Created conf.py** - Sphinx configuration with your settings
3. **Applied Celin palette** - Beautiful cosmic colors automatically configured
4. **Built navigation** - Hierarchical structure with toctrees

When you ran Sphinx:

1. **Processed RST files** - Converted to HTML
2. **Applied Furo theme** - Modern, responsive design
3. **Added colors** - Your chosen palette (Celin)
4. **Generated search** - Full-text search functionality

## Next Steps

Now that you have basic documentation working:

1. **Explore Themes** - Try different Sphinx themes
2. **Add Content** - Create more documentation pages
3. **Customize Colors** - Use or create color palettes
4. **Enable Features** - Add extensions like autodoc

Continue to the next section to learn more about Sphinx configuration!
