Real-world examples of how to use markdown includes effectively.

## 1️⃣ Including Project README

### 🎯 Use Case
Share your project's main README.md in the documentation overview.

### 📝 Configuration
```yaml
modules:
  overview:
    title: "📚 Project Overview"
    description: "Project overview from README"
    markdown_includes: "../../README.md"
```

### ✅ Benefits
- Single source of truth for project information
- Automatically stays up-to-date
- No need to maintain duplicate content

---

## 2️⃣ User Guide Series

### 🎯 Use Case
Create comprehensive user documentation from multiple markdown files.

### 📝 Configuration
```yaml
modules:
  user_guide:
    title: "📖 User Guide"
    description: "Complete user documentation"
    markdown_includes:
      - "markdown/getting_started.md"
      - "markdown/advanced_usage.md"
      - "markdown/troubleshooting.md"
```

### ✅ Benefits
- Organized, modular documentation
- Easy to maintain individual sections
- Clear separation of topics

---

## 3️⃣ API Documentation Enhancement

### 🎯 Use Case
Enhance auto-generated API docs with detailed examples from markdown.

### 📝 Configuration
```yaml
modules:
  api:
    title: "🔧 API Reference"
    module: "myproject.api"
    description: "Complete API documentation"
    # Autodoc generates API reference
    # Markdown adds detailed examples
    markdown_includes: "markdown/api_examples.md"
```

### ✅ Benefits
- Combine automated and manual documentation
- Add context and examples to API reference
- Keep examples separate and maintainable

---

## 4️⃣ Contributing Guidelines

### 🎯 Use Case
Include your CONTRIBUTING.md in the developer documentation.

### 📝 Configuration
```yaml
modules:
  contributing:
    title: "🤝 Contributing"
    description: "How to contribute to this project"
    markdown_includes: "../../CONTRIBUTING.md"
```

### ✅ Benefits
- Single CONTRIBUTING.md for both GitHub/GitLab/Bitbucket and docs
- Always in sync
- Developers see it in documentation too

---

## 5️⃣ Multi-language Documentation

### 🎯 Use Case
Document both Python and C/C++ components in one project.

### 📝 Configuration
```yaml
modules:
  python_api:
    title: "🐍 Python API"
    module: "myproject"
    markdown_includes: "markdown/python_guide.md"

  cpp_api:
    title: "⚡ C++ API"
    language: cpp
    doxygen_files:
      - "mylib.h"
      - "mylib.cpp"
    markdown_includes: "markdown/cpp_guide.md"
```

### ✅ Benefits
- Consistent documentation across languages
- Additional context for each language
- Unified documentation structure

---

## 6️⃣ Tutorial Series

### 🎯 Use Case
Create step-by-step tutorials with markdown files.

### 📝 Configuration
```yaml
modules:
  tutorials:
    title: "🎓 Tutorials"
    description: "Step-by-step learning path"

  tutorial_basics:
    parent: "tutorials"
    title: "1️⃣ Basics"
    markdown_includes: "tutorials/01_basics.md"

  tutorial_advanced:
    parent: "tutorials"
    title: "2️⃣ Advanced"
    markdown_includes: "tutorials/02_advanced.md"
```

### ✅ Benefits
- Numbered, sequential tutorials
- Each tutorial in its own file
- Easy to add new tutorials

---

## 7️⃣ Changelog Integration

### 🎯 Use Case
Include your CHANGELOG.md in the documentation.

### 📝 Configuration
```yaml
modules:
  changelog:
    title: "📋 Changelog"
    description: "Version history and changes"
    markdown_includes: "../../CHANGELOG.md"
```

### ✅ Benefits
- Single changelog file
- Visible in documentation
- Track changes in version control

---

## 8️⃣ FAQ Section

### 🎯 Use Case
Maintain FAQ in markdown, include in documentation.

### 📝 Configuration
```yaml
modules:
  faq:
    title: "❓ FAQ"
    description: "Frequently Asked Questions"
    markdown_includes: "markdown/faq.md"
```

### ✅ Benefits
- Easy to update FAQ
- Searchable in documentation
- Can be maintained by non-developers

---

## 🎯 Choosing the Right Approach

### Use Markdown Includes When:
- ✅ You already have markdown documentation
- ✅ Content needs to be maintained separately
- ✅ Multiple people edit the documentation
- ✅ Want to reuse content across projects

### Use YAML Configuration When:
- ✅ Simple, structured information
- ✅ Close integration with module definitions
- ✅ Automated API documentation
- ✅ Consistent formatting across all modules

### Best of Both Worlds:
- 🌟 Use YAML for structure and metadata
- 🌟 Use markdown includes for detailed content
- 🌟 Combine both for comprehensive documentation!
