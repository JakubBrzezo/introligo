# Java Language Support

Introligo provides automatic documentation extraction for Java packages, seamlessly integrating Javadoc documentation into your Sphinx site.

## Overview

Java documentation is extracted directly from source files by parsing Javadoc comments and converting them to reStructuredText format. This provides a clean, native Sphinx experience without requiring external tools beyond reading Java source files.

## Features

✅ **Automatic Extraction** - Parses Java source files and extracts Javadoc comments
✅ **RST Conversion** - Converts Javadoc tags to properly formatted reStructuredText
✅ **Seamless Integration** - Extracted docs appear directly in your Sphinx site
✅ **No External Tools** - Works without javadoc command (reads sources directly)
✅ **Manual Override** - Option to provide manual documentation when needed

## Basic Usage

### Minimal Configuration

```yaml
modules:
  my_package:
    title: "My Java Package"
    language: java
    java_package: "com.example.mypackage"
    java_source_path: "src/main/java"
```

### Configuration Fields

| Field | Description | Required |
|-------|-------------|----------|
| `language: java` | Specifies Java language | Yes |
| `java_package` | Java package name (e.g., com.example.pkg) | Yes* |
| `java_source_path` | Path to source directory (relative to config) | Recommended |
| `java_packages` | List of multiple packages | Optional |
| `java_source_files` | List of specific Java files | Optional |
| `java_manual_content` | Manual documentation (fallback) | Optional |

*Either `java_package`, `java_packages`, or `java_source_files` is required

## How It Works

### Automatic Extraction Process

1. **Detection**: Introligo detects `language: java` in your configuration
2. **File Discovery**: Finds Java source files in the specified package/files
3. **Parsing**: Reads Java files and extracts Javadoc comments
4. **Conversion**: Parses Javadoc tags (@param, @return, @throws) and converts to RST
5. **Integration**: Injects the formatted documentation into your Sphinx build

### Example Flow

```
Your YAML Config
    ↓
Introligo Generator
    ↓
Read Java Source Files
    ↓
Parse Javadoc Comments
    ↓
Convert to RST Format
    ↓
Generate Sphinx RST files
    ↓
Beautiful Documentation!
```

## Complete Example

```yaml
sphinx:
  project: "My Java Project"
  html_theme: "furo"

modules:
  api_reference:
    title: "API Reference"
    description: "Complete API documentation"

  calculator:
    parent: "api_reference"
    title: "Calculator Package"
    language: java
    description: "Arithmetic operations package"

    # Package configuration
    java_package: "com.example.calculator"
    java_source_path: "src/main/java"

    # Your narrative documentation
    overview: |
      The Calculator package provides simple arithmetic operations
      for integer values with proper error handling.

    features:
      - "Addition and subtraction operations"
      - "Multiplication and division with zero-check"
      - "Exception handling for edge cases"

    installation: |
      Add the following to your project's classpath:

      ```bash
      javac com/example/calculator/*.java
      ```

    usage_examples:
      - title: "Basic Usage"
        language: "java"
        code: |
          Calculator calc = new Calculator();

          int sum = calc.add(5, 3);
          System.out.println(sum);  // Output: 8

          int diff = calc.subtract(10, 4);
          System.out.println(diff);  // Output: 6

      - title: "Error Handling"
        language: "java"
        code: |
          Calculator calc = new Calculator();

          try {
              int result = calc.divide(10, 0);
          } catch (ArithmeticException e) {
              System.err.println("Cannot divide by zero!");
          }
```

## Generated Documentation

The above configuration generates documentation with:

### Class Overview
Extracted from class-level Javadoc comments in your Java code

### Method Documentation
```java
public int add(int a, int b)
```

Adds two integers.
This method performs addition of two integer values and returns the sum.

**Parameters:**
- `a` - The first integer (addend)
- `b` - The second integer (addend)

**Returns:** The sum of a and b

**Throws:**
- `ArithmeticException` - If overflow occurs

### Field Documentation
All public fields and constants with their Javadoc comments

## Javadoc Tag Support

Introligo recognizes and converts the following Javadoc tags:

| Javadoc Tag | RST Output | Description |
|-------------|------------|-------------|
| `@param` | **Parameters:** section | Method parameter descriptions |
| `@return` | **Returns:** section | Return value description |
| `@throws` / `@exception` | **Throws:** section | Exception documentation |
| Description text | Regular paragraphs | Main description |

Tags that are filtered out (metadata only):
- `@author` - Author information
- `@version` - Version information
- `@since` - Since which version
- `@see` - See also references
- `@deprecated` - Deprecation notice

## Package-Level Documentation

Document an entire Java package:

```yaml
modules:
  calculator:
    title: "Calculator Package"
    language: java
    java_package: "com.example.calculator"
    java_source_path: "src/main/java"
```

This will automatically find and document all `.java` files in `src/main/java/com/example/calculator/`.

## File-Level Documentation

Document specific Java files:

```yaml
modules:
  utils:
    title: "Utility Classes"
    language: java
    java_source_files:
      - "src/main/java/com/example/utils/StringUtils.java"
      - "src/main/java/com/example/utils/DateUtils.java"
    java_source_path: "src/main/java"
```

## Multiple Packages

Document multiple related packages:

```yaml
modules:
  all_packages:
    title: "All Packages"
    language: java
    java_packages:
      - "com.example.calculator"
      - "com.example.utils"
      - "com.example.models"
    java_source_path: "src/main/java"
```

Each package will be extracted and documented separately within the same page.

## Manual Documentation Fallback

When source files are not accessible, you can provide manual documentation:

```yaml
modules:
  my_package:
    language: java
    java_package: "com.example.pkg"

    # Manual documentation (used as fallback)
    java_manual_content: |
      Package provides awesome functionality.

      Classes
      ~~~~~~~

      **Calculator**

      .. code-block:: java

         public class Calculator {
             public int add(int a, int b)
         }

      Provides basic arithmetic operations.

      **Parameters:**
      - ``a`` - First operand
      - ``b`` - Second operand

      **Returns:** Sum of a and b
```

## Maven/Gradle Integration

### Maven Project Structure

```yaml
modules:
  api:
    language: java
    java_package: "com.mycompany.myapp"
    java_source_path: "src/main/java"
```

### Gradle Project Structure

```yaml
modules:
  api:
    language: java
    java_package: "com.mycompany.myapp"
    java_source_path: "app/src/main/java"
```

### Multi-Module Maven Project

```yaml
modules:
  core_api:
    language: java
    java_package: "com.mycompany.core"
    java_source_path: "core/src/main/java"

  utils_api:
    language: java
    java_package: "com.mycompany.utils"
    java_source_path: "utils/src/main/java"
```

## Requirements

### For Automatic Extraction
- Java source files (.java) accessible to Introligo
- Proper package directory structure
- UTF-8 encoded source files

### Optional
- Java JDK (only if you want to compile/test)
- javadoc tool (not required for extraction)

## Best Practices

### 1. Write Good Javadoc Comments

```java
package com.example.calculator;

/**
 * Calculator class provides simple arithmetic operations.
 *
 * <p>This class implements basic mathematical functions
 * with proper error handling and input validation.</p>
 *
 * @author Example Team
 * @version 1.0.0
 */
public class Calculator {

    /**
     * Adds two integers.
     *
     * <p>This method performs addition of two integer values
     * and returns the sum.</p>
     *
     * @param a the first integer (addend)
     * @param b the second integer (addend)
     * @return the sum of a and b
     * @throws ArithmeticException if integer overflow occurs
     */
    public int add(int a, int b) throws ArithmeticException {
        return a + b;
    }
}
```

### 2. Use Descriptive Package Names

```yaml
java_package: "com.organization.project.calculator"
```

### 3. Organize with Parents

```yaml
modules:
  api:
    title: "API Reference"

  calculator_pkg:
    parent: "api"
    language: java
    java_package: "com.example.calculator"

  utils_pkg:
    parent: "api"
    language: java
    java_package: "com.example.utils"
```

### 4. Combine with Narrative Docs

```yaml
modules:
  my_package:
    language: java
    java_package: "com.example.pkg"
    java_source_path: "src/main/java"

    # Add context with narrative sections
    overview: "Why this package exists..."
    installation: "Add to your classpath..."
    usage_examples: [...]
    notes: "Important implementation details..."
```

### 5. Document Public API Only

Focus Javadoc comments on public classes and methods that form your API:

```java
/**
 * Public API method - well documented
 */
public int publicMethod() { ... }

// Private helper - minimal comments needed
private void helperMethod() { ... }
```

## Troubleshooting

### Source Files Not Found

**Problem:** `Java package directory not found`

**Solution:**
- Verify `java_source_path` points to the correct directory
- Check that package name matches directory structure
- Ensure Java files exist: `src/main/java/com/example/pkg/*.java`

### Empty Documentation

**Problem:** No documentation appears even though extraction succeeds

**Solution:**
- Add Javadoc comments to your Java code (use `/** */` not `/* */`)
- Use proper Javadoc format with tags
- Check that classes/methods are public
- Verify UTF-8 encoding

### Encoding Issues

**Problem:** Special characters appear incorrectly

**Solution:**
- Ensure Java files are UTF-8 encoded
- Check your editor's file encoding settings
- Re-save files with UTF-8 encoding

### Missing Methods

**Problem:** Some methods don't appear in documentation

**Solution:**
- Check that methods are `public` or `protected`
- Private methods are not extracted by default
- Verify Javadoc comments are present

## Comparison with Other Languages

| Feature | Python | C/C++ | Go | Java |
|---------|--------|-------|-----|------|
| **Extraction Tool** | autodoc | Doxygen | go doc | Source parser |
| **Automatic** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **External Tool** | No | Yes | No* | No |
| **Format** | Docstrings | Comments | Comments | Javadoc |
| **Manual Fallback** | No | No | ✅ Yes | ✅ Yes |
| **Tag Support** | ✅ Full | ✅ Full | ⚠️ Limited | ✅ Full |

*Requires Go to be installed

## Example Java Project

See the complete example in the Introligo repository:

```
examples/java_project/
├── introligo_config.yaml
├── README.md
└── com/
    └── example/
        └── calculator/
            ├── Calculator.java
            └── MathUtils.java
```

This example demonstrates:
- Full package documentation
- Individual file documentation
- Javadoc tag conversion
- Usage examples
- Error handling patterns

## See Also

- [Javadoc Guide](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/javadoc.html) - Official Javadoc documentation
- [How to Write Doc Comments](https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html) - Best practices
- [Maven Javadoc Plugin](https://maven.apache.org/plugins/maven-javadoc-plugin/) - Maven integration
- [Introligo Java Example](https://github.com/JakubBrzezo/introligo/tree/main/examples/java_project)

## Summary

Introligo's Java support provides:

✅ **Automatic extraction** from Java source files
✅ **Javadoc tag conversion** (@param, @return, @throws)
✅ **Clean RST output** for Sphinx
✅ **Package & file-level** documentation
✅ **Maven/Gradle support** out of the box
✅ **Manual override option** for flexibility

Start documenting your Java packages today!
