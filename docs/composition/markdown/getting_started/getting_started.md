# Getting Started with Introligo

**5-minute guide to unified documentation.**

## What You'll Build

By the end of this guide, you'll have:
- ✅ All your docs automatically discovered
- ✅ Professional Sphinx documentation site
- ✅ Beautiful theme with search
- ✅ Automatic navigation
- ✅ One command to rebuild everything

## Prerequisites

- Python 3.8+
- A project with some documentation (READMEs, markdown files, etc.)

## Step 1: Install (1 minute)

```bash
pip install PyYAML jinja2 sphinx furo
```

That's all you need!

## Step 2: Create Configuration (2 minutes)

Create `introligo_config.yaml` in your project root:

```yaml
# Minimal configuration - let Introligo do the work!
index:
  title: "My Project Docs"

discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
    markdown_docs: "docs/**/*.md"

sphinx:
  project: "My Project"
  html_theme: "furo"
```

**That's it!** This finds all your READMEs, CHANGELOG, and markdown files.

## Step 3: Generate Documentation (2 minutes)

```bash
# Generate docs
python -m introligo introligo_config.yaml -o my_docs -v

# Build with Sphinx
cd my_docs
sphinx-build -b html . _build/html

# View it!
python -m http.server 8000 --directory _build/html
```

Open http://localhost:8000 in your browser. **Done!** 🎉

## What Just Happened?

1. **Discovery**: Introligo scanned your project
2. **Organization**: Docs were categorized automatically
3. **Generation**: RST files were created
4. **Building**: Sphinx created the HTML site

All from one simple config file!

## Next Steps

### Add More Documentation Types

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
    contributing: true  # Add CONTRIBUTING.md
    license: true       # Add LICENSE
    markdown_docs: "docs/**/*.md"
```

### Add API Documentation

For Python projects:

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true

modules:
  api:
    title: "API Reference"
    module: "myproject"  # Your package name
```

### Customize Theme

```yaml
sphinx:
  project: "My Project"
  html_theme: "furo"
  palette: "celin"  # Beautiful cosmic colors!

  html_theme_options:
    sidebar_hide_name: false
```

### Exclude Unwanted Files

```yaml
discovery:
  enabled: true
  auto_include:
    markdown_docs: "docs/**/*.md"

  exclude_patterns:
    - "node_modules"
    - ".venv"
    - "build"
    - "test_*"
```

## Common Patterns

### Pattern 1: Simple Open Source Project

```yaml
index:
  title: "📚 My Library Docs"

discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true
    contributing: true
    license: true

modules:
  api:
    module: "mylib"

sphinx:
  project: "MyLib"
  html_theme: "furo"
  palette: "celin"
```

### Pattern 2: Documentation-Heavy Project

```yaml
index:
  title: "Complete Docs"

discovery:
  enabled: true
  scan_paths:
    - "."
    - "docs/"
    - "guides/"
  auto_include:
    readme: true
    changelog: true
    markdown_docs: "**/*.md"

sphinx:
  project: "My Project"
  html_theme: "furo"
```

### Pattern 3: API-Focused Library

```yaml
index:
  title: "API Documentation"

discovery:
  enabled: true
  auto_include:
    readme: true
    changelog: true

modules:
  api:
    title: "API Reference"
    module: "mypackage"

  examples:
    title: "Examples"
    file_includes:
      - "examples/basic.md"
      - "examples/advanced.md"

sphinx:
  project: "MyPackage"
  html_theme: "furo"
```

## Troubleshooting

### "No module named 'introligo'"

Install in development mode:
```bash
pip install -e .
```

Or use full path:
```bash
python -m introligo.introligo config.yaml -o docs
```

### "No modules found"

Check your `discovery` section:
```yaml
discovery:
  enabled: true  # Make sure this is true!
  auto_include:
    readme: true  # At least one should be true
```

### Docs not appearing

Run with verbose output to see what's discovered:
```bash
python -m introligo config.yaml -o docs -v
```

Look for lines like:
```
INFO: 📄 Found README: README.md
INFO: 📅 Found CHANGELOG: CHANGELOG.md
```

### Wrong categorization

Override with manual modules:
```yaml
discovery:
  enabled: true
  auto_include:
    markdown_docs: "docs/**/*.md"

modules:
  my_guide:  # Manually control this one
    title: "Special Guide"
    file_includes: "docs/special.md"
```

## Tips for Success

### 1. Start Small

Begin with just READMEs:
```yaml
discovery:
  enabled: true
  auto_include:
    readme: true
```

Then add more types incrementally.

### 2. Use Verbose Mode

Always use `-v` while learning:
```bash
python -m introligo config.yaml -o docs -v
```

You'll see exactly what's being discovered and categorized.

### 3. Preview Before Building

Use dry-run to see what would be generated:
```bash
python -m introligo config.yaml -o docs --dry-run
```

### 4. Keep Docs Where They Are

Don't reorganize your docs for Introligo. It finds them wherever they are!

### 5. Mix Auto and Manual

Use discovery for common files, manual modules for special cases:

```yaml
discovery:
  enabled: true
  auto_include:
    readme: true

modules:
  architecture:  # Special case
    title: "Architecture"
    file_includes: "docs/architecture.md"
```

## What's Next?

Now that you have basic docs working:

1. **Explore Examples**: Check [`examples/`](examples/) for real-world configs
2. **Read the Guide**: See [EXAMPLES.md](examples/EXAMPLES.md) for detailed patterns
3. **Customize Theme**: Try different palettes and themes
4. **Preview Themes**: Use `python docs/preview.py --motive <theme>` to test different color palettes
5. **Add API Docs**: Include autodoc for your code
6. **Share**: Publish to Read the Docs or GitHub Pages

## Need Help?

- **Examples**: [`examples/`](examples/) directory
- **Issues**: [GitHub Issues](https://github.com/JakubBrzezo/introligo/issues)
- **Architecture**: [HUB_ARCHITECTURE.md](HUB_ARCHITECTURE.md) for technical details

---

**Ready to unite your docs?** Start with the minimal config above and build from there! 🚀
