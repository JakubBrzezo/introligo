# Diagram Examples for Introligo

This example demonstrates how to include various types of diagrams in your Sphinx documentation using Introligo.

## Supported Diagram Types

### 1. PlantUML (.puml, .plantuml)
UML diagrams including sequence diagrams, class diagrams, activity diagrams, etc.

**Requirements:**
- Install: `pip install sphinxcontrib-plantuml`
- PlantUML JAR file or PlantUML server

**Example files:**
- `diagrams/sequence.puml` - Authentication sequence diagram
- `diagrams/class_diagram.puml` - Domain model class diagram

### 2. Mermaid (.mmd, .mermaid)
Flowcharts, sequence diagrams, Gantt charts, and more.

**Requirements:**
- Install: `pip install sphinxcontrib-mermaid`

**Example files:**
- `diagrams/flowchart.mmd` - Data processing flowchart

### 3. Graphviz (.dot, .gv)
Directed graphs and architecture diagrams.

**Requirements:**
- Install: `pip install sphinx` (includes graphviz extension)
- System: Install Graphviz (`sudo apt-get install graphviz` on Ubuntu)

**Example files:**
- `diagrams/architecture.dot` - System architecture diagram

### 4. SVG (.svg)
Static vector graphics (referenced as images).

**Requirements:**
- None (built-in support)

## Usage

### Method 1: Using `diagram_includes`

```yaml
modules:
  my_page:
    title: "My Page"
    diagram_includes:
      - path: "diagrams/sequence.puml"
        title: "Optional Title"
```

### Method 2: Using `file_includes` (Auto-detection)

```yaml
modules:
  my_page:
    title: "My Page"
    file_includes:
      - "diagrams/sequence.puml"
      - "diagrams/flowchart.mmd"
```

### Method 3: Inline Diagrams

```yaml
modules:
  my_page:
    title: "My Page"
    custom_sections:
      - title: "Architecture"
        content: |
          .. graphviz::

             digraph G {
                A -> B;
             }
```

## Generating Documentation

### Method 1: Using preview.py (Recommended)

From the project root, run:
```bash
cd docs
python preview.py --example diagram_project
```

This will:
- Generate RST files from the configuration
- Build Sphinx HTML documentation
- Serve the docs at http://localhost:8000
- Press Ctrl+C to stop

### Method 2: Manual Build

1. Install required dependencies:
   ```bash
   pip install sphinx furo sphinxcontrib-plantuml sphinxcontrib-mermaid
   sudo apt-get install graphviz  # On Ubuntu/Debian
   ```

2. Generate documentation:
   ```bash
   python -m introligo examples/diagram_project/introligo_config.yaml -o examples/diagram_project/docs
   ```

3. Build Sphinx documentation:
   ```bash
   cd examples/diagram_project/docs
   sphinx-build -b html . _build/html
   ```

4. View the documentation:
   ```bash
   # Open examples/diagram_project/docs/_build/html/index.html in your browser
   ```

## Configuration Options

Introligo automatically detects which diagram extensions to enable based on the files you include. You can also manually configure diagram settings:

```yaml
sphinx:
  # Graphviz settings
  graphviz_settings:
    graphviz_output_format: "svg"
    graphviz_dot_args: ["-Grankdir=LR"]

  # PlantUML settings
  plantuml_settings:
    plantuml: "java -jar /path/to/plantuml.jar"
    plantuml_output_format: "svg"

  # Mermaid settings
  mermaid_settings:
    mermaid_output_format: "svg"
```

## Notes

- **PlantUML**: Requires Java and PlantUML JAR file, or access to a PlantUML server
- **Mermaid**: Renders client-side in the browser
- **Graphviz**: Requires Graphviz system installation for rendering
- **SVG**: No special requirements, just reference the file path

All diagram types can be mixed and matched in the same documentation project!
