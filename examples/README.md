# Introligo Examples

This directory contains example projects demonstrating how to use Introligo to document different types of projects.

## Available Examples

### 1. Python Project (`python_project/`)
Demonstrates how to document a Python module using Introligo with Sphinx autodoc.

**Features:**
- Python module with docstrings
- Type hints support
- Usage examples in documentation
- Automatic API reference generation

**Quick Start:**
```bash
# List all examples
python docs/preview.py --list-examples

# Run the Python example
python docs/preview.py --example python_project
```

### 2. C Project (`c_project/`)
Demonstrates how to document C code using Introligo with Doxygen and Breathe.

**Features:**
- C header and implementation files
- Doxygen integration
- Breathe extension for Sphinx
- Code documentation from comments

**Quick Start:**
```bash
# First generate Doxygen XML (required for C projects)
cd examples/c_project
doxygen Doxyfile
cd ../..

# Run the C example
python docs/preview.py --example c_project
```

### 3. LaTeX Project (`latex_project/`)
Demonstrates how to include LaTeX mathematical equations in documentation.

**Features:**
- LaTeX equation files
- Automatic conversion to RST math directive
- MathJax rendering in HTML
- Document preamble stripping
- Multiple file support

**Quick Start:**
```bash
# Run the LaTeX example (no prerequisites needed)
python docs/preview.py --example latex_project
```

## Using the Preview Script

The `docs/preview.py` script has been enhanced with example support:

```bash
# List all available examples
python docs/preview.py --list-examples

# Run a specific example
python docs/preview.py --example <example_name>

# Run example without serving (build only)
python docs/preview.py --example python_project --no-serve

# Run example on custom port
python docs/preview.py --example python_project --port 8080
```

## Example Structure

Each example follows this structure:

```
example_name/
├── introligo_config.yaml    # Introligo configuration
├── README.md                # Step-by-step guide
├── source files...          # Python, C, or other source files
└── docs/                    # Generated after running (auto-created)
    ├── index.rst
    ├── generated/
    └── _build/html/         # Built HTML documentation
```

## Creating Your Own Example

To create a new example:

1. **Create a directory** in `examples/`:
   ```bash
   mkdir examples/my_example
   ```

2. **Add your source files** (Python, C, etc.)

3. **Create `introligo_config.yaml`** with your documentation structure:
   ```yaml
   index:
     title: "My Example Documentation"
     description: "Description of my example"

   generate_index: true

   modules:
     my_module:
       title: "My Module"
       description: "Module description"
       # For Python:
       module: "my_module"
       # For C/C++:
       # language: c
       # doxygen_files:
       #   - myfile.h
   ```

4. **Add a README.md** with instructions

5. **Test it**:
   ```bash
   python docs/preview.py --example my_example
   ```

## Requirements

### For Python Examples
```bash
pip install introligo sphinx sphinx_rtd_theme
```

### For C/C++ Examples
```bash
# Python packages
pip install introligo sphinx sphinx_rtd_theme breathe

# System packages
# Ubuntu/Debian:
sudo apt-get install doxygen

# macOS:
brew install doxygen
```

## Documentation Workflow

The typical workflow for each example:

1. **Prepare** - Write source code with documentation
2. **Configure** - Create `introligo_config.yaml`
3. **Generate** - Run `preview.py --example <name>`
4. **Preview** - View at http://localhost:8000
5. **Iterate** - Edit and rebuild as needed

## Tips

- **Python projects**: Use docstrings with type hints for best results
- **C/C++ projects**: Run `doxygen` before Introligo to generate XML
- **Organization**: Use parent-child relationships in YAML for hierarchy
- **Examples**: Add `usage_examples` in YAML for better documentation

## Troubleshooting

**Problem**: Example not listed
- **Solution**: Ensure `introligo_config.yaml` exists in the example directory

**Problem**: Python module not found
- **Solution**: Ensure the module is in PYTHONPATH or add to `conf.py`:
  ```python
  sys.path.insert(0, os.path.abspath('..'))
  ```

**Problem**: C documentation empty
- **Solution**: Run `doxygen Doxyfile` first to generate XML files

## Learn More

- See individual example READMEs for detailed instructions
- Check the main Introligo documentation for advanced features
- Refer to `introligo_config.yaml` files for configuration examples
