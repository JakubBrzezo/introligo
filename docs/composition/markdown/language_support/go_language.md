# Go Language Support

Introligo provides automatic documentation extraction for Go packages, seamlessly integrating Go API documentation into your Sphinx site.

## Overview

Unlike Python (with autodoc) and C/C++ (with Doxygen/Breathe), Go documentation is extracted directly using the `go doc` command and converted to reStructuredText format. This provides a clean, native Sphinx experience without requiring external tools beyond Go itself.

## Features

✅ **Automatic Extraction** - Runs `go doc -all` to extract complete package documentation
✅ **RST Conversion** - Converts godoc output to properly formatted reStructuredText
✅ **Seamless Integration** - Extracted docs appear directly in your Sphinx site
✅ **Graceful Fallback** - Works even without Go installed (provides pkg.go.dev links)
✅ **Manual Override** - Option to provide manual documentation when needed

## Basic Usage

### Minimal Configuration

```yaml
modules:
  my_package:
    title: "My Go Package"
    language: go
    godoc_package: "github.com/user/mypackage"
    godoc_path: "."
```

### Configuration Fields

| Field | Description | Required |
|-------|-------------|----------|
| `language: go` | Specifies Go language | Yes |
| `godoc_package` | Go package import path | Yes |
| `godoc_path` | Path to package directory (relative to config) | Recommended |
| `godoc_packages` | List of multiple packages | Optional |
| `godoc_manual_content` | Manual documentation (fallback) | Optional |

## How It Works

### Automatic Extraction Process

1. **Detection**: Introligo detects `language: go` in your configuration
2. **Execution**: Runs `go doc -all <package>` in the specified directory
3. **Conversion**: Parses godoc output and converts to RST format
4. **Integration**: Injects the formatted documentation into your Sphinx build

### Example Flow

```
Your YAML Config
    ↓
Introligo Generator
    ↓
go doc -all github.com/user/pkg
    ↓
Parse & Convert to RST
    ↓
Generate Sphinx RST files
    ↓
Beautiful Documentation!
```

## Complete Example

```yaml
sphinx:
  project: "My Go Project"
  html_theme: "furo"

modules:
  api_reference:
    title: "API Reference"
    description: "Complete API documentation"

  calculator:
    parent: "api_reference"
    title: "Calculator Package"
    language: go
    description: "Arithmetic operations package"

    # Package configuration
    godoc_package: "github.com/example/calculator"
    godoc_path: "./calculator"

    # Your narrative documentation
    overview: |
      The Calculator package provides simple arithmetic operations
      for integer values with proper error handling.

    features:
      - "Addition and subtraction operations"
      - "Multiplication and division with zero-check"
      - "Error handling for edge cases"

    usage_examples:
      - title: "Basic Usage"
        language: "go"
        code: |
          package main

          import "github.com/example/calculator"

          func main() {
              result := calculator.Add(5, 3)
              println(result)  // Output: 8
          }

      - title: "Error Handling"
        language: "go"
        code: |
          result, err := calculator.Divide(10, 2)
          if err != nil {
              log.Fatal(err)
          }
          println(result)  // Output: 5
```

## Generated Documentation

The above configuration generates documentation with:

### Package Overview
Extracted from package-level comments in your Go code

### Function Documentation
```go
func Add(a, b int) int
```
Add returns the sum of two integers.

**Parameters:**
- `a` - The first integer
- `b` - The second integer

**Returns:** The sum of a and b.

### Type Documentation
All exported types, structs, interfaces, and constants from your package

## Manual Documentation Fallback

When Go is not installed or the package is not accessible, you can provide manual documentation:

```yaml
modules:
  my_package:
    language: go
    godoc_package: "github.com/user/pkg"

    # Manual documentation (used as fallback)
    godoc_manual_content: |
      Package provides awesome functionality.

      Functions
      ~~~~~~~~~

      .. code-block:: go

         func DoSomething(input string) error

      DoSomething performs an operation on the input string.

      **Parameters:**
      - ``input`` - The input string to process

      **Returns:** An error if the operation fails.
```

## Multiple Packages

Document multiple related packages:

```yaml
modules:
  all_packages:
    title: "All Packages"
    language: go
    godoc_packages:
      - "github.com/user/pkg1"
      - "github.com/user/pkg2"
      - "github.com/user/pkg3"
    godoc_path: "."
```

Each package will be extracted and documented separately within the same page.

## Requirements

### For Automatic Extraction
- Go 1.16 or higher installed
- Package accessible (either local or via `go get`)
- Proper Go module structure

### For Manual Documentation Only
- No special requirements
- Works with just Sphinx and Introligo

## Best Practices

### 1. Write Good Godoc Comments

```go
// Package calculator provides arithmetic operations.
//
// This package implements basic mathematical functions
// with proper error handling and input validation.
package calculator

// Add returns the sum of two integers.
//
// Example:
//     result := Add(5, 3)  // result = 8
func Add(a, b int) int {
    return a + b
}
```

### 2. Use Descriptive Package Names

```yaml
godoc_package: "github.com/organization/project/pkg/calculator"
```

### 3. Organize with Parents

```yaml
modules:
  api:
    title: "API Reference"

  math_pkg:
    parent: "api"
    language: go
    godoc_package: "github.com/org/proj/math"

  utils_pkg:
    parent: "api"
    language: go
    godoc_package: "github.com/org/proj/utils"
```

### 4. Combine with Narrative Docs

```yaml
modules:
  my_package:
    language: go
    godoc_package: "github.com/user/pkg"

    # Add context with narrative sections
    overview: "Why this package exists..."
    installation: "go get github.com/user/pkg"
    usage_examples: [...]
    best_practices: [...]
```

## Troubleshooting

### Go Not Found

**Problem:** `WARNING: Go is not installed - skipping documentation extraction`

**Solution:**
- Install Go from https://go.dev/dl/
- Ensure `go` is in your PATH
- Or provide `godoc_manual_content` as fallback

### Package Not Found

**Problem:** `go doc` fails to find the package

**Solution:**
- Run `go get <package>` first
- Check that `godoc_path` points to correct directory
- Verify the package import path is correct

### Empty Documentation

**Problem:** No documentation appears even though extraction succeeds

**Solution:**
- Add godoc comments to your Go code
- Use proper comment format (see Best Practices)
- Check that functions/types are exported (start with capital letter)

## Comparison with Other Languages

| Feature | Python | C/C++ | Go |
|---------|--------|-------|-----|
| **Extraction Tool** | autodoc | Doxygen | go doc |
| **Automatic** | ✅ Yes | ✅ Yes | ✅ Yes |
| **External Tool** | No | Yes | No* |
| **Format** | Docstrings | Comments | Comments |
| **Manual Fallback** | No | No | ✅ Yes |

*Requires Go to be installed

## See Also

- [Go Documentation Comments](https://go.dev/doc/comment)
- [Effective Go](https://go.dev/doc/effective_go)
- [pkg.go.dev](https://pkg.go.dev) - Online Go package documentation
- [Introligo Go Example](https://github.com/JakubBrzezo/introligo/tree/main/examples/go_project)

## Summary

Introligo's Go support provides:

✅ **Automatic extraction** using `go doc`
✅ **Clean RST conversion** for Sphinx
✅ **Seamless integration** with your docs
✅ **Graceful fallback** when Go unavailable
✅ **Manual override option** for flexibility

Start documenting your Go packages today!
