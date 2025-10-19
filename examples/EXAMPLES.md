# Introligo Examples

This directory contains example configurations demonstrating various features of Introligo.

## Available Examples

### 1. Python Project (`python_project/`)
Demonstrates documentation for a Python project using Sphinx autodoc.

**Features:**
- Sphinx auto-configuration in YAML
- **AUTO-DETECTED extensions** (autodoc, napoleon, viewcode)
- Autodoc settings for Python modules
- Napoleon extension for Google-style docstrings
- Alabaster theme configuration

**Run:**
```bash
python preview.py --example python_project
```

### 2. C Project (`c_project/`)
Demonstrates documentation for a C library using Doxygen and Breathe.

**Features:**
- Doxygen integration
- **AUTO-DETECTED Breathe extension** (from doxygen_files)
- Breathe configuration for C documentation
- Multiple file documentation

**Run:**
```bash
python preview.py --example c_project
```

### 3. LaTeX Project (`latex_project/`)
Demonstrates including LaTeX mathematical content in documentation.

**Features:**
- LaTeX file inclusion
- **AUTO-DETECTED mathjax extension** (from latex_includes)
- Math directive generation
- Mathematical documentation

**Run:**
```bash
python preview.py --example latex_project
```

### 4. RST Project (`rst_project/`)
Demonstrates including existing reStructuredText files in documentation.

**Features:**
- RST file inclusion (native format, no conversion)
- Single and multiple file inclusion
- Mixed content (RST includes + YAML config)
- Documentation organization
- Team collaboration workflows

**Run:**
```bash
python preview.py --example rst_project
```

### 5. Furo with Celin Palette (`introligo_with_furo_celin.yaml`)
Example configuration using the Furo theme with Celin cosmic color palette.

**Features:**
- Auto-generated conf.py
- Celin color palette (built-in)
- Furo theme configuration
- Git version management
- Intersphinx mapping

**Generate:**
```bash
python -m introligo examples/introligo_with_furo_celin.yaml -o /tmp/test_docs -v
cd /tmp/test_docs
sphinx-build -b html . _build/html
```

### 6. Custom Palette (`introligo_with_custom_palette.yaml`)
Example using the default color palette with Furo theme.

**Features:**
- Default color palette (built-in)
- Simple Sphinx configuration
- Minimal setup example

**Generate:**
```bash
python -m introligo examples/introligo_with_custom_palette.yaml -o /tmp/test_docs -v
```

## Creating Your Own Configuration

### Basic Structure

```yaml
# Basic project info
index:
  title: "My Project Documentation"
  description: "Project description"

generate_index: true

# Sphinx configuration (auto-generates conf.py)
sphinx:
  project: "My Project"
  author: "Your Name"
  copyright_year: "2025"

  html_theme: "furo"  # or "alabaster", "sphinx_rtd_theme", etc.
  palette: "celin"    # "celin", "default", or path to custom palette

  # Extensions are AUTO-DETECTED! Only add custom ones if needed:
  # extensions:
  #   - "sphinx.ext.intersphinx"  # Custom extension only
  # autodoc, napoleon, viewcode are added automatically for Python projects!

# Your documentation modules
modules:
  my_module:
    title: "My Module"
    module: "mypackage.mymodule"  # Python detected → autodoc, napoleon, viewcode added!
    description: "Module description"
```

### With Custom Color Palette

Create a palette file `my_palette.yaml`:

```yaml
name: "My Palette"
description: "Custom colors"

colors:
  primary:
    1: "#0066FF"
    2: "#3385FF"

  neutral:
    1: "#333333"
    2: "#FFFFFF"

light_mode:
  color-brand-primary: "{primary.1}"
  color-background-primary: "{neutral.2}"
  color-foreground-primary: "{neutral.1}"

dark_mode:
  color-brand-primary: "{primary.2}"
  color-background-primary: "{neutral.1}"
  color-foreground-primary: "{neutral.2}"
```

Reference it in your config:
```yaml
sphinx:
  palette: "path/to/my_palette.yaml"
```

## Built-in Palettes

### Celin Palette
Cosmic-inspired colors with deep space theme.

**Colors:**
- Intergalactic Space (dark backgrounds)
- Cosmic Dawn (primary blues)
- Clouds of Uranus (cyan accents)
- Pulsar Light (light backgrounds)
- Aurora Borealis (greens)
- Betelgeuse Flash (oranges)
- Galactic Dust (pinks)
- Meteor Arc (yellows)
- Echo of Mars (reds)

**Use:** `palette: "celin"`

### Default Palette
Clean, simple colors for general documentation.

**Colors:**
- Primary Blue
- Neutral Gray
- Accent Green

**Use:** `palette: "default"`

## Testing Examples

### List all examples
```bash
cd docs
python preview.py --list-examples
```

### Run a specific example
```bash
python preview.py --example python_project
```

### Generate without serving
```bash
python preview.py --example python_project --no-serve
```

### Use custom port
```bash
python preview.py --example python_project --port 8080
```

## Tips

1. **Start simple** - Begin with a basic configuration and add features incrementally
2. **Use built-in palettes** - They're ready to use and look professional
3. **Test locally** - Use `preview.py` for quick iteration
4. **Customize palettes** - Copy a built-in palette and modify it for your brand
5. **Check the docs** - See `docs/sphinx_config_guide.md` for comprehensive configuration reference

## Troubleshooting

### conf.py not generated?
Make sure you have a `sphinx` section in your YAML configuration.

### Colors not working?
Verify your theme supports CSS variables (Furo does, some themes don't).

### Import errors?
Check `project_root` and `add_project_to_path` settings in sphinx config.

### Build fails?
Run with `-v` (verbose) flag to see detailed error messages.

## Contributing Examples

Have a great example configuration? Contributions are welcome!

1. Create a new directory in `examples/`
2. Add `introligo_config.yaml`
3. Add a `README.md` explaining the example
4. Submit a pull request

## More Information

- **Sphinx config guide:** `docs/sphinx_config_guide.md`
- **Color palettes:** `introligo/palettes/`
- **Templates:** `introligo/templates/`
