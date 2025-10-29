# Java Calculator Project - Introligo Example

This example demonstrates how to use **Introligo** to generate documentation for Java projects.

## Overview

This project contains a simple Java calculator library with:

- **Calculator.java**: Basic arithmetic operations (add, subtract, multiply, divide, modulo)
- **MathUtils.java**: Advanced mathematical utilities (power, factorial, prime checking, GCD)

The example shows how Introligo can automatically extract and format Javadoc comments into beautiful Sphinx documentation.

## Project Structure

```
java_project/
├── introligo_config.yaml          # Introligo configuration
├── README.md                       # This file
└── com/
    └── example/
        └── calculator/
            ├── Calculator.java     # Main calculator class
            └── MathUtils.java      # Math utility functions
```

## Features Demonstrated

### 1. Java Package Documentation

The configuration shows how to document an entire Java package:

```yaml
modules:
  calculator:
    language: java
    java_package: "com.example.calculator"
    java_source_path: "."
```

Introligo will:
- Find all `.java` files in the package directory
- Extract Javadoc comments from classes, methods, and fields
- Convert them to reStructuredText format
- Include them in the generated documentation

### 2. Individual File Documentation

You can also document specific Java files:

```yaml
modules:
  utils:
    language: java
    java_source_files:
      - "com/example/calculator/MathUtils.java"
    java_source_path: "."
```

### 3. Javadoc Features Supported

The example demonstrates documentation extraction for:

- **Class documentation** with description and metadata (@author, @version)
- **Method documentation** with parameters (@param), return values (@return), and exceptions (@throws)
- **Field documentation** for constants and member variables
- **Access modifiers** (public, private, protected, static, final, abstract)
- **Exception handling** documentation with @throws/@exception tags

### 4. Rich Documentation Content

The configuration also shows how to add:

- **Overview sections** - High-level description of the module
- **Installation instructions** - How to set up and use the code
- **Usage examples** - Practical code examples with syntax highlighting
- **Notes** - Implementation details and important information

## Generating Documentation

### Step 1: Compile Java Sources (Optional)

If you want to test the Java code:

```bash
javac com/example/calculator/*.java
```

### Step 2: Generate Documentation

From the `java_project` directory:

```bash
# Generate RST files
introligo introligo_config.yaml --output-dir docs/source

# Build HTML documentation with Sphinx
cd docs
sphinx-build -b html source build/html
```

Or use the shorthand:

```bash
introligo introligo_config.yaml --output-dir docs/source && cd docs && make html
```

### Step 3: View Documentation

Open `docs/build/html/index.html` in your web browser.

## Configuration Options

### Java-Specific Configuration Fields

| Field | Description | Example |
|-------|-------------|---------|
| `language` | Set to `"java"` | `language: java` |
| `java_package` | Java package name | `java_package: "com.example.calculator"` |
| `java_packages` | Multiple packages | `java_packages: ["com.example.calc", "com.example.util"]` |
| `java_source_files` | Specific files | `java_source_files: ["Calculator.java"]` |
| `java_source_path` | Path to sources | `java_source_path: "src/main/java"` |
| `javadoc_path` | Pre-generated Javadoc | `javadoc_path: "build/javadoc"` |
| `java_manual_content` | Manual fallback | Content used if extraction fails |

### How Java Documentation Works

1. **Language Detection**: Introligo detects Java modules by checking for:
   - `language: java` field
   - Presence of `java_package`, `java_packages`, `java_source_files`, or `javadoc_path`

2. **Extraction**: The `JavaDocExtractor` reads Java source files and extracts:
   - Javadoc comments (`/** ... */`)
   - Class, interface, method, and field declarations
   - Access modifiers and type information

3. **Conversion**: Javadoc is converted to reStructuredText:
   - `@param` becomes **Parameters:** section
   - `@return` becomes **Returns:** section
   - `@throws/@exception` becomes **Throws:** section
   - Code signatures are formatted in `.. code-block:: java` directives

4. **Rendering**: Sphinx builds the final HTML documentation with:
   - Syntax-highlighted code blocks
   - Formatted parameter tables
   - Cross-references and navigation

## Requirements

- **Python 3.8+** with Introligo installed
- **Sphinx 4.0+** for building documentation
- **Java JDK** (optional, only needed to compile/test the code)

## Comparison with Other Languages

| Feature | Python | C/C++ | Go | Java |
|---------|--------|-------|----|----|
| Auto-extraction | ✅ autodoc | ✅ Doxygen/Breathe | ✅ go doc | ✅ Javadoc parser |
| Sphinx extension | sphinx.ext.autodoc | breathe | None (code blocks) | None (code blocks) |
| External tools | None | Doxygen | Go toolchain | None |
| Configuration | `module: "package"` | `doxygen_file: "file.h"` | `godoc_package: "pkg"` | `java_package: "pkg"` |

## Advanced Usage

### Multiple Packages

Document several Java packages at once:

```yaml
modules:
  all_packages:
    language: java
    java_packages:
      - "com.example.calculator"
      - "com.example.utils"
      - "com.example.models"
    java_source_path: "src/main/java"
```

### Manual Content Fallback

Provide manual documentation if Java is not available:

```yaml
modules:
  calculator:
    language: java
    java_package: "com.example.calculator"
    java_manual_content: |
      **Calculator Package**

      Provides basic arithmetic operations.

      .. code-block:: java

         public class Calculator {
             public int add(int a, int b) { ... }
             public int subtract(int a, int b) { ... }
         }
```

### Integration with Maven/Gradle

For Maven projects:

```yaml
modules:
  api:
    language: java
    java_package: "com.mycompany.myapp"
    java_source_path: "src/main/java"
```

For Gradle projects:

```yaml
modules:
  api:
    language: java
    java_package: "com.mycompany.myapp"
    java_source_path: "app/src/main/java"
```

## Troubleshooting

### Documentation Not Generated

If Java documentation doesn't appear:

1. **Check language is set**: `language: java`
2. **Verify source path**: Ensure `java_source_path` points to the correct directory
3. **Check package structure**: Package name should match directory structure
4. **Review logs**: Look for errors in Introligo output

### Javadoc Not Extracted

If Javadoc comments aren't showing up:

1. **Use proper format**: Javadoc must use `/** */` (not `/* */` or `//`)
2. **Check file encoding**: Ensure Java files are UTF-8 encoded
3. **Verify file access**: Ensure Introligo can read the Java files
4. **Check extraction logs**: Enable verbose logging with `--verbose`

### Formatting Issues

If the generated RST looks wrong:

1. **Review code-block directives**: Java code should be in `.. code-block:: java`
2. **Check indentation**: RST is sensitive to indentation
3. **Validate Javadoc tags**: Ensure @param, @return, @throws are properly formatted

## Next Steps

- Explore the generated documentation in `docs/build/html/`
- Modify `Calculator.java` or `MathUtils.java` and regenerate docs
- Try documenting your own Java projects
- Combine with other language modules (Python, C++, Go)

## Resources

- [Introligo Documentation](https://github.com/wttech/introligo)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Javadoc Guide](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/javadoc.html)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
