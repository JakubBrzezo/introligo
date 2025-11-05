# Language Support Overview

Introligo supports automatic API documentation extraction for multiple programming languages, each with optimized integration for the best documentation experience.

## Supported Languages

### Python

**Extraction Tool:** Sphinx autodoc
**Complexity:** ★☆☆☆☆ (Simple)
**Features:** ★★★★★ (Excellent)

- Zero-configuration autodoc integration
- Multiple docstring styles (Google, NumPy, Sphinx)
- Type hint support
- Automatic inheritance trees
- Source code links

[Python Documentation Guide →](python_language_support.md)

### C/C++

**Extraction Tool:** Doxygen + Breathe
**Complexity:** ★★★☆☆ (Moderate)
**Features:** ★★★★★ (Excellent)

- Industry-standard Doxygen integration
- Full C++ features (templates, namespaces, inheritance)
- Rich documentation with diagrams
- Multi-file support
- Automatic Breathe configuration

[C/C++ Documentation Guide →](cc_language_support.md)

### Go

**Extraction Tool:** go doc + custom parser
**Complexity:** ★★☆☆☆ (Easy)
**Features:** ★★★☆☆ (Good)

- Automatic extraction via `go doc`
- RST conversion
- Graceful fallback without Go
- Manual documentation option
- Multi-package support

[Go Documentation Guide →](go_language_support.md)

### Java

**Extraction Tool:** Source parser + Javadoc converter
**Complexity:** ★★☆☆☆ (Easy)
**Features:** ★★★★☆ (Very Good)

- Automatic extraction from Java source files
- Full Javadoc tag support (@param, @return, @throws)
- No external tools required
- Package and file-level documentation
- Maven/Gradle project support

[Java Documentation Guide →](java_language_support.md)

### Rust

**Extraction Tool:** cargo doc + source parser
**Complexity:** ★★☆☆☆ (Easy)
**Features:** ★★★★☆ (Very Good)

- Automatic extraction via `cargo doc`
- RST conversion from doc comments
- Graceful fallback without Cargo
- Manual documentation option
- Multi-crate support

[Rust Documentation Guide →](rust_language_support.md)

### Protocol Buffers (Protobuf)

**Extraction Tool:** Direct source parser
**Complexity:** ★★☆☆☆ (Easy)
**Features:** ★★★★☆ (Very Good)

- Automatic extraction from .proto source files
- No external tools required (works without protoc)
- AsyncAPI validation keywords support (@Min, @Max, @Pattern, etc.)
- Message, enum, and service documentation
- gRPC API documentation
- Multiple comment styles (inline and block)

[Protocol Buffers Documentation Guide →](protobuf_language_support.md)

### LaTeX / Mathematics

**Extraction Tool:** MathJax
**Complexity:** ★☆☆☆☆ (Simple)
**Features:** ★★★★☆ (Very Good)

- Inline and block equations
- External LaTeX file inclusion
- Full LaTeX math syntax
- Numbered equations with cross-references
- Automatic MathJax configuration

[LaTeX/Math Documentation Guide →](latex_support.md)

## Quick Comparison

| Language | Setup | Auto-Extract | External Tool | Build Time |
|----------|-------|--------------|---------------|------------|
| **Python** | Minimal | ✅ Yes | No | Fast |
| **C/C++** | Moderate | ✅ Yes | Doxygen | Slow |
| **Go** | Minimal | ✅ Yes* | Go (optional) | Fast |
| **Java** | Minimal | ✅ Yes | No | Fast |
| **Rust** | Minimal | ✅ Yes* | Cargo (optional) | Moderate |
| **Protobuf** | Minimal | ✅ Yes | No | Fast |
| **LaTeX** | Minimal | Manual | No | Fast |

*Go extraction requires Go to be installed; gracefully falls back to manual docs
*Rust extraction requires Cargo to be installed; gracefully falls back to manual docs

## Features by Language

### Documentation Quality

| Feature | Python | C/C++ | Go | Java | Rust | Protobuf | LaTeX |
|---------|--------|-------|-----|------|------|----------|-------|
| Function Docs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| Class Docs | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | N/A |
| Type Info | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| Examples | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cross-refs | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ |
| Diagrams | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ⚠️ |

### Configuration Complexity

| Aspect | Python | C/C++ | Go | Java | Rust | Protobuf | LaTeX |
|--------|--------|-------|-----|------|------|----------|-------|
| Initial Setup | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| Learning Curve | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| Maintenance | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ |

### Integration Method

**Python:**
```yaml
modules:
  my_module:
    module: "mypackage.mymodule"  # That's it!
```

**C/C++:**
```yaml
doxygen:
  xml_path: "doxygen/xml"
  project_name: "myproject"

modules:
  my_api:
    language: cpp
    doxygen_file: "api.h"
```

**Go:**
```yaml
modules:
  my_package:
    language: go
    godoc_package: "github.com/user/pkg"
    godoc_path: "."
```

**Java:**
```yaml
modules:
  my_package:
    language: java
    java_package: "com.example.mypackage"
    java_source_path: "src/main/java"
```

**Rust:**
```yaml
modules:
  my_crate:
    language: rust
    rustdoc_crate: "my_crate"
    rustdoc_path: "."
```

**Protobuf:**
```yaml
modules:
  my_api:
    language: protobuf
    proto_path: "protos"
```

**LaTeX:**
```yaml
modules:
  equations:
    latex_includes:
      - "math/equations.tex"
```

## Choosing the Right Approach

### For Python Projects

✅ **Use Python support** if:
- You have Python source code with docstrings
- You want automatic API extraction
- You need type hint documentation
- You want zero-configuration setup

### For C/C++ Projects

✅ **Use C/C++ support** if:
- You have C/C++ source with Doxygen comments
- You need comprehensive C++ feature support
- You can run Doxygen as part of your build
- You want rich documentation with diagrams

### For Go Projects

✅ **Use Go support** if:
- You have Go packages with godoc comments
- You want automatic extraction (when Go is available)
- You need fallback for environments without Go
- You want simple, clean documentation

### For Java Projects

✅ **Use Java support** if:
- You have Java source files with Javadoc comments
- You want automatic extraction without external tools
- You need Maven/Gradle project documentation
- You want full Javadoc tag support (@param, @return, @throws)
- You can provide source files to the documentation build

### For Protocol Buffers Projects

✅ **Use Protobuf support** if:
- You have .proto files defining gRPC services or message formats
- You want to document API contracts and message schemas
- You need AsyncAPI validation keywords (@Min, @Max, @Pattern)
- You want documentation without requiring protoc
- You need to document microservice APIs

### For Mathematical Content

✅ **Use LaTeX support** if:
- You need mathematical equations
- You want inline or block formulas
- You have external LaTeX files
- You need numbered, cross-referenced equations

## Multi-Language Projects

Introligo handles mixed-language projects seamlessly:

```yaml
modules:
  # Python API
  python_api:
    title: "Python API"
    module: "myproject.api"

  # C++ Core
  cpp_core:
    title: "C++ Core"
    language: cpp
    doxygen_file: "core.h"

  # Go Services
  go_services:
    title: "Go Services"
    language: go
    godoc_package: "github.com/org/services"

  # Java Backend
  java_backend:
    title: "Java Backend"
    language: java
    java_package: "com.myproject.backend"
    java_source_path: "backend/src/main/java"

  # Protobuf API
  protobuf_api:
    title: "Protobuf API"
    language: protobuf
    proto_path: "proto"

  # Mathematical Models
  math_models:
    title: "Mathematical Models"
    latex_includes:
      - "models/equations.tex"
```

## Auto-Configuration

Introligo automatically configures Sphinx extensions based on detected languages:

**Detected Python module** → Adds `sphinx.ext.autodoc`, `sphinx.ext.napoleon`, `sphinx.ext.viewcode`

**Detected C/C++ doxygen** → Adds `breathe`

**Detected Go godoc** → Logs detection (no extension needed)

**Detected Java package** → Logs detection (no extension needed)

**Detected Protobuf** → Logs detection (no extension needed)

**Detected LaTeX includes** → Adds `sphinx.ext.mathjax`

## Best Practices

### 1. Organize by Language

```yaml
modules:
  api_reference:
    title: "API Reference"

  python_api:
    parent: "api_reference"
    title: "Python API"
    # Python modules here

  cpp_api:
    parent: "api_reference"
    title: "C++ API"
    # C++ modules here
```

### 2. Use Consistent Style

- **Python**: Google or NumPy docstring style
- **C/C++**: JavaDoc style Doxygen comments
- **Go**: Standard godoc conventions
- **LaTeX**: Consistent notation throughout

### 3. Combine with Narrative Docs

Every language supports adding:
- `overview`: High-level description
- `usage_examples`: Code examples
- `features`: Bullet points
- `notes`: Additional information

### 4. Test Documentation Build

```bash
# Generate Introligo RST
python -m introligo config.yaml -o docs

# Build with Sphinx
cd docs && sphinx-build -b html . _build/html
```

## Common Workflows

### Python-Only Project

```bash
# Simple setup
pip install sphinx furo

# Create config
cat > introligo_config.yaml << EOF
sphinx:
  project: "My Project"
  html_theme: "furo"

modules:
  api:
    module: "myproject"
    title: "API"
EOF

# Generate and build
python -m introligo introligo_config.yaml -o docs
cd docs && sphinx-build -b html . _build/html
```

### C++ with Python Bindings

```bash
# Install requirements
pip install sphinx breathe furo
sudo apt-get install doxygen

# Run Doxygen first
doxygen Doxyfile

# Then Introligo + Sphinx
python -m introligo config.yaml -o docs
cd docs && sphinx-build -b html . _build/html
```

### Multi-Language Microservices

```yaml
modules:
  services:
    title: "Services"

  python_service:
    parent: "services"
    module: "services.python"
    title: "Python Service"

  java_service:
    parent: "services"
    language: java
    java_package: "com.org.javaservice"
    java_source_path: "java-service/src/main/java"
    title: "Java Service"

  go_service:
    parent: "services"
    language: go
    godoc_package: "github.com/org/go-service"
    title: "Go Service"

  protobuf_api:
    parent: "services"
    language: protobuf
    proto_path: "proto"
    title: "gRPC API Definitions"

  cpp_lib:
    parent: "services"
    language: cpp
    doxygen_file: "lib.h"
    title: "C++ Library"
```

## Troubleshooting

### Python Import Errors

**Solution:** Add project to path:
```yaml
sphinx:
  add_project_to_path: true
  project_root: ".."
```

### Doxygen XML Not Found

**Solution:** Verify paths:
```bash
ls doxygen/xml/index.xml  # Should exist
```

### Go Not Available

**Solution:** Use manual docs:
```yaml
godoc_manual_content: |
  Package documentation here...
```

### Java Source Not Found

**Solution:** Verify paths and package structure:
```bash
ls src/main/java/com/example/pkg/*.java  # Should exist
```

Or use manual docs:
```yaml
java_manual_content: |
  Package documentation here...
```

### Protobuf Files Not Found

**Solution:** Verify proto_path:
```bash
ls protos/*.proto  # Should exist
```

Or use manual docs:
```yaml
protodoc_manual_content: |
  API documentation here...
```

### Math Not Rendering

**Solution:** Check MathJax extension:
```yaml
sphinx:
  extensions:
    - "sphinx.ext.mathjax"
```

## See Also

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Python Docstring Conventions (PEP 257)](https://www.python.org/dev/peps/pep-0257/)
- [Doxygen Manual](https://www.doxygen.nl/manual/)
- [Go Documentation](https://go.dev/doc/comment)
- [Javadoc Guide](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/javadoc.html)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [gRPC Documentation](https://grpc.io/docs/)
- [LaTeX Mathematics](https://en.wikibooks.org/wiki/LaTeX/Mathematics)

## Summary

Introligo provides comprehensive multi-language documentation support:

- ✅ **Python** - Zero-config autodoc integration
- ✅ **C/C++** - Industry-standard Doxygen + Breathe
- ✅ **Go** - Automatic go doc extraction
- ✅ **Java** - Javadoc source file parsing with full tag support
- ✅ **Rust** - Automatic cargo doc extraction with RST conversion
- ✅ **Protobuf** - gRPC and Protocol Buffer API documentation with AsyncAPI keywords
- ✅ **LaTeX** - Beautiful mathematical formulas

Choose the language support that fits your project, or use them all together for multi-language documentation!
