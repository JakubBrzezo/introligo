# C/C++ Language Support

Introligo integrates with Doxygen and Breathe to provide comprehensive C/C++ API documentation in Sphinx.

## Overview

C/C++ documentation in Introligo uses the industry-standard Doxygen tool for extracting documentation from source code comments, combined with the Breathe Sphinx extension for seamless integration. This two-stage process provides rich, detailed API documentation.

## Features

✅ **Industry Standard** - Uses Doxygen, the de-facto C/C++ documentation tool
✅ **Full C++ Support** - Classes, templates, namespaces, inheritance
✅ **Breathe Integration** - Native Sphinx directives for C/C++ constructs
✅ **Rich Formatting** - Diagrams, graphs, cross-references
✅ **Multi-File** - Document entire codebases or specific files
✅ **Auto-Configuration** - Introligo auto-adds Breathe extension

## Prerequisites

### Required Tools

1. **Doxygen** - Install from your package manager:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install doxygen

   # macOS
   brew install doxygen

   # Or download from https://www.doxygen.nl
   ```

2. **Breathe** - Install via pip:
   ```bash
   pip install breathe
   ```

## Basic Usage

### Minimal Configuration

```yaml
# Global Doxygen configuration
doxygen:
  xml_path: "doxygen/xml"     # Where Doxygen outputs XML
  project_name: "myproject"

modules:
  calculator:
    title: "Calculator Functions"
    language: cpp
    doxygen_file: "calculator.h"
```

### Configuration Fields

| Field | Description | Required |
|-------|-------------|----------|
| `language` | Set to `c` or `cpp` | Yes |
| `doxygen_file` | Single header/source file | One of these |
| `doxygen_files` | List of multiple files | One of these |
| `doxygen_class` | Specific class name | One of these |
| `doxygen_function` | Specific function name | One of these |
| `doxygen_namespace` | Specific namespace | One of these |

**Global `doxygen` section:**
| Field | Description | Required |
|-------|-------------|----------|
| `xml_path` | Path to Doxygen XML output | Yes |
| `project_name` | Project identifier | Yes |

## How It Works

### Two-Stage Process

1. **Doxygen Stage**: Extract documentation from C/C++ source
2. **Breathe Stage**: Convert Doxygen XML to Sphinx RST

```
C/C++ Source Code
    ↓
Doxygen (generate XML)
    ↓
XML Output
    ↓
Introligo + Breathe
    ↓
Sphinx RST Files
    ↓
Beautiful Documentation!
```

### Workflow

1. **Write Doxygen comments** in your C/C++ code
2. **Run Doxygen** to generate XML: `doxygen Doxyfile`
3. **Configure Introligo** to point to the XML
4. **Generate docs** with Introligo
5. **Build with Sphinx** as usual

## Complete Example

### Project Structure

```
myproject/
├── src/
│   ├── calculator.h      # Header with Doxygen comments
│   └── calculator.cpp
├── doxygen/
│   ├── Doxyfile         # Doxygen configuration
│   └── xml/             # Generated XML (output)
├── docs/
│   ├── introligo_config.yaml
│   └── (generated RST files)
```

### Doxygen Configuration (Doxyfile)

```
# Basic Doxygen configuration
PROJECT_NAME           = "Calculator"
OUTPUT_DIRECTORY       = doxygen
GENERATE_XML           = YES      # ← Required for Breathe
GENERATE_HTML          = NO       # Optional
XML_OUTPUT             = xml      # ← This is what Introligo uses

# Input files
INPUT                  = src/
RECURSIVE              = YES
FILE_PATTERNS          = *.h *.hpp *.cpp
```

### Introligo Configuration

```yaml
# Global Doxygen configuration
doxygen:
  xml_path: "../doxygen/xml"
  project_name: "calculator"

sphinx:
  project: "Calculator Library"
  html_theme: "furo"

modules:
  api_reference:
    title: "API Reference"
    description: "Complete C++ API documentation"

  calculator_module:
    parent: "api_reference"
    title: "Calculator Functions"
    language: cpp
    description: "Basic arithmetic operations"

    # Document specific files
    doxygen_files:
      - calculator.h
      - calculator.cpp

    overview: |
      The Calculator library provides simple arithmetic
      operations with error handling.

    usage_examples:
      - title: "Basic Usage"
        language: "cpp"
        code: |
          #include "calculator.h"

          int main() {
              int result = add(5, 3);
              std::cout << "Result: " << result << std::endl;
              return 0;
          }
```

## Doxygen Comment Styles

### JavaDoc Style (Recommended)

```cpp
/**
 * @brief Add two integers
 *
 * This function performs addition of two integer values
 * and returns the result.
 *
 * @param a The first integer
 * @param b The second integer
 * @return The sum of a and b
 *
 * @code
 * int result = add(5, 3);  // result = 8
 * @endcode
 */
int add(int a, int b);
```

### Qt Style

```cpp
/*!
 * \brief Divide two numbers
 *
 * Performs division with zero-check.
 *
 * \param dividend The number to be divided
 * \param divisor The number to divide by
 * \param[out] result Pointer to store the result
 * \return true if successful, false if divisor is zero
 */
bool divide(int dividend, int divisor, int* result);
```

### Class Documentation

```cpp
/**
 * @class Calculator
 * @brief A simple calculator class
 *
 * This class provides basic arithmetic operations
 * for integer values with proper error handling.
 *
 * @author Your Name
 * @version 1.0
 * @date 2025-01-25
 */
class Calculator {
public:
    /**
     * @brief Constructor
     * @param precision Calculation precision level
     */
    Calculator(int precision = 0);

    /**
     * @brief Add two numbers
     * @param a First operand
     * @param b Second operand
     * @return Sum of a and b
     */
    int add(int a, int b) const;

    /**
     * @brief Get current precision
     * @return Current precision value
     */
    int getPrecision() const { return m_precision; }

private:
    int m_precision;  ///< Calculation precision
};
```

### Namespace Documentation

```cpp
/**
 * @namespace math
 * @brief Mathematical operations
 *
 * This namespace contains various mathematical
 * functions and utilities.
 */
namespace math {

/**
 * @brief Calculate factorial
 * @param n Input number (must be non-negative)
 * @return Factorial of n
 * @throws std::invalid_argument if n is negative
 */
int factorial(int n);

}  // namespace math
```

## Advanced Configuration

### Document Specific Elements

**Single File:**
```yaml
modules:
  calculator:
    language: cpp
    doxygen_file: "calculator.h"
```

**Multiple Files:**
```yaml
modules:
  api:
    language: cpp
    doxygen_files:
      - "core.h"
      - "utils.h"
      - "types.h"
```

**Specific Class:**
```yaml
modules:
  calculator_class:
    language: cpp
    doxygen_class: "Calculator"
```

**Specific Function:**
```yaml
modules:
  add_function:
    language: cpp
    doxygen_function: "add"
```

**Specific Namespace:**
```yaml
modules:
  math_namespace:
    language: cpp
    doxygen_namespace: "math"
```

### Multiple Projects

Document multiple C/C++ projects:

```yaml
# Can't have multiple doxygen sections,
# but can organize with subdirectories

doxygen:
  xml_path: "doxygen_output/xml"
  project_name: "combined"

modules:
  lib1:
    language: cpp
    doxygen_files:
      - "lib1/api.h"

  lib2:
    language: cpp
    doxygen_files:
      - "lib2/core.h"
```

## Breathe Directives

Introligo generates these Breathe directives:

### File Documentation
```rst
.. doxygenfile:: calculator.h
   :project: calculator
```

### Class Documentation
```rst
.. doxygenclass:: Calculator
   :project: calculator
   :members:
   :undoc-members:
```

### Function Documentation
```rst
.. doxygenfunction:: add
   :project: calculator
```

### Namespace Documentation
```rst
.. doxygennamespace:: math
   :project: calculator
   :members:
   :undoc-members:
```

## Best Practices

### 1. Use Clear Comment Format

```cpp
/**
 * @brief One-line summary
 *
 * Detailed description here.
 *
 * @param name Parameter description
 * @return Return value description
 */
```

### 2. Document All Public APIs

```cpp
// Good - public function with doc
/**
 * @brief Public API function
 */
void publicFunction();

// OK - private function without doc
private:
    void privateHelper();  // Can use regular comments
```

### 3. Use @code Blocks for Examples

```cpp
/**
 * @brief Example function
 *
 * @code
 * int result = multiply(5, 3);
 * std::cout << result;  // Output: 15
 * @endcode
 */
int multiply(int a, int b);
```

### 4. Document Member Variables

```cpp
class MyClass {
private:
    int m_count;        ///< Number of items processed
    bool m_enabled;     ///< Whether processing is enabled
    std::string m_name; /**< Name of the instance */
};
```

### 5. Group Related Items

```cpp
/**
 * @defgroup arithmetic Arithmetic Operations
 * @brief Basic arithmetic functions
 * @{
 */

/// Add two numbers
int add(int a, int b);

/// Subtract two numbers
int subtract(int a, int b);

/** @} */  // end of arithmetic group
```

## Troubleshooting

### Doxygen XML Not Found

**Problem:** `Breathe projects: cannot find XML`

**Solution:** Check paths in configuration:
```yaml
doxygen:
  xml_path: "../doxygen/xml"  # Relative to docs directory
```

Verify XML was generated:
```bash
ls -la doxygen/xml/
# Should see index.xml and other XML files
```

### Missing Documentation

**Problem:** Functions appear but have no description

**Solution:** Add Doxygen comments to your C/C++ code:
```cpp
/** @brief Add this comment! */
void myFunction();
```

### Breathe Not Installed

**Problem:** `Extension error: Could not import extension breathe`

**Solution:**
```bash
pip install breathe
```

### Wrong Project Name

**Problem:** Documentation doesn't appear or shows wrong project

**Solution:** Match project names:
```yaml
doxygen:
  project_name: "calculator"  # ← Must match

modules:
  calc:
    doxygen_file: "calc.h"  # ← Uses global project name
```

## Example Projects

### Calculator Library

See `examples/c_project/` for a complete working example with:
- Annotated C source files
- Configured Doxyfile
- Introligo configuration
- Generated documentation

### Structure
```
examples/c_project/
├── calculator.h          # Header with Doxygen comments
├── calculator.c          # Implementation
├── Doxyfile             # Doxygen config
├── introligo_config.yaml # Introligo config
├── doxygen/
│   └── xml/             # Generated XML
└── docs/
    └── (generated docs)
```

## Comparison with Other Languages

| Feature | C/C++ | Python | Go |
|---------|-------|--------|-----|
| **Tool** | Doxygen | autodoc | go doc |
| **Stages** | 2 (Doxygen + Breathe) | 1 (Sphinx) | 1 (Introligo) |
| **Setup** | ⚠️ Complex | ✅ Simple | ✅ Simple |
| **Features** | ✅ Very Rich | ✅ Rich | ⚠️ Basic |
| **Diagrams** | ✅ Yes | ❌ No | ❌ No |
| **Templates** | ✅ Full | N/A | N/A |

## See Also

- [Doxygen Manual](https://www.doxygen.nl/manual/)
- [Breathe Documentation](https://breathe.readthedocs.io/)
- [Doxygen Special Commands](https://www.doxygen.nl/manual/commands.html)
- [C++ Documentation Guide](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-comments)

## Summary

Introligo's C/C++ support provides:

✅ **Industry-standard** Doxygen integration
✅ **Automatic Breathe configuration** - Just specify files
✅ **Flexible targeting** - Files, classes, functions, or namespaces
✅ **Rich documentation** - Full Doxygen feature set
✅ **Seamless Sphinx integration** - Native RST output

Document your C/C++ projects with the power of Doxygen and the beauty of Sphinx!
