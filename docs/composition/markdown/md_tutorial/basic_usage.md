This section demonstrates the markdown inclusion feature with practical examples.

## 📚 Including Multiple Markdown Files

You can include multiple markdown files in your module documentation:

```yaml
# Include multiple markdown files
modules:
  my_module:
    title: "My Module"
    description: "Module with markdown documentation"
    module: "myproject.my_module"

    # Include markdown files
    markdown_includes:
      - "docs/user_guide.md"
      - "docs/api_reference.md"
      - "CONTRIBUTING.md"
```

## 📄 Single Markdown File

For simpler cases, use a single file:

```yaml
# Include single file (string instead of list)
modules:
  my_module:
    title: "My Module"
    markdown_includes: "README.md"
```

## 🔗 Relative Paths

All paths are resolved relative to the configuration file:

```yaml
# Config file at: docs/composition/introligo_config.yaml
modules:
  my_module:
    title: "My Module"
    # Include from project root
    markdown_includes:
      - "../../README.md"
      - "../../docs/guides/setup.md"
```

## ✨ Why Use Markdown Includes?

### 🎯 Benefits

- **Reuse existing documentation** - Include your README.md and other markdown files directly
- **DRY principle** - Don't duplicate documentation across formats
- **Easy maintenance** - Update once, reflect everywhere
- **Version control friendly** - Markdown files are easy to review in pull requests
- **Familiar format** - Write in markdown, generate RST documentation

### 🚀 Perfect For

- Project overviews and README files
- Detailed user guides and tutorials
- Contributing guidelines
- Changelog and release notes
- FAQ sections
