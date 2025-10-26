# Go Calculator Example

This example demonstrates how to use Introligo to generate documentation for a Go project.

## Structure

```
go_project/
├── calculator/
│   └── calculator.go    # Go calculator package with godoc comments
├── go.mod               # Go module file
├── introligo_config.yaml # Introligo configuration
└── README.md            # This file
```

## Prerequisites

1. **Python 3.8+** with Introligo installed
2. **Sphinx** for building documentation
3. **Go 1.21+** (optional, for running godoc locally)

## Go Documentation Extraction

Introligo automatically extracts Go documentation from your packages using `go doc` and converts it to reStructuredText format for seamless integration with Sphinx.

**How it works:**

1. **Automatic Extraction**: When you specify `language: go` and `godoc_package`, Introligo runs `go doc -all` on your package
2. **Conversion to RST**: The godoc output is parsed and converted to proper reStructuredText with code blocks and formatting
3. **Direct Integration**: The extracted documentation appears directly in your Sphinx site alongside your narrative documentation

**Requirements:**
- Go must be installed on the build system
- The package must be accessible (either local or installed via `go get`)

**Fallback**: If Go is not available or the package can't be found, Introligo gracefully falls back to providing links to pkg.go.dev

## Generating Documentation

From this directory, run:

```bash
python -m introligo introligo_config.yaml -o docs
```

This will:
1. Read the `introligo_config.yaml` configuration
2. Generate reStructuredText files in `docs/generated/`
3. Create a `conf.py` with auto-configured Go extensions
4. Create an `index.rst` file

## Building HTML Documentation

Once the RST files are generated, build the HTML documentation:

```bash
cd docs
sphinx-build -b html . _build/html
```

Then open `_build/html/index.html` in your browser.

## Configuration Highlights

The `introligo_config.yaml` demonstrates:

- **Go package documentation** using `godoc_package` field
- **Language specification** with `language: go`
- **Automatic extension configuration** - Introligo auto-adds `sphinxcontrib.golangdomain`
- **Usage examples** with Go code blocks
- **Error handling examples** specific to Go patterns

## Go-Specific Fields

For Go documentation, you can use these fields in your module configuration:

- `godoc_package`: Single Go package path (e.g., `github.com/user/pkg`)
- `godoc_packages`: List of Go package paths for multi-package documentation
- `godoc_path`: Path to the Go package directory (relative to config file)
- `godoc_function`: Specific function to document (future feature)
- `godoc_type`: Specific type to document (future feature)
- `language: go`: Explicitly set language to Go

## Example Usage

The calculator package provides simple functions:

```go
import "github.com/example/calculator"

result := calculator.Add(5, 3)
result = calculator.Multiply(4, 7)

result, err := calculator.Divide(10, 2)
if err != nil {
    log.Fatal(err)
}
```

## Notes

The Go support in Introligo provides:
- **Automatic documentation extraction** using `go doc`
- **Automatic language detection** from `godoc_*` fields
- **Proper syntax highlighting** for Go code examples
- **Seamless integration** - extracted docs appear directly in your Sphinx site
- **Graceful fallback** - works even without Go installed (with links to pkg.go.dev)
