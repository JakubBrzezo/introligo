# Rust Language Support

Introligo provides automatic documentation extraction for Rust crates, seamlessly integrating Rust API documentation into your Sphinx site.

## Overview

Similar to Go and Java support, Rust documentation is extracted directly from your Rust source code using `cargo doc` and converted to reStructuredText format. This provides a clean, native Sphinx experience without requiring external tools beyond Cargo itself.

## Features

✅ **Automatic Extraction** - Runs `cargo doc` to build documentation and extracts content from source
✅ **RST Conversion** - Converts Rust documentation comments to properly formatted reStructuredText
✅ **Seamless Integration** - Extracted docs appear directly in your Sphinx site
✅ **Graceful Fallback** - Works even without Cargo installed (provides docs.rs links)
✅ **Manual Override** - Option to provide manual documentation when needed

## Basic Usage

### Minimal Configuration

```yaml
modules:
  my_crate:
    title: "My Rust Crate"
    language: rust
    rustdoc_crate: "my_crate"
    rustdoc_path: "."
```

### Configuration Fields

| Field | Description | Required |
|-------|-------------|----------|
| `language: rust` | Specifies Rust language | Yes |
| `rustdoc_crate` | Rust crate name | Recommended |
| `rustdoc_path` | Path to crate directory (relative to config) | Recommended |
| `rustdoc_manual_content` | Manual documentation (fallback) | Optional |

## How It Works

### Automatic Extraction Process

1. **Detection**: Introligo detects `language: rust` in your configuration
2. **Execution**: Runs `cargo doc --no-deps` to build documentation
3. **Parsing**: Extracts documentation comments from source files (lib.rs, main.rs)
4. **Conversion**: Parses doc comments and converts to RST format
5. **Integration**: Injects the formatted documentation into your Sphinx build

### Example Flow

```
Your YAML Config
    ↓
Introligo Generator
    ↓
cargo doc --no-deps
    ↓
Parse Rust source (lib.rs)
    ↓
Extract doc comments (//!, ///)
    ↓
Generate Sphinx RST files
    ↓
Beautiful Documentation!
```

## Complete Example

```yaml
sphinx:
  project: "My Rust Project"
  html_theme: "furo"

modules:
  api_reference:
    title: "API Reference"
    description: "Complete API documentation"

  calculator:
    parent: "api_reference"
    title: "Calculator Crate"
    language: rust
    description: "Arithmetic operations crate"

    # Crate configuration
    rustdoc_crate: "calculator"
    rustdoc_path: "./calculator"

    # Your narrative documentation
    overview: |
      The Calculator crate provides simple arithmetic operations
      for numeric values with proper error handling.

    features:
      - "Addition and subtraction operations"
      - "Multiplication and division with zero-check"
      - "Error handling for edge cases"
      - "Generic numeric type support"

    usage_examples:
      - title: "Basic Usage"
        language: "rust"
        code: |
          use calculator::Calculator;

          fn main() {
              let calc = Calculator::new();
              let result = calc.add(5, 3);
              println!("{}", result);  // Output: 8
          }

      - title: "Error Handling"
        language: "rust"
        code: |
          use calculator::Calculator;

          fn main() {
              let calc = Calculator::new();
              match calc.divide(10, 2) {
                  Ok(result) => println!("Result: {}", result),
                  Err(e) => eprintln!("Error: {}", e),
              }
          }
```

## Generated Documentation

The above configuration generates documentation with:

### Crate-Level Documentation
Extracted from module-level comments in your Rust code (//! comments)

### Function Documentation
```rust
pub fn add(a: i32, b: i32) -> i32
```
Adds two integers and returns the sum.

**Parameters:**
- `a` - The first integer
- `b` - The second integer

**Returns:** The sum of a and b.

### Type Documentation
All public items (structs, enums, traits, functions) with their documentation

## Manual Documentation Fallback

When Cargo is not installed or the crate is not accessible, you can provide manual documentation:

```yaml
modules:
  my_crate:
    language: rust
    rustdoc_crate: "my_crate"

    # Manual documentation (used as fallback)
    rustdoc_manual_content: |
      Crate provides awesome functionality.

      Functions
      ~~~~~~~~~

      .. code-block:: rust

         pub fn do_something(input: &str) -> Result<String, Error>

      Performs an operation on the input string.

      **Parameters:**
      - ``input`` - The input string to process

      **Returns:** A Result with the processed string or an error.
```

## Requirements

### For Automatic Extraction
- Rust and Cargo installed
- Valid Cargo.toml in crate directory
- Source code in src/ directory

### For Manual Documentation Only
- No special requirements
- Works with just Sphinx and Introligo

## Best Practices

### 1. Write Good Rustdoc Comments

```rust
//! # Calculator Crate
//!
//! This crate provides basic arithmetic operations
//! with proper error handling.

/// Adds two integers and returns the sum.
///
/// # Examples
///
/// ```
/// let result = add(5, 3);
/// assert_eq!(result, 8);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

### 2. Use Descriptive Crate Names

```yaml
rustdoc_crate: "my_awesome_calculator"
rustdoc_path: "./crates/calculator"
```

### 3. Organize with Parents

```yaml
modules:
  api:
    title: "API Reference"

  core_crate:
    parent: "api"
    language: rust
    rustdoc_crate: "myproject_core"
    rustdoc_path: "./crates/core"

  utils_crate:
    parent: "api"
    language: rust
    rustdoc_crate: "myproject_utils"
    rustdoc_path: "./crates/utils"
```

### 4. Combine with Narrative Docs

```yaml
modules:
  my_crate:
    language: rust
    rustdoc_crate: "my_crate"
    rustdoc_path: "."

    # Add context with narrative sections
    overview: "Why this crate exists..."
    installation: "cargo add my_crate"
    usage_examples: [...]
    best_practices: [...]
```

## Troubleshooting

### Cargo Not Found

**Problem:** `WARNING: Cargo is not installed - skipping documentation extraction`

**Solution:**
- Install Rust and Cargo from https://rustup.rs/
- Ensure `cargo` is in your PATH
- Or provide `rustdoc_manual_content` as fallback

### Crate Not Found

**Problem:** Cargo doc fails to find the crate

**Solution:**
- Check that `rustdoc_path` points to correct directory
- Verify Cargo.toml exists in the path
- Ensure the crate builds with `cargo build`

### Empty Documentation

**Problem:** No documentation appears even though extraction succeeds

**Solution:**
- Add rustdoc comments to your Rust code
- Use proper comment format: `///` for items, `//!` for modules
- Check that items are public (marked with `pub`)

## Comparison with Other Languages

| Feature | Python | Go | Java | Rust |
|---------|--------|-----|------|------|
| **Extraction Tool** | autodoc | go doc | Source parser | cargo doc |
| **Automatic** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **External Tool** | No | No* | No | Yes |
| **Format** | Docstrings | Comments | Comments | Doc comments |
| **Manual Fallback** | No | ✅ Yes | ✅ Yes | ✅ Yes |

\*Requires Cargo to be installed

## See Also

- [Rust Documentation](https://doc.rust-lang.org/rustdoc/)
- [The rustdoc book](https://doc.rust-lang.org/rustdoc/index.html)
- [docs.rs](https://docs.rs) - Rust documentation host
- [Introligo Rust Example](https://github.com/JakubBrzezo/introligo/tree/main/examples/rust_project)

## Summary

Introligo's Rust support provides:

✅ **Automatic extraction** using `cargo doc`
✅ **Clean RST conversion** for Sphinx
✅ **Seamless integration** with your docs
✅ **Graceful fallback** when Cargo unavailable
✅ **Manual override option** for flexibility

Start documenting your Rust crates today!
