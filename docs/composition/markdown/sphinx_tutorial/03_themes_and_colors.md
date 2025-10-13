## Choosing a Sphinx Theme

Sphinx themes control how your documentation looks. Introligo works with any Sphinx theme and makes configuration easy.

## Popular Themes

### Furo (Recommended)

Modern, clean, responsive design with excellent color customization.

```yaml
sphinx:
  html_theme: "furo"
  palette: "celin"  # or "default"
```

**Features:**
- Beautiful out of the box
- Dark mode support
- Mobile-friendly
- Full CSS variable support for colors

**Install:**
```bash
pip install furo
```

### Alabaster

Simple, classic Sphinx theme. Lightweight and clean.

```yaml
sphinx:
  html_theme: "alabaster"
  html_theme_options:
    description: "Project description"
    github_user: "username"
    github_repo: "repository"
```

**Features:**
- Minimalist design
- Sidebar navigation
- Built into Sphinx

**Install:** Already included with Sphinx

### Read the Docs Theme

The classic ReadTheDocs appearance.

```yaml
sphinx:
  html_theme: "sphinx_rtd_theme"
```

**Features:**
- Familiar interface
- Good for large projects
- Collapsible sidebar

**Install:**
```bash
pip install sphinx-rtd-theme
```

### Book Theme

Modern book-like design, great for narratives.

```yaml
sphinx:
  html_theme: "sphinx_book_theme"
```

**Features:**
- Beautiful typography
- Margin notes
- Perfect for tutorials

**Install:**
```bash
pip install sphinx-book-theme
```

## Color Palettes

Introligo includes a powerful color palette system. Instead of manually configuring colors, use pre-made palettes or create your own.

### Built-in Palettes

#### Celin Palette - Cosmic Theme

Inspired by space and cosmic phenomena. Perfect for technical documentation.

```yaml
sphinx:
  html_theme: "furo"
  palette: "celin"
```

**Colors:**
- **Intergalactic Space** - Deep dark backgrounds
- **Cosmic Dawn** - Bright blue primary colors
- **Clouds of Uranus** - Cyan accents
- **Pulsar Light** - Light backgrounds
- **Aurora Borealis** - Green highlights
- **Betelgeuse Flash** - Orange warnings
- **Galactic Dust** - Pink/purple tones
- **Meteor Arc** - Yellow accents
- **Echo of Mars** - Red alerts

**Both light and dark modes included!**

#### Default Palette - Clean and Simple

Professional, neutral colors suitable for any project.

```yaml
sphinx:
  html_theme: "furo"
  palette: "default"
```

**Colors:**
- **Primary Blue** - Links and accents
- **Neutral Gray** - Backgrounds and text
- **Accent Green** - Success states

### Creating Custom Palettes

Create your own color palette in a YAML file:

**my_palette.yaml:**
```yaml
name: "My Company Palette"
description: "Brand colors for documentation"

# Define color groups with shades
colors:
  brand_blue:
    1: "#003366"  # Dark
    2: "#0066CC"  # Medium
    3: "#3399FF"  # Light

  brand_gray:
    1: "#1A1A1A"  # Dark
    2: "#808080"  # Medium
    3: "#F5F5F5"  # Light
    4: "#FFFFFF"  # White

  brand_green:
    1: "#00AA00"
    2: "#00FF00"

# Light mode theme mapping
light_mode:
  # Brand colors
  color-brand-primary: "{brand_blue.2}"
  color-brand-content: "{brand_blue.3}"

  # Backgrounds
  color-background-primary: "{brand_gray.4}"
  color-background-secondary: "{brand_gray.3}"

  # Text
  color-foreground-primary: "{brand_gray.1}"
  color-foreground-secondary: "{brand_gray.2}"

  # Sidebar
  color-sidebar-background: "{brand_gray.3}"
  color-sidebar-link-text: "{brand_gray.1}"
  color-sidebar-item-background--current: "{brand_blue.2}"

  # Links
  color-link: "{brand_blue.2}"
  color-link--hover: "{brand_blue.3}"

  # Code
  color-inline-code-background: "{brand_gray.3}"
  color-inline-code-foreground: "{brand_gray.1}"

# Dark mode theme mapping
dark_mode:
  # Brand colors
  color-brand-primary: "{brand_blue.3}"
  color-brand-content: "{brand_blue.3}"

  # Backgrounds (inverted)
  color-background-primary: "{brand_gray.1}"
  color-background-secondary: "{brand_gray.2}"

  # Text (inverted)
  color-foreground-primary: "{brand_gray.3}"
  color-foreground-secondary: "{brand_gray.4}"

  # Sidebar
  color-sidebar-background: "{brand_gray.2}"
  color-sidebar-link-text: "{brand_gray.3}"
  color-sidebar-item-background--current: "{brand_blue.2}"

  # Links
  color-link: "{brand_blue.3}"
  color-link--hover: "{brand_green.2}"

  # Code
  color-inline-code-background: "{brand_gray.2}"
  color-inline-code-foreground: "{brand_gray.3}"
```

Use your custom palette:

```yaml
sphinx:
  html_theme: "furo"
  palette: "path/to/my_palette.yaml"
```

### Color Reference System

Colors use a reference format: `{color_group.shade}`

**Example:**
- `{brand_blue.2}` → `#0066CC`
- `{brand_gray.4}` → `#FFFFFF`

This makes it easy to:
- Maintain consistent colors
- Create variations (light/dark modes)
- Update colors in one place

## Available Theme Variables (Furo)

Customize every aspect of your theme:

### Brand Colors
- `color-brand-primary` - Primary brand color
- `color-brand-content` - Content accent color

### Backgrounds
- `color-background-primary` - Main background
- `color-background-secondary` - Secondary background
- `color-background-hover` - Hover states
- `color-background-border` - Border colors

### Foreground/Text
- `color-foreground-primary` - Main text
- `color-foreground-secondary` - Secondary text
- `color-foreground-muted` - Muted text
- `color-foreground-border` - Text borders

### Sidebar
- `color-sidebar-background` - Sidebar background
- `color-sidebar-background-border` - Sidebar border
- `color-sidebar-item-background--current` - Current page
- `color-sidebar-item-background--hover` - Hover state
- `color-sidebar-link-text` - Link text color
- `color-sidebar-link-text--top-level` - Top level links

### Links
- `color-link` - Link color
- `color-link--hover` - Link hover color
- `color-link-underline` - Link underline
- `color-link-underline--hover` - Hover underline

### Code
- `color-inline-code-background` - Code background
- `color-inline-code-foreground` - Code text
- `color-highlighted-background` - Highlighted code
- `color-highlighted-text` - Highlighted text

### UI Elements
- `color-header-background` - Header background
- `color-header-border` - Header border
- `color-header-text` - Header text
- `color-admonition-background` - Note boxes
- `color-admonition-title-background` - Note titles
- `color-admonition-title` - Note title text

## Theme Options

Configure theme-specific options:

### Furo Options

```yaml
sphinx:
  html_theme: "furo"
  palette: "celin"

  html_theme_options:
    sidebar_hide_name: false
    navigation_with_keys: true
    top_of_page_button: "edit"
```

### Alabaster Options

```yaml
sphinx:
  html_theme: "alabaster"

  html_theme_options:
    description: "My project description"
    github_user: "username"
    github_repo: "repository"
    github_button: true
    github_type: "star"
    fixed_sidebar: true
```

### RTD Theme Options

```yaml
sphinx:
  html_theme: "sphinx_rtd_theme"

  html_theme_options:
    logo_only: false
    display_version: true
    prev_next_buttons_location: "bottom"
    style_external_links: true
    collapse_navigation: false
    sticky_navigation: true
    navigation_depth: 4
```

## Logo and Favicon

Add branding to your documentation:

```yaml
sphinx:
  html_theme: "furo"
  html_logo: "str(PROJECT_ROOT / '_assets' / 'logo.png')"
  html_favicon: "str(PROJECT_ROOT / '_assets' / 'favicon.ico')"
```

**Directory structure:**
```
myproject/
├── _assets/
│   ├── logo.png
│   └── favicon.ico
└── docs/
    ├── introligo_config.yaml
    └── conf.py (generated)
```

## Static Files

Include custom CSS, JavaScript, or images:

```yaml
sphinx:
  html_static_path: ["_static"]
```

Create custom CSS:

**docs/_static/custom.css:**
```css
/* Override or extend theme styles */
.custom-class {
    color: #FF0000;
}
```

Reference in configuration:

```yaml
sphinx:
  html_static_path: ["_static"]
  html_css_files:
    - "custom.css"
```

## Example: Complete Theme Configuration

```yaml
sphinx:
  project: "My Project"
  author: "Development Team"

  # Furo theme with Celin colors
  html_theme: "furo"
  palette: "celin"

  # Branding
  html_title: "My Project Documentation"
  html_logo: "str(PROJECT_ROOT / '_assets' / 'logo.png')"
  html_favicon: "str(PROJECT_ROOT / '_assets' / 'favicon.ico')"

  # Theme options
  html_theme_options:
    sidebar_hide_name: false
    navigation_with_keys: true

  # Static files
  html_static_path: ["_static"]
  html_css_files:
    - "custom.css"
```

## Testing Your Theme

After generating documentation:

```bash
# Generate with Introligo
python -m introligo config.yaml -o docs -v

# Build HTML
cd docs
sphinx-build -b html . _build/html

# Serve and test
python -m http.server 8000 --directory _build/html
```

Open http://localhost:8000 and check:
- ✅ Colors look good in light mode
- ✅ Colors look good in dark mode
- ✅ Logo appears correctly
- ✅ Navigation is clear
- ✅ Code blocks are readable
- ✅ Mobile layout works

## Tips for Great-Looking Docs

1. **Use a modern theme** - Furo or Book theme
2. **Enable dark mode** - Use palettes with both modes
3. **Add a logo** - Branding makes it professional
4. **Choose readable colors** - Test contrast
5. **Keep it consistent** - Use color palettes
6. **Test on mobile** - Ensure responsive design

## Troubleshooting

### Colors not applying?
- Check that your theme supports CSS variables
- Furo fully supports color customization
- Alabaster has limited support
- RTD theme doesn't support CSS variable customization

### Theme not found?
```bash
pip install theme-package-name
```

### Logo not showing?
- Check file path relative to project root
- Use `str(PROJECT_ROOT / ...)` syntax
- Verify file exists

### Dark mode not working?
- Ensure you defined `dark_mode` in your palette
- Check that your theme supports dark mode
- Furo has excellent dark mode support

## Next Steps

Learn about:
- **Advanced Features** - Extensions and integrations
- **Autodoc** - Automatic API documentation
- **Custom Extensions** - Add your own features
