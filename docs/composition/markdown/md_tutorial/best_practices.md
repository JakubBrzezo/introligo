This section provides guidelines for effectively using markdown includes in documentation workflows.

## Content Placement

Markdown files are included at the end of generated documentation pages, after all other sections. This positioning is appropriate for:

- **Supplementary documentation**: Detailed guides following the main content
- **Detailed guides**: In-depth tutorials and walkthroughs
- **Contributing guidelines**: Project contribution procedures
- **FAQ sections**: Frequently asked questions

## File Organization

Markdown documentation should be organized with a clear structure:

```text
project/
├── docs/
│   ├── composition/
│   │   ├── introligo_config.yaml
│   │   └── markdown/
│   │       ├── guide1.md
│   │       └── guide2.md
│   ├── user_guides/
│   │   ├── getting_started.md
│   │   └── advanced_usage.md
│   └── conf.py
├── CONTRIBUTING.md
└── README.md
```

### Organization Guidelines

1. **Keep related files together**: Group markdown files by topic
2. **Use descriptive names**: Ensure file purposes are clear from filenames
3. **Maintain consistency**: Apply consistent naming conventions
4. **Separate concerns**: Organize different topics into separate files

## Markdown Format

Markdown content is automatically converted to RST. The following features are supported:

### Supported Features

- **Headers** (H1-H4): Converted to RST section titles
- **Code blocks**: Language syntax highlighting supported
- **Lists**: Bullet points and numbered lists
- **Checklists**: Task lists with checkbox syntax preserved
- **Regular text**: Paragraphs and line breaks
- **Links**: External URLs, internal documentation references, and anchors (see Link Conversion section)
- **Images**: Automatically converted to RST image directives
- **Tables**: Markdown tables converted to RST list-table directives
- **Emojis**: Supported in documentation text

### Conversion Reference

This table itself demonstrates markdown table conversion.

| Markdown | RST Output | Feature |
|----------|------------|---------|
| `# Title` | Title with `====` | Headers |
| `## Heading` | Heading with `----` | Headers |
| `### Subheading` | Subheading with `~~~~` | Headers |
| Code block | `.. code-block::` | Code blocks |
| `- [ ] Task` | `- [ ] Task` | Checklists |
| Links | `` `Link <url>`_ `` | Links |
| Images | `.. image::` | Images |
| Tables | `.. list-table::` | Tables |

## Integration Workflow

### Step 1: Create Markdown Documentation
Write guides, tutorials, and documentation in markdown files.

### Step 2: Configure Introligo
Add `markdown_includes` to the module configuration:

```yaml
modules:
  user_guide:
    title: "User Guide"
    markdown_includes:
      - "markdown/getting_started.md"
      - "markdown/advanced.md"
```

### Step 3: Generate Documentation
Run Introligo to generate RST files with embedded markdown content.

### Step 4: Build with Sphinx
Build the complete documentation with Sphinx.

## Advanced Techniques

### Combining YAML and Markdown
YAML-defined sections can be combined with markdown includes for enhanced flexibility:

```yaml
modules:
  my_module:
    title: "My Module"
    description: "Short description"
    features:
      - "Feature 1"
      - "Feature 2"
    # Add detailed guide from markdown
    markdown_includes: "detailed_guide.md"
```

### Path Resolution
Paths function identically to the `!include` directive, relative to the configuration file:

```yaml
# From docs/composition/config.yaml
markdown_includes: "markdown/guide.md"  # Correct
markdown_includes: "./markdown/guide.md"  # Also valid
markdown_includes: "../../README.md"  # Parent directory navigation
```

### Markdown Simplicity
Focus on well-supported features for optimal conversion results.

### Documentation Preview
Always preview documentation after adding markdown includes to verify proper rendering.

## Documentation Quality Checklist

Before finalizing your documentation:

- [ ] All markdown files use consistent formatting
- [ ] Links are tested and functional
- [ ] Images display correctly with appropriate alt text
- [ ] Code examples are syntax-highlighted properly
- [ ] Tables render correctly in both markdown and RST
- [x] Documentation builds without errors
- [ ] Cross-references between documents work
- [ ] Spelling and grammar have been reviewed
- [ ] Technical accuracy verified by subject matter expert
