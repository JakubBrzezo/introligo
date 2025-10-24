# Introligo Documentation Composition

This directory contains the modular configuration files for Introligo's own documentation.

## Structure

```
composition/
├── introligo_config_new.yaml          # Main config with !include directives
├── modules/                            # Module configuration files
│   ├── getting_started/
│   │   ├── _main.yaml                 # Getting Started category
│   │   ├── installation.yaml          # Installation guide
│   │   └── quickstart.yaml            # Quick start guide
│   ├── user_guide/
│   │   └── _main.yaml                 # User Guide category
│   ├── about/
│   │   ├── _main.yaml                 # About category
│   │   ├── license.yaml               # License information
│   │   └── changelog.yaml             # Changelog (includes CHANGELOG.md)
│   ├── api/
│   │   └── (API reference modules)
│   └── examples/
│       └── (Example modules)
└── markdown/                           # Markdown content files
    ├── md_tutorial/
    ├── sphinx_tutorial/
    └── devcontainer_tutorial/
```

## Key Features

### Modular Configuration

The new structure uses the `!include` directive to split the large configuration into manageable files:

- Each section (Getting Started, User Guide, About, etc.) has its own directory
- Individual pages are defined in separate YAML files
- The main `introligo_config_new.yaml` includes these files

### Benefits

1. **Better Organization** - Related documentation is grouped together
2. **Easier Maintenance** - Edit specific sections without navigating a 1800+ line file
3. **Reusability** - Module configurations can be reused or shared
4. **Collaboration** - Multiple people can work on different sections simultaneously
5. **Version Control** - Cleaner diffs when changes are made

### File Naming Convention

- `_main.yaml` - Main category/section definition
- Other files - Named after the module they define (e.g., `installation.yaml`, `license.yaml`)

## Usage

### Generate Documentation

```bash
# From the introligo root directory
python -m introligo docs/composition/introligo_config_new.yaml -o docs

# Or use the preview script
python docs/preview.py
```

### Adding New Modules

1. Create a new YAML file in the appropriate `modules/` subdirectory
2. Add an `!include` directive in `introligo_config_new.yaml`:

```yaml
modules:
  my_new_module: !include modules/user_guide/my_new_module.yaml
```

### Module File Template

```yaml
# Module Description
# Copyright (c) 2025 WT Tech Jakub Brzezowski

parent: "user_guide"  # Optional: parent category
title: "Module Title"
description: "Brief description"
overview: |
  Detailed overview of the module

features:
  - "Feature 1"
  - "Feature 2"

usage_examples:
  - title: "Example Title"
    description: "Example description"
    language: "python"
    code: |
      # Example code
```

## Migration Notes

The original `introligo_config.yaml` (1871 lines) has been split into:
- Main config: `introligo_config_new.yaml` (~270 lines)
- Module files: Multiple small, focused files (~20-80 lines each)

This makes the configuration:
- 90% easier to navigate
- 100% more maintainable
- Self-documenting through file organization

## Future Enhancements

Consider moving these to separate files:
- Full User Guide modules (configuration, Python docs, C++ docs, etc.)
- Examples section
- API reference modules

Each can follow the same pattern demonstrated in the Getting Started and About sections.
