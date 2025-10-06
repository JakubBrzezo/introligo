Learn how to effectively use markdown includes in your documentation workflow.

## 📍 Content Placement

Markdown files are included at the end of the generated documentation page, after all other sections. This makes them ideal for:

- 📖 **Supplementary documentation** - Add detailed guides after the main content
- 🔍 **Detailed guides** - Deep-dive tutorials and walkthroughs
- 🤝 **Contributing guidelines** - How to contribute to the project
- ❓ **FAQ sections** - Frequently asked questions

## 🗂️ File Organization

Consider organizing your markdown documentation with a clear structure:

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

### 💡 Organization Tips

1. **📁 Keep related files together** - Group markdown files by topic
2. **📝 Use descriptive names** - Make file purposes clear from the name
3. **🔄 Maintain consistency** - Use consistent naming conventions
4. **📊 Separate concerns** - Different topics in different files

## 🎨 Markdown Format

The markdown content is automatically converted to RST. For best results:

### ✅ Supported Markdown Features

- **Headers** (H1-H4) - Converted to RST section titles
- **Code blocks** - With language syntax highlighting
- **Lists** - Bullet points and numbered lists
- **Regular text** - Paragraphs and line breaks
- **Emojis** 😎 - Works perfectly in documentation!

### 🔧 Conversion Details

| Markdown | RST Output |
|----------|------------|
| `# Title` | Title with `====` underline |
| `## Heading` | Heading with `----` underline |
| `### Subheading` | Subheading with `~~~~` underline |
| ` ```python ` | `.. code-block:: python` |

## 🔄 Integration Workflow

### 1️⃣ Create your markdown documentation
Write your guides, tutorials, and documentation in markdown files.

### 2️⃣ Configure Introligo
Add `markdown_includes` to your module configuration:

```yaml
modules:
  user_guide:
    title: "User Guide"
    markdown_includes:
      - "markdown/getting_started.md"
      - "markdown/advanced.md"
```

### 3️⃣ Generate documentation
Run Introligo to generate RST files with embedded markdown content.

### 4️⃣ Build with Sphinx
Build your complete documentation with Sphinx as usual.

## 🎓 Pro Tips

### 💎 Tip 1: Mix and Match
Combine YAML-defined sections with markdown includes for maximum flexibility:

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

### 💎 Tip 2: Path Resolution
Paths work just like `!include` directive - relative to the config file:

```yaml
# From docs/composition/config.yaml
markdown_includes: "markdown/guide.md"  # ✅ Correct
markdown_includes: "./markdown/guide.md"  # ✅ Also works
markdown_includes: "../../README.md"  # ✅ Go up directories
```

### 💎 Tip 3: Keep Markdown Simple
Focus on well-supported features for best conversion results.

### 💎 Tip 4: Preview Before Commit
Always preview your documentation after adding markdown includes to ensure proper rendering.
