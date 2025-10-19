#!/usr/bin/env python3
"""
Introligo - Enhanced YAML to reStructuredText generator for Sphinx documentation.

Copyright (c) 2025 WT Tech Jakub Brzezowski

This is an open-source component of the Celin Project, freely available for use
in any project without restrictions.


This script processes YAML configuration files containing module definitions
and generates corresponding RST files for Sphinx autodoc with hierarchical organization.

Features:
- Custom page titles and descriptions
- Hierarchical module organization with subpages
- Rich content support (features, usage examples, installation, etc.)
- Automatic directory structure generation based on page hierarchy
- Automatic toctree generation
- Template-based RST generation
- Support for multiple documentation sections
- ASCII-safe folder naming
- File inclusion support with !include directive for modular configurations
- Multi-format file inclusion (RST, Markdown, LaTeX, Text) with auto-detection
- Smart Markdown to RST conversion with link handling
- Support for Python (autodoc), C, and C++ (Doxygen/Breathe) documentation

Include Directive Usage:
    Split your configuration across multiple files using the !include directive.

    Main config file (introligo_config.yaml)::

        modules:
          utils: !include utils/utils_config.yaml
          build_tools: !include build/build_config.yaml

    Module config file (utils/utils_config.yaml)::

        title: "Utility Scripts"
        description: "Collection of utilities"
        features:
          - Feature 1
          - Feature 2

    Or include entire module sections::

        modules: !include modules/all_modules.yaml

    Paths are resolved relative to the file containing the !include directive.

Language Support:
    Introligo automatically detects the project type and adds the appropriate
    Sphinx extensions. No manual extension configuration needed!

    For Python modules::

        modules:
          my_module:
            title: "My Module"
            language: python  # Optional - auto-detected from 'module' field
            module: my_package.my_module

    Auto-adds: sphinx.ext.autodoc, sphinx.ext.napoleon, sphinx.ext.viewcode

    For C/C++ with Doxygen::

        # Global Doxygen configuration
        doxygen:
          xml_path: "path/to/doxygen/xml"
          project_name: "myproject"

        modules:
          my_header:
            title: "My Header"
            language: cpp  # Auto-detected from doxygen_file
            doxygen_file: myheader.h

          my_component:
            title: "My Component"
            language: c  # Auto-detected from doxygen_files
            doxygen_files:
              - mycomponent.h
              - mycomponent.c

    Auto-adds: breathe extension

    Supported Doxygen directives:
    - doxygen_file: Document single file
    - doxygen_files: Document multiple files (list)
    - doxygen_class: Document specific class
    - doxygen_function: Document specific function
    - doxygen_namespace: Document specific namespace

    The doxygen.xml_path will be used to generate breathe_projects configuration.

    For LaTeX/Math content::

        modules:
          my_module:
            title: "Mathematical Proofs"
            latex_includes: "proofs/theorem.tex"

    Auto-adds: sphinx.ext.mathjax

    You can still manually specify extensions in your config if needed, and they
    will be preserved alongside auto-detected ones.

File Inclusion:
    Introligo now supports multiple file types for documentation composition.
    You can combine RST, Markdown, LaTeX, and text files seamlessly.

    **Unified File Inclusion (Recommended)**:
    Use the `file_includes` field for automatic type detection::

        modules:
          my_module:
            title: "My Module"
            description: "Module documentation"
            file_includes:
              - "docs/overview.rst"      # Auto-detected as RST
              - "README.md"               # Auto-detected as Markdown
              - "proofs/theorem.tex"      # Auto-detected as LaTeX
              - "notes.txt"               # Auto-detected as text

    **Type-Specific Inclusion**:
    You can also use type-specific fields for explicit control:

    RST Inclusion::

        modules:
          my_module:
            title: "My Module"
            rst_includes:
              - "docs/architecture.rst"
              - "docs/api_details.rst"

    Markdown Inclusion::

        modules:
          my_module:
            title: "My Module"
            markdown_includes:
              - "docs/user_guide.md"
              - "docs/api_reference.md"

    LaTeX Inclusion (wrapped in math directive)::

        modules:
          my_module:
            title: "My Module"
            latex_includes: "formulas/equations.tex"

    **Supported File Types**:
    - `.rst` - Included as-is (native reStructuredText)
    - `.md` - Converted to RST format with smart link handling
    - `.tex` - Wrapped in RST math directive
    - `.txt` - Wrapped in literal code block

    **Mixed Usage Example**::

        modules:
          core:
            title: "Core Module"
            description: "Main functionality"

            # Mix different inclusion methods
            file_includes: "README.md"       # Unified approach
            rst_includes: "architecture.rst"  # Type-specific
            latex_includes: "proofs.tex"      # Type-specific

    All paths are resolved relative to the configuration file.
    Content is included at the end of the generated documentation page.

Requirements:
    pip install PyYAML jinja2
    For C/C++: pip install breathe (and configure Doxygen)
"""

import argparse
import logging
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import yaml
from jinja2 import Environment, Template

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class IncludeLoader(yaml.SafeLoader):
    """YAML loader with support for !include directive.

    Allows splitting configuration across multiple files using:
        !include path/to/file.yaml

    Paths are resolved relative to the file containing the !include directive.
    """

    def __init__(self, stream):
        """Initialize the loader with file path tracking.

        Args:
            stream: YAML input stream, typically a file object.
        """
        self._root_dir = Path.cwd()

        # Track the directory of the current file for relative includes
        if hasattr(stream, "name"):
            self._current_file = Path(stream.name).resolve()
            self._root_dir = self._current_file.parent

        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.Node) -> Any:
    """Construct included YAML content.

    Args:
        loader: The YAML loader instance
        node: The YAML node containing the include path

    Returns:
        The loaded content from the included file

    Raises:
        IntroligoError: If the included file cannot be loaded
    """
    # Get the path from the node
    include_path = loader.construct_scalar(cast(yaml.ScalarNode, node))

    # Resolve path relative to the current file's directory
    if hasattr(loader, "_root_dir"):
        full_path = (loader._root_dir / include_path).resolve()
    else:
        full_path = Path(include_path).resolve()

    if not full_path.exists():
        raise IntroligoError(f"Include file not found: {full_path}")

    logger.debug(f"  Including: {full_path}")

    # Load the included file with the same loader to support nested includes
    try:
        with open(full_path, encoding="utf-8") as f:
            return yaml.load(f, Loader=IncludeLoader)
    except yaml.YAMLError as e:
        raise IntroligoError(f"Invalid YAML in included file {full_path}: {e}") from e
    except Exception as e:
        raise IntroligoError(f"Error loading included file {full_path}: {e}") from e


# Register the include constructor
yaml.add_constructor("!include", include_constructor, IncludeLoader)


class IntroligoError(Exception):
    """Custom exception for Introligo errors.

    Args:
        message: The error message.
        context: Optional additional context about the error.

    Attributes:
        message: The error message.
        context: Additional context information.
    """

    def __init__(self, message: str, context: Optional[str] = None):
        """Initialize the IntroligoError.

        Args:
            message: The error message.
            context: Optional additional context about the error.
        """
        self.message = message
        self.context = context
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error.

        Returns:
            Formatted error message with optional context.
        """
        if self.context:
            return f"{self.message}\nContext: {self.context}"
        return self.message


def slugify(text: str) -> str:
    """Convert text to ASCII-safe filesystem-compatible slug.

    Args:
        text: The text to convert to a slug.

    Returns:
        ASCII-safe slug suitable for filenames and URLs.
    """
    ascii_text = unicodedata.normalize("NFKD", text)
    ascii_text = ascii_text.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9\s\-_]", "", ascii_text.lower())
    slug = re.sub(r"[\s\-]+", "_", slug)
    slug = re.sub(r"^_+|_+$", "", slug)
    slug = re.sub(r"_+", "_", slug)
    return slug or "unnamed"


def count_display_width(text: str) -> int:
    """Calculate display width for RST underlines, accounting for emojis.

    Emojis and other wide characters need extra underline characters.
    This function estimates the visual width by counting emoji characters
    and adding extra characters to the base length.

    Args:
        text: The text to measure

    Returns:
        Estimated character width for RST underlines
    """
    # Count emojis (characters in emoji ranges)
    emoji_count = 0
    for char in text:
        code = ord(char)
        # Common emoji ranges - comprehensive coverage
        if (
            0x1F300 <= code <= 0x1F9FF  # Misc Symbols and Pictographs + Supplemental
            or 0x2600 <= code <= 0x26FF  # Misc symbols
            or 0x2700 <= code <= 0x27BF  # Dingbats
            or 0xFE00 <= code <= 0xFE0F  # Variation selectors
            or 0x1F000 <= code <= 0x1F02F  # Additional symbols
            or 0x1F600 <= code <= 0x1F64F  # Emoticons
            or 0x1F680 <= code <= 0x1F6FF  # Transport and Map
            or 0x1F900 <= code <= 0x1F9FF  # Supplemental Symbols and Pictographs
            or code == 0x2B50  # Star
            or code == 0x2705  # Check mark
            or code == 0x274C  # Cross mark
            or code == 0x2716  # Heavy multiplication X
            or code == 0x2714  # Heavy check mark
            or code == 0x2728  # Sparkles
            or code == 0x203C  # Double exclamation
            or code == 0x2049  # Exclamation question
            or code == 0x25B6  # Play button
            or code == 0x25C0  # Reverse button
            or code == 0x2139  # Information
            or 0x2194 <= code <= 0x2199  # Arrows
            or 0x21A9 <= code <= 0x21AA  # Return arrows
            or 0x231A <= code <= 0x231B  # Watch + Hourglass
            or 0x23E9 <= code <= 0x23F3  # Media buttons
            or 0x23F8 <= code <= 0x23FA
        ):  # Media buttons continued
            emoji_count += 1

    # Add extra character for each emoji (emojis display wider)
    # Use +1 per emoji for better results
    return len(text) + emoji_count


class PageNode:
    """Represents a documentation page in the hierarchy."""

    def __init__(self, page_id: str, config: Dict[str, Any], parent: Optional["PageNode"] = None):
        """Initialize a page node in the documentation tree.

        Args:
            page_id: Unique identifier for the page.
            config: Configuration dictionary for the page.
            parent: Parent PageNode, if this is a subpage.
        """
        self.page_id = page_id
        self.config = config
        self.parent = parent
        self.children: List[PageNode] = []

        self.title = config.get("title", page_id)
        self.slug = slugify(self.title)
        self.path = Path(self.slug)

    def get_rst_filename(self) -> str:
        """Get the RST filename for this page.

        Returns:
            The filename with .rst extension.
        """
        return f"{self.slug}.rst"

    def get_output_dir(self, base_generated_dir: Path) -> Path:
        """Get the full output directory path for this page (with full lineage).

        Args:
            base_generated_dir: Base directory for generated files.

        Returns:
            Full path to the output directory for this page.
        """
        lineage: List[str] = []
        node = self.parent
        while node:
            lineage.insert(0, node.slug)
            node = node.parent
        return base_generated_dir.joinpath(*lineage)

    def get_output_file(self, base_generated_dir: Path) -> Path:
        """Get the full output file path for this page.

        Args:
            base_generated_dir: Base directory for generated files.

        Returns:
            Full path to the output RST file.
        """
        return self.get_output_dir(base_generated_dir) / self.get_rst_filename()

    def get_relative_path_from(self, other_dir: Path, base_generated_dir: Path) -> str:
        """Get relative path for toctree entries.

        Args:
            other_dir: Reference directory to calculate path from (parent's directory).
            base_generated_dir: Base directory for generated files.

        Returns:
            Relative path string for use in Sphinx toctree.
        """
        self_path = self.get_output_file(base_generated_dir)
        try:
            # Calculate path relative to the parent's directory
            relative = self_path.relative_to(other_dir).with_suffix("")
        except ValueError:
            # Fallback: try relative to base_generated_dir
            try:
                relative = self_path.relative_to(base_generated_dir).with_suffix("")
            except ValueError:
                relative = self_path.with_suffix("")
        return str(relative).replace("\\", "/")

    def is_leaf(self) -> bool:
        """Check if this node is a leaf (has no children).

        Returns:
            True if the node has no children, False otherwise.
        """
        return len(self.children) == 0

    def has_module(self) -> bool:
        """Check if this node has an associated Python module.

        Returns:
            True if the config specifies a module, False otherwise.
        """
        return "module" in self.config


class IntroligoGenerator:
    """Main generator class for processing YAML and creating RST files."""

    def __init__(
        self,
        config_file: Path,
        output_dir: Path,
        template_file: Optional[Path] = None,
        dry_run: bool = False,
        strict: bool = False,
    ):
        """Initialize the Introligo generator.

        Args:
            config_file: Path to the YAML configuration file.
            output_dir: Output directory for generated documentation.
            template_file: Optional custom Jinja2 template file.
            dry_run: If True, only show what would be generated.
            strict: If True, fail on any generation error.
        """
        self.config_file = config_file
        self.output_dir = output_dir
        self.generated_dir = output_dir / "generated"
        self.template_file = template_file
        self.dry_run = dry_run
        self.strict = strict
        self.config: Dict[str, Any] = {}
        self.page_tree: List[PageNode] = []
        self.doxygen_config: Dict[str, str] = {}
        self.sphinx_config: Dict[str, Any] = {}
        self.palette_data: Dict[str, Any] = {}

    def load_config(self) -> None:
        """Load configuration with support for !include directives.

        Raises:
            IntroligoError: If the config file is not found, has invalid YAML,
                or doesn't contain required 'modules' dictionary.
        """
        if not self.config_file.exists():
            raise IntroligoError(f"Configuration file not found: {self.config_file}")

        logger.info(f"📖 Loading configuration from {self.config_file}")

        try:
            with open(self.config_file, encoding="utf-8") as f:
                self.config = yaml.load(f, Loader=IncludeLoader)
        except yaml.YAMLError as e:
            raise IntroligoError(f"Invalid YAML in {self.config_file}: {e}") from e

        if not isinstance(self.config, dict):
            raise IntroligoError("Configuration must be a YAML dictionary")

        modules = self.config.get("modules")
        if not isinstance(modules, dict):
            raise IntroligoError("Configuration must contain a 'modules' dictionary")

        # Load Doxygen configuration if present
        if "doxygen" in self.config:
            self.doxygen_config = self.config["doxygen"]
            project_name = self.doxygen_config.get("project_name", "default")
            logger.info(f"✅ Loaded Doxygen configuration: {project_name}")

        logger.info(f"✅ Loaded configuration with {len(modules)} module(s)")

    def build_page_tree(self) -> None:
        """Build hierarchical page tree from loaded configuration.

        Creates PageNode objects and establishes parent-child relationships
        based on the 'parent' field in each page's configuration.
        """
        modules = self.config["modules"]
        node_map: Dict[str, PageNode] = {}
        seen_slugs = set()

        for page_id, page_config in modules.items():
            if not isinstance(page_config, dict):
                logger.warning(f"⚠️  Skipping invalid page config: {page_id}")
                continue

            node = PageNode(page_id, page_config)
            if node.slug in seen_slugs:
                logger.warning(f"⚠️  Duplicate slug detected: {node.slug} (page {page_id})")
            seen_slugs.add(node.slug)
            node_map[page_id] = node

        root_nodes = []
        for node in node_map.values():
            parent_id = node.config.get("parent")
            if parent_id and parent_id in node_map:
                parent_node = node_map[parent_id]
                node.parent = parent_node
                parent_node.children.append(node)
            else:
                root_nodes.append(node)

        self.page_tree = root_nodes
        logger.info(f"📊 Built page tree with {len(root_nodes)} root pages")

    def get_default_template(self) -> str:
        """Get the default Jinja2 template for RST generation.

        Returns:
            Default template string with support for rich content sections.
        """
        # Load template from package resources
        template_path = Path(__file__).parent / "templates" / "default.jinja2"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")

        # Fallback to inline template if file not found
        return """..
   This file is AUTO-GENERATED by Introligo.
   DO NOT EDIT manually - changes will be overwritten.
   To modify this documentation, edit the source YAML configuration
   and regenerate using: python -m introligo <config.yaml> -o <output_dir>

{{ title }}
{{ '=' * (title|display_width) }}

{{ description if description else 'Documentation for ' + (module if module else title) + '.' }}

{% if overview %}
Overview
--------

{{ overview }}
{% endif %}

{% if features %}
Features
--------

{% for feature in features %}
* {{ feature }}
{% endfor %}
{% endif %}

{% if installation %}
Installation
------------

{% if installation is mapping %}
{% if installation.title %}
{{ installation.title }}
{{ '~' * (installation.title|display_width) }}

{% endif %}
{% if installation.steps %}
{% for step_info in installation.steps %}
**{{ step_info.step }}**

{% if step_info.description %}
{{ step_info.description }}
{% endif %}

{% if step_info.code %}
.. code-block:: bash

{{ step_info.code|indent(4, true) }}

{% endif %}
{% endfor %}
{% endif %}
{% else %}
{{ installation }}
{% endif %}
{% endif %}

{% if requirements %}
Requirements
------------

{% if requirements is string %}
{{ requirements }}
{% elif requirements is iterable %}
{% for req in requirements %}
* {{ req }}
{% endfor %}
{% endif %}
{% endif %}

{% if usage_examples %}
Usage Examples
--------------

{% for example in usage_examples %}
{{ example.title }}
{{ '~' * (example.title|display_width) }}

{{ example.description if example.description else '' }}

.. code-block:: {{ example.language if example.language else 'python' }}

{{ example.code|indent(4, true) }}

{% endfor %}
{% endif %}

{% if configuration %}
Configuration
-------------

{{ configuration }}
{% endif %}

{% if api_reference %}
API Reference
-------------

{{ api_reference }}
{% endif %}

{% if children %}
Subpages
--------

.. toctree::
   :maxdepth: 2
   :titlesonly:

{% for child in children %}
   {{ child.relative_path }}
{% endfor %}
{% endif %}

{% set has_dox = (
    doxygen_file or doxygen_files or doxygen_class or
    doxygen_function or doxygen_namespace
) -%}
{% if module or has_dox -%}
{% if not api_reference %}
API Documentation
-----------------
{% endif %}

{% if language == 'python' or not language %}
.. automodule:: {{ module }}
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:
   :special-members: __init__
{% elif language == 'c' or language == 'cpp' %}
{% if doxygen_files %}
{% for file in doxygen_files %}
.. doxygenfile:: {{ file }}
   :project: {{ global_doxygen_project }}

{% endfor %}
{% elif doxygen_file %}
.. doxygenfile:: {{ doxygen_file }}
   :project: {{ global_doxygen_project }}
{% elif doxygen_class %}
.. doxygenclass:: {{ doxygen_class }}
   :project: {{ global_doxygen_project }}
   :members:
   :undoc-members:
{% elif doxygen_function %}
.. doxygenfunction:: {{ doxygen_function }}
   :project: {{ global_doxygen_project }}
{% elif doxygen_namespace %}
.. doxygennamespace:: {{ doxygen_namespace }}
   :project: {{ global_doxygen_project }}
   :members:
   :undoc-members:
{% elif module %}
.. doxygenfile:: {{ module }}
   :project: {{ global_doxygen_project }}
{% endif %}
{% endif %}
{% endif %}

{% if notes %}
Notes
-----

{{ notes }}
{% endif %}

{% if see_also %}
See Also
--------

{% for item in see_also %}
* {{ item }}
{% endfor %}
{% endif %}

{% if references %}
References
----------

{% for ref in references %}
* {{ ref }}
{% endfor %}
{% endif %}

{% if changelog %}
Changelog
---------

{{ changelog }}
{% endif %}

{% if examples_dir %}
Additional Examples
-------------------

Examples can be found in the ``{{ examples_dir }}`` directory.
{% endif %}

{% if workflow %}
Workflow
--------

{% if workflow is mapping %}
{% if workflow.title %}
{{ workflow.title }}
{{ '~' * (workflow.title|display_width) }}

{% endif %}
{% if workflow.description %}
{{ workflow.description }}

{% endif %}
{% if workflow.steps %}
{% for step in workflow.steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
{% endif %}
{% else %}
{{ workflow }}
{% endif %}
{% endif %}

{% if how_it_works %}
How It Works
------------

{% if how_it_works is mapping %}
{% if how_it_works.title %}
{{ how_it_works.title }}
{{ '~' * (how_it_works.title|display_width) }}

{% endif %}
{{ how_it_works.description if how_it_works.description else '' }}
{% else %}
{{ how_it_works }}
{% endif %}
{% endif %}

{% if limitations %}
Limitations
-----------

{% for limitation in limitations %}
* {{ limitation }}
{% endfor %}
{% endif %}

{% if troubleshooting %}
Troubleshooting
---------------

{% for item in troubleshooting %}
{% if item is mapping %}
**{{ item.issue }}**

{{ item.solution }}

{% else %}
* {{ item }}
{% endif %}
{% endfor %}
{% endif %}

{% if best_practices %}
Best Practices
--------------

{% for practice in best_practices %}
* {{ practice }}
{% endfor %}
{% endif %}

{% if python_api %}
Python API
----------

{% for example in python_api %}
{{ example.title }}
{{ '~' * (example.title|display_width) }}

{% if example.description %}
{{ example.description }}

{% endif %}
.. code-block:: {{ example.language if example.language else 'python' }}

{{ example.code|indent(4, true) }}

{% endfor %}
{% endif %}

{% if examples %}
Examples
--------

{% for example in examples %}
{{ example.title }}
{{ '~' * (example.title|display_width) }}

{% if example.description %}
{{ example.description }}

{% endif %}
{% if example.code %}
.. code-block:: {{ example.language if example.language else 'bash' }}

{{ example.code|indent(4, true) }}

{% endif %}
{% endfor %}
{% endif %}

{% if related_tools %}
Related Tools
-------------

{% for tool in related_tools %}
{% if tool is mapping %}
* **{{ tool.name }}**: {{ tool.description }}{% if tool.url %}

  {{ tool.url }}{% endif %}
{% else %}
* {{ tool }}
{% endif %}
{% endfor %}
{% endif %}

{% if custom_sections %}
{% for section in custom_sections %}

{{ section.title }}
{{ '-' * (section.title|display_width) }}

{{ section.content }}
{% endfor %}
{% endif %}

{% if rst_includes %}
{% for rst_content in rst_includes %}

{{ rst_content }}
{% endfor %}
{% endif %}

{% if markdown_includes %}
{% for markdown_content in markdown_includes %}

{{ markdown_content }}
{% endfor %}
{% endif %}

{% if latex_includes %}
{% for latex_content in latex_includes %}

{{ latex_content }}
{% endfor %}
{% endif %}

{% if file_includes %}
{% for file_content in file_includes %}

{{ file_content }}
{% endfor %}
{% endif %}
"""

    def load_template(self) -> Template:
        """Load template and add custom filters.

        Returns:
            Configured Jinja2 Template object with custom filters.
        """
        if self.template_file and self.template_file.exists():
            template_content = self.template_file.read_text(encoding="utf-8")
            logger.info(f"📄 Using custom template: {self.template_file}")
        else:
            template_content = self.get_default_template()
            logger.info("📄 Using enhanced default template")

        # Create environment with custom filter
        env = Environment()
        env.filters["display_width"] = count_display_width

        return env.from_string(template_content)

    def process_usage_examples(self, examples: Any) -> List[Dict[str, Any]]:
        """Process usage examples to ensure they're in the right format.

        Args:
            examples: Usage examples in various formats (dict, list, or string).

        Returns:
            List of normalized example dictionaries with title, description,
            language, and code fields.
        """
        if not examples:
            return []

        processed = []
        if isinstance(examples, list):
            for example in examples:
                if isinstance(example, dict):
                    processed.append(
                        {
                            "title": example.get("title", "Example"),
                            "description": example.get("description", ""),
                            "language": example.get("language", "python"),
                            "code": example.get("code", ""),
                        }
                    )
                elif isinstance(example, str):
                    # Simple string example
                    processed.append(
                        {
                            "title": "Example",
                            "description": "",
                            "language": "python",
                            "code": example,
                        }
                    )
        elif isinstance(examples, dict):
            # Single example as dict
            processed.append(
                {
                    "title": examples.get("title", "Example"),
                    "description": examples.get("description", ""),
                    "language": examples.get("language", "python"),
                    "code": examples.get("code", ""),
                }
            )
        elif isinstance(examples, str):
            # Single example as string
            processed.append(
                {"title": "Example", "description": "", "language": "python", "code": examples}
            )

        return processed

    def include_markdown_file(self, markdown_path: str) -> str:
        """Include a markdown file and convert it to reStructuredText-compatible format.

        Args:
            markdown_path: Path to the markdown file (relative to config file).

        Returns:
            The content of the markdown file converted to RST-compatible format.

        Raises:
            IntroligoError: If the markdown file cannot be read.
        """
        # Resolve path relative to the config file's directory
        md_path_obj = Path(markdown_path)
        if not md_path_obj.is_absolute():
            md_path_obj = self.config_file.parent / markdown_path

        if not md_path_obj.exists():
            raise IntroligoError(f"Markdown file not found: {md_path_obj}")

        try:
            content = md_path_obj.read_text(encoding="utf-8")
            # Convert basic markdown to RST
            content = self._convert_markdown_to_rst(content)
            logger.info(f"  📄 Included markdown: {md_path_obj}")
            return content
        except Exception as e:
            raise IntroligoError(f"Error reading markdown file {md_path_obj}: {e}") from e

    def include_latex_file(self, latex_path: str) -> str:
        """Include a LaTeX file as a math directive in reStructuredText.

        Args:
            latex_path: Path to the LaTeX file (relative to config file).

        Returns:
            The content of the LaTeX file wrapped in RST math directive.

        Raises:
            IntroligoError: If the LaTeX file cannot be read.
        """
        # Resolve path relative to the config file's directory
        latex_path_obj = Path(latex_path)
        if not latex_path_obj.is_absolute():
            latex_path_obj = self.config_file.parent / latex_path

        if not latex_path_obj.exists():
            raise IntroligoError(f"LaTeX file not found: {latex_path_obj}")

        try:
            content = latex_path_obj.read_text(encoding="utf-8")
            # Wrap LaTeX content in RST math directive
            rst_content = self._convert_latex_to_rst(content)
            logger.info(f"  📐 Included LaTeX: {latex_path_obj}")
            return rst_content
        except Exception as e:
            raise IntroligoError(f"Error reading LaTeX file {latex_path_obj}: {e}") from e

    def include_rst_file(self, rst_path: str) -> str:
        """Include a reStructuredText file as-is.

        Args:
            rst_path: Path to the RST file (relative to config file).

        Returns:
            The content of the RST file.

        Raises:
            IntroligoError: If the RST file cannot be read.
        """
        # Resolve path relative to the config file's directory
        rst_path_obj = Path(rst_path)
        if not rst_path_obj.is_absolute():
            rst_path_obj = self.config_file.parent / rst_path

        if not rst_path_obj.exists():
            raise IntroligoError(f"RST file not found: {rst_path_obj}")

        try:
            content = rst_path_obj.read_text(encoding="utf-8")
            logger.info(f"  📝 Included RST: {rst_path_obj}")
            return content
        except Exception as e:
            raise IntroligoError(f"Error reading RST file {rst_path_obj}: {e}") from e

    def include_txt_file(self, txt_path: str) -> str:
        """Include a text file as a literal block in reStructuredText.

        Args:
            txt_path: Path to the text file (relative to config file).

        Returns:
            The content of the text file wrapped in literal block.

        Raises:
            IntroligoError: If the text file cannot be read.
        """
        # Resolve path relative to the config file's directory
        txt_path_obj = Path(txt_path)
        if not txt_path_obj.is_absolute():
            txt_path_obj = self.config_file.parent / txt_path

        if not txt_path_obj.exists():
            raise IntroligoError(f"Text file not found: {txt_path_obj}")

        try:
            content = txt_path_obj.read_text(encoding="utf-8")
            # Wrap in literal block
            rst_content = "::\n\n"
            for line in content.split("\n"):
                rst_content += "   " + line + "\n"
            logger.info(f"  📄 Included text: {txt_path_obj}")
            return rst_content
        except Exception as e:
            raise IntroligoError(f"Error reading text file {txt_path_obj}: {e}") from e

    def include_file(self, file_path: str) -> str:
        """Include a file with auto-detection based on file extension.

        Supports:
        - .rst: included as-is
        - .md: converted to RST
        - .tex: wrapped in math directive
        - .txt: wrapped in literal block

        Args:
            file_path: Path to the file (relative to config file).

        Returns:
            The processed content of the file.

        Raises:
            IntroligoError: If the file cannot be read or type is unsupported.
        """
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            path_obj = self.config_file.parent / file_path

        if not path_obj.exists():
            raise IntroligoError(f"Include file not found: {path_obj}")

        suffix = path_obj.suffix.lower()

        if suffix == ".rst":
            return self.include_rst_file(file_path)
        elif suffix == ".md":
            return self.include_markdown_file(file_path)
        elif suffix == ".tex":
            return self.include_latex_file(file_path)
        elif suffix == ".txt":
            return self.include_txt_file(file_path)
        else:
            raise IntroligoError(
                f"Unsupported file type '{suffix}' for file: {path_obj}. "
                f"Supported types: .rst, .md, .tex, .txt"
            )

    def _convert_latex_to_rst(self, latex: str) -> str:
        """Convert LaTeX content to reStructuredText math directive.

        Args:
            latex: LaTeX content to convert.

        Returns:
            RST-formatted math content.
        """
        # Strip common LaTeX document wrappers if present
        content = latex.strip()

        # Remove document class and begin/end document if present
        lines = content.split("\n")
        filtered_lines = []
        skip_preamble = False

        for line in lines:
            stripped = line.strip()
            # Skip common LaTeX document commands
            if stripped.startswith("\\documentclass") or stripped.startswith("\\usepackage"):
                skip_preamble = True
                continue
            if stripped == "\\begin{document}":
                skip_preamble = False
                continue
            if stripped == "\\end{document}":
                break
            if not skip_preamble:
                filtered_lines.append(line)

        clean_content = "\n".join(filtered_lines).strip()

        # Wrap in RST math directive
        result = [".. math::", ""]
        for line in clean_content.split("\n"):
            result.append("   " + line)
        result.append("")

        return "\n".join(result)

    def _convert_markdown_links_to_rst(self, text: str) -> str:
        """Convert markdown links to RST format.

        Handles:
        - External links: [text](http://url) -> `text <http://url>`_
        - External links with anchors: [text](http://url#anchor) -> `text <http://url#anchor>`_
        - Internal docs with anchors: [text](./file.md#anchor) -> :doc:`text <file>` (see section)
        - Internal docs: [text](./file.md) -> :doc:`file`
        - Anchor links: [text](#anchor) -> :ref:`anchor`
        - Images: ![alt](path) -> .. image:: path

        Args:
            text: Line of text potentially containing markdown links.

        Returns:
            Text with links converted to RST format.
        """
        import re

        # Handle images first: ![alt](path)
        text = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            lambda m: f"\n\n.. image:: {m.group(2)}\n   :alt: {m.group(1)}\n\n",
            text,
        )

        # Handle external links with anchors: [text](http://...#anchor or https://...#anchor)
        text = re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)", lambda m: f"`{m.group(1)} <{m.group(2)}>`_", text
        )

        # Handle internal document links with anchors: [text](./file.md#anchor)
        # Convert to :doc: reference with note about the section
        def convert_doc_link_with_anchor(match):
            link_text = match.group(1)
            file_path = match.group(2)
            anchor = match.group(3)

            # Remove .md/.rst extension and leading ./
            doc_path = file_path.replace(".md", "").replace(".rst", "")
            if doc_path.startswith("./"):
                doc_path = doc_path[2:]
            elif doc_path.startswith("../"):
                # Keep relative paths as-is
                pass

            # Create a more informative link text that includes the section
            # This helps users know which section they're linking to
            section_name = anchor.replace("-", " ").replace("_", " ").title()

            # If link text already mentions the section, use it as-is
            if link_text != section_name and section_name.lower() not in link_text.lower():
                combined_text = f"{link_text} ({section_name})"
            else:
                combined_text = link_text

            return f":doc:`{combined_text} <{doc_path}>`"

        text = re.sub(
            r"\[([^\]]+)\]\(([^)#:]+\.(?:md|rst))#([^)]+)\)", convert_doc_link_with_anchor, text
        )

        # Handle anchor-only links: [text](#anchor)
        text = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", lambda m: f":ref:`{m.group(2)}`", text)

        # Handle internal document links without anchors:
        # [text](./file.md) or [text](path/to/file.md)
        # Convert to :doc: reference without .md extension
        def convert_doc_link(match):
            link_text = match.group(1)
            file_path = match.group(2)

            # Remove .md extension and leading ./
            doc_path = file_path.replace(".md", "").replace(".rst", "")
            if doc_path.startswith("./"):
                doc_path = doc_path[2:]
            elif doc_path.startswith("../"):
                # Keep relative paths as-is for now
                pass

            # For simple cases, use the link as-is
            # Sphinx will handle the resolution
            if link_text != doc_path:
                return f":doc:`{link_text} <{doc_path}>`"
            else:
                return f":doc:`{doc_path}`"

        text = re.sub(r"\[([^\]]+)\]\(([^)#:]+\.(?:md|rst))\)", convert_doc_link, text)

        # Handle remaining local file links (without extension)
        # These might be relative paths like [text](./path/to/doc)
        text = re.sub(
            r"\[([^\]]+)\]\((\./[^)#:]+|\.\.\/[^)#:]+)\)",
            lambda m: f":doc:`{m.group(1)} <{m.group(2).replace('./', '').replace('../', '')}>`",
            text,
        )

        return text

    def _convert_markdown_table_to_rst(self, lines: list, start_index: int) -> tuple:
        """Convert markdown table to RST list-table directive.

        Args:
            lines: List of all lines in the document
            start_index: Index where the table starts

        Returns:
            Tuple of (rst_lines, end_index) where rst_lines is the converted table
            and end_index is the index after the table ends
        """

        table_lines = []
        i = start_index

        # Collect all table lines
        while i < len(lines) and "|" in lines[i]:
            table_lines.append(lines[i])
            i += 1

        if len(table_lines) < 2:
            return ([], start_index)

        # Parse table
        rows = []
        for line in table_lines:
            # Split by | and clean up
            cells = [cell.strip() for cell in line.split("|")]
            # Remove empty first/last cells from leading/trailing |
            if cells and cells[0] == "":
                cells = cells[1:]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            if cells:
                rows.append(cells)

        if len(rows) < 2:
            return ([], start_index)

        # First row is header, second is separator, rest is data
        headers = rows[0]
        data_rows = rows[2:] if len(rows) > 2 else []

        # Build RST list-table
        rst_lines = ["", ".. list-table::", "   :header-rows: 1", "   :widths: auto", ""]

        # Add header row
        rst_lines.append("   * - " + headers[0])
        for header in headers[1:]:
            rst_lines.append("     - " + header)

        # Add data rows
        for row in data_rows:
            if row:  # Skip empty rows
                rst_lines.append("   * - " + row[0])
                for cell in row[1:]:
                    rst_lines.append("     - " + cell)

        rst_lines.append("")

        return (rst_lines, i)

    def _convert_markdown_to_rst(self, markdown: str) -> str:
        """Convert basic markdown syntax to reStructuredText.

        Args:
            markdown: Markdown content to convert.

        Returns:
            RST-compatible content.
        """
        lines = markdown.split("\n")
        result = []
        in_code_block = False
        code_language = ""
        first_h1_found = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Handle code blocks
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    code_language = line.strip()[3:].strip() or "text"
                    result.append("")
                    result.append(f".. code-block:: {code_language}")
                    result.append("")
                else:
                    # End of code block
                    in_code_block = False
                    result.append("")
                i += 1
                continue

            if in_code_block:
                # Inside code block - indent by 3 spaces
                result.append("   " + line)
                i += 1
                continue

            # Handle tables (before link conversion to preserve table structure)
            if (
                "|" in line
                and not in_code_block
                and i + 1 < len(lines)
                and "|" in lines[i + 1]
                and ("-" in lines[i + 1] or "=" in lines[i + 1])
            ):
                # This is a table!
                rst_table, new_index = self._convert_markdown_table_to_rst(lines, i)
                if rst_table:
                    result.extend(rst_table)
                    i = new_index
                    continue

            # Convert markdown links to RST (before processing headers)
            line = self._convert_markdown_links_to_rst(line)

            # Handle headers
            if line.startswith("# "):
                # H1
                title = line[2:].strip()
                # Skip first H1 if it's "Changelog"
                if not first_h1_found and title.lower() == "changelog":
                    first_h1_found = True
                    i += 1
                    continue
                first_h1_found = True
                result.append("")
                result.append(title)
                result.append("=" * len(title))
                result.append("")
            elif line.startswith("## "):
                # H2
                title = line[3:].strip()
                result.append("")
                result.append(title)
                result.append("-" * len(title))
                result.append("")
            elif line.startswith("### "):
                # H3
                title = line[4:].strip()
                result.append("")
                result.append(title)
                result.append("~" * len(title))
                result.append("")
            elif line.startswith("#### "):
                # H4
                title = line[5:].strip()
                result.append("")
                result.append(title)
                result.append("^" * len(title))
                result.append("")
            else:
                # Regular line
                result.append(line)

            i += 1

        return "\n".join(result)

    def generate_rst_content(self, node: PageNode, template: Template) -> str:
        """Generate RST content with enhanced features support.

        Args:
            node: PageNode containing page configuration.
            template: Jinja2 template for rendering.

        Returns:
            Generated RST content as a string.
        """
        config = node.config

        # Process children for toctree
        children_info = []
        if node.children:
            for child in node.children:
                current_output_dir = node.get_output_dir(self.generated_dir)
                relative_path = child.get_relative_path_from(current_output_dir, self.generated_dir)
                children_info.append({"title": child.title, "relative_path": relative_path})

        # Build context with all possible fields
        # Handle doxygen_files (list) or doxygen_file (single string)
        doxygen_file = config.get("doxygen_file", "")
        doxygen_files = config.get("doxygen_files", [])

        # If doxygen_file is set but doxygen_files is not, convert to list
        if doxygen_file and not doxygen_files:
            doxygen_files = [doxygen_file]

        # Process markdown includes
        markdown_includes = config.get("markdown_includes", [])
        if isinstance(markdown_includes, str):
            markdown_includes = [markdown_includes]

        markdown_content = []
        for md_path in markdown_includes:
            try:
                content = self.include_markdown_file(md_path)
                markdown_content.append(content)
            except IntroligoError as e:
                logger.warning(f"⚠️  {e}")

        # Process LaTeX includes
        latex_includes = config.get("latex_includes", [])
        if isinstance(latex_includes, str):
            latex_includes = [latex_includes]

        latex_content = []
        for latex_path in latex_includes:
            try:
                content = self.include_latex_file(latex_path)
                latex_content.append(content)
            except IntroligoError as e:
                logger.warning(f"⚠️  {e}")

        # Process RST includes
        rst_includes = config.get("rst_includes", [])
        if isinstance(rst_includes, str):
            rst_includes = [rst_includes]

        rst_content = []
        for rst_path in rst_includes:
            try:
                content = self.include_rst_file(rst_path)
                rst_content.append(content)
            except IntroligoError as e:
                logger.warning(f"⚠️  {e}")

        # Process generic file includes (auto-detection)
        file_includes = config.get("file_includes", [])
        if isinstance(file_includes, str):
            file_includes = [file_includes]

        file_content = []
        for file_path in file_includes:
            try:
                content = self.include_file(file_path)
                file_content.append(content)
            except IntroligoError as e:
                logger.warning(f"⚠️  {e}")

        context = {
            "title": node.title,
            "module": config.get("module", ""),
            "language": config.get("language", "python"),
            "doxygen_file": doxygen_file,
            "doxygen_files": doxygen_files,
            "doxygen_class": config.get("doxygen_class", ""),
            "doxygen_function": config.get("doxygen_function", ""),
            "doxygen_namespace": config.get("doxygen_namespace", ""),
            "global_doxygen_project": self.doxygen_config.get("project_name", "default"),
            "description": config.get("description", ""),
            "overview": config.get("overview", ""),
            "features": config.get("features", []),
            "installation": config.get("installation", ""),
            "requirements": config.get("requirements", ""),
            "usage_examples": self.process_usage_examples(config.get("usage_examples")),
            "configuration": config.get("configuration", ""),
            "api_reference": config.get("api_reference", ""),
            "children": children_info,
            "notes": config.get("notes", ""),
            "see_also": config.get("see_also", []),
            "references": config.get("references", []),
            "changelog": config.get("changelog", ""),
            "examples_dir": config.get("examples_dir", ""),
            "workflow": config.get("workflow", ""),
            "how_it_works": config.get("how_it_works", ""),
            "limitations": config.get("limitations", []),
            "troubleshooting": config.get("troubleshooting", []),
            "best_practices": config.get("best_practices", []),
            "python_api": self.process_usage_examples(config.get("python_api")),
            "examples": self.process_usage_examples(config.get("examples")),
            "related_tools": config.get("related_tools", []),
            "custom_sections": config.get("custom_sections", []),
            "markdown_includes": markdown_content,
            "latex_includes": latex_content,
            "rst_includes": rst_content,
            "file_includes": file_content,
        }

        # Clean up empty values, but keep language field
        context = {k: v for k, v in context.items() if v or k == "language"}

        return template.render(context)

    def generate_index(self, root_nodes: List[PageNode]) -> str:
        """Generate the main index.rst file.

        Args:
            root_nodes: List of root PageNode objects to include in index.

        Returns:
            Generated index.rst content as a string.
        """
        index_config = self.config.get("index", {})
        title = index_config.get("title", "API Documentation")
        description = index_config.get("description", "Generated API documentation.")
        overview = index_config.get("overview", "")

        content = f"""..
   This file is AUTO-GENERATED by Introligo.
   DO NOT EDIT manually - changes will be overwritten.
   To modify this documentation, edit the source YAML configuration
   and regenerate using: python -m introligo <config.yaml> -o <output_dir>

{title}
{"=" * count_display_width(title)}

{description}

"""
        if overview:
            content += f"""{overview}

"""

        content += """.. toctree::
   :maxdepth: 2
   :caption: Documentation:

"""
        for node in sorted(root_nodes, key=lambda n: n.title):
            relative_path = node.get_relative_path_from(self.generated_dir, self.generated_dir)
            content += f"   generated/{relative_path}\n"

        # Add footer note
        content += """
.. note::
   This documentation was generated from yaml composition using the
   **Introligo** tool created by **WT Tech Jakub Brzezowski**.

"""

        # Add any additional index sections
        if "custom_sections" in index_config:
            for section in index_config["custom_sections"]:
                section_title = section.get("title", "Section")
                content += f"""
{section_title}
{"-" * count_display_width(section_title)}

{section.get("content", "")}
"""

        return content

    def generate_all_nodes(
        self,
        nodes: List[PageNode],
        template: Template,
        strict: bool = False,
    ) -> Dict[str, Tuple[str, Path]]:
        """Generate all RST files for the page tree.

        Args:
            nodes: List of PageNode objects to generate.
            template: Jinja2 template for rendering.
            strict: If True, raise exception on generation errors.

        Returns:
            Dictionary mapping file paths to tuples of (content, Path).

        Raises:
            IntroligoError: If strict mode is enabled and generation fails.
        """
        generated_files = {}
        for node in nodes:
            try:
                content = self.generate_rst_content(node, template)
                output_file = node.get_output_file(self.generated_dir)
                generated_files[str(output_file)] = (content, output_file)
                logger.info(f"  📄 Generated: {node.title} -> {output_file}")

                if node.children:
                    child_files = self.generate_all_nodes(node.children, template, strict)
                    generated_files.update(child_files)
            except Exception as e:
                if strict:
                    raise IntroligoError(
                        f"Strict mode: failed to generate {node.page_id}: {e}"
                    ) from e
                logger.error(f"⛔ Failed to generate {node.page_id}: {e}")
                continue
        return generated_files

    def generate_all(self) -> Dict[str, Tuple[str, Path]]:
        """Main generation method.

        Loads configuration, builds page tree, and generates all RST files.

        Returns:
            Dictionary mapping file paths to tuples of (content, Path).
        """
        self.load_config()
        self.load_sphinx_config()
        self.build_page_tree()
        template = self.load_template()

        logger.info("🔄 Generating RST files for page tree...")
        generated_files = self.generate_all_nodes(self.page_tree, template, self.strict)

        if self.config.get("generate_index", True):
            index_content = self.generate_index(self.page_tree)
            index_path = self.output_dir / "index.rst"
            generated_files[str(index_path)] = (index_content, index_path)
            logger.info("  📋 Generated: index.rst")

        return generated_files

    def write_files(self, generated_files: Dict[str, Tuple[str, Path]]) -> None:
        """Write all generated files to disk.

        Args:
            generated_files: Dictionary mapping file paths to (content, Path) tuples.
        """
        if self.dry_run:
            logger.info("🔍 DRY RUN - Would generate:")
            for _, full_path in generated_files.values():
                logger.info(f"  📄 {full_path}")
            return

        for content, full_path in generated_files.values():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            logger.info(f"✅ Wrote: {full_path}")

    def generate_breathe_config(self) -> Optional[str]:
        """Generate Breathe configuration snippet for Sphinx conf.py.

        Returns:
            Breathe configuration snippet as a string, or None if no Doxygen config.
        """
        if not self.doxygen_config:
            return None

        project_name = self.doxygen_config.get("project_name", "default")
        xml_path = self.doxygen_config.get("xml_path", "")

        if not xml_path:
            return None

        # Convert to absolute path if relative
        # Relative paths are resolved from the config file's directory
        xml_path_obj = Path(xml_path)
        if not xml_path_obj.is_absolute():
            # Resolve relative to config file directory
            xml_path_obj = self.config_file.parent / xml_path
        xml_path_str = str(xml_path_obj.resolve())

        config = f"""# Breathe Configuration for Doxygen Integration
# AUTO-GENERATED by Introligo
#
# WARNING: This file is AUTO-GENERATED and should NOT be edited manually.
# Any manual changes will be OVERWRITTEN when regenerated.
#
# To modify Breathe configuration:
# 1. Edit your introligo YAML configuration file (doxygen section)
# 2. Regenerate using: python -m introligo <config.yaml> -o <output_dir>

from pathlib import Path

breathe_projects = {{
    "{project_name}": r"{xml_path_str}"
}}
breathe_default_project = "{project_name}"
"""
        return config

    def load_palette(self, palette_name: str) -> Dict[str, Any]:
        """Load a color palette from the palettes directory.

        Args:
            palette_name: Name of the palette (without .yaml extension) or path to palette file.

        Returns:
            Dictionary containing palette data.

        Raises:
            IntroligoError: If the palette file cannot be loaded.
        """
        # Check if it's a full path or just a name
        palette_path = Path(palette_name)

        if not palette_path.exists():
            # Try as a built-in palette
            package_palette = Path(__file__).parent / "palettes" / f"{palette_name}.yaml"
            if package_palette.exists():
                palette_path = package_palette
            else:
                # Try relative to config file
                config_relative = self.config_file.parent / palette_name
                if config_relative.exists():
                    palette_path = config_relative
                else:
                    raise IntroligoError(
                        f"Palette not found: {palette_name}. "
                        f"Tried: {palette_path}, {package_palette}, {config_relative}"
                    )

        try:
            with open(palette_path, encoding="utf-8") as f:
                palette_data: Dict[str, Any] = yaml.load(f, Loader=IncludeLoader)
                logger.info(f"✅ Loaded palette: {palette_data.get('name', palette_name)}")
                return palette_data
        except Exception as e:
            raise IntroligoError(f"Error loading palette {palette_path}: {e}") from e

    def resolve_color_references(
        self, palette_colors: Dict[str, Any], theme_mapping: Dict[str, str]
    ) -> Dict[str, str]:
        """Resolve color references in theme mapping.

        Color references are in the format {color_group.shade}, e.g., {cosmic_dawn.3}.

        Args:
            palette_colors: Dictionary of color definitions from palette.
            theme_mapping: Dictionary of theme variables with potential color references.

        Returns:
            Dictionary with all color references resolved to actual hex values.
        """
        resolved = {}
        for key, value in theme_mapping.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                # Extract reference like {cosmic_dawn.3}
                ref = value[1:-1]  # Remove braces
                parts = ref.split(".")

                if len(parts) == 2:
                    color_group, shade = parts
                    if color_group in palette_colors:
                        # Try shade as both string and int
                        color_value = palette_colors[color_group].get(
                            shade,
                            palette_colors[color_group].get(
                                int(shade) if shade.isdigit() else shade
                            ),
                        )
                        if color_value:
                            resolved[key] = color_value
                        else:
                            logger.warning(
                                f"⚠️  Color reference not found: {ref} "
                                f"(available shades: {list(palette_colors[color_group].keys())})"
                            )
                            resolved[key] = value
                    else:
                        logger.warning(
                            f"⚠️  Color group not found: {color_group} "
                            f"(available groups: {list(palette_colors.keys())})"
                        )
                        resolved[key] = value
                else:
                    logger.warning(f"⚠️  Invalid color reference format: {value}")
                    resolved[key] = value
            else:
                resolved[key] = value

        return resolved

    def flatten_palette_colors(self, palette_colors: Dict[str, Any]) -> Dict[str, str]:
        """Flatten nested color palette into CSS variable format.

        Args:
            palette_colors: Nested color definitions from palette.

        Returns:
            Flattened dictionary with CSS variable names.
        """
        flattened = {}
        for group_name, shades in palette_colors.items():
            if isinstance(shades, dict):
                for shade, color in shades.items():
                    var_name = f"{group_name}-{shade}"
                    flattened[var_name] = color
        return flattened

    def detect_project_languages(self) -> set:
        """Detect programming languages used in the project.

        Returns:
            Set of language strings found in module configurations.
        """
        languages = set()
        modules = self.config.get("modules", {})

        def scan_module(module_config):
            """Recursively scan module configuration for language field."""
            if isinstance(module_config, dict):
                # Check if this module has a language field
                if "language" in module_config:
                    languages.add(module_config["language"])
                # Check if this module has Python-specific fields
                elif "module" in module_config:
                    languages.add("python")
                # Check if this module has C/C++-specific fields
                if (
                    any(
                        key in module_config
                        for key in [
                            "doxygen_file",
                            "doxygen_files",
                            "doxygen_class",
                            "doxygen_function",
                            "doxygen_namespace",
                        ]
                    )
                    and "language" not in module_config
                ):
                    # Default to C if no language specified for Doxygen content
                    languages.add("c")

        for module_config in modules.values():
            scan_module(module_config)

        # If no languages detected, assume Python as default
        if not languages:
            languages.add("python")

        return languages

    def auto_configure_extensions(self) -> None:
        """Automatically configure Sphinx extensions based on detected project types."""
        if "sphinx" not in self.config:
            return

        # Get existing extensions or initialize empty list
        extensions = self.sphinx_config.get("extensions", [])

        # Detect languages used in the project
        languages = self.detect_project_languages()
        logger.info(f"🔍 Detected project languages: {', '.join(languages)}")

        # Auto-add Python extensions
        if "python" in languages or not languages:
            python_extensions = [
                "sphinx.ext.autodoc",
                "sphinx.ext.napoleon",
                "sphinx.ext.viewcode",
            ]
            for ext in python_extensions:
                if ext not in extensions:
                    extensions.append(ext)
                    logger.info(f"  ✨ Auto-added Python extension: {ext}")

        # Auto-add C/C++ extensions
        if ("c" in languages or "cpp" in languages) and "breathe" not in extensions:
            extensions.append("breathe")
            logger.info("  ✨ Auto-added C/C++ extension: breathe")

        # Auto-add LaTeX/Math extensions if latex_includes are found
        has_latex = any(
            "latex_includes" in module_config
            for module_config in self.config.get("modules", {}).values()
            if isinstance(module_config, dict)
        )
        if has_latex:
            math_extensions = ["sphinx.ext.mathjax"]
            for ext in math_extensions:
                if ext not in extensions:
                    extensions.append(ext)
                    logger.info(f"  ✨ Auto-added math extension: {ext}")

        # Update the sphinx config with auto-detected extensions
        self.sphinx_config["extensions"] = extensions

    def load_sphinx_config(self) -> None:
        """Load Sphinx configuration from the config file."""
        if "sphinx" not in self.config:
            logger.info("ℹ️  No 'sphinx' configuration found, skipping conf.py generation")
            return

        self.sphinx_config = self.config["sphinx"]

        # Auto-configure extensions based on project type
        self.auto_configure_extensions()

        # Load palette if specified
        palette_ref = self.sphinx_config.get("palette")
        if palette_ref:
            if isinstance(palette_ref, str):
                # Load palette from file
                self.palette_data = self.load_palette(palette_ref)
            elif isinstance(palette_ref, dict):
                # Inline palette definition
                self.palette_data = palette_ref

        logger.info("✅ Loaded Sphinx configuration")

    def generate_conf_py(self) -> Optional[str]:
        """Generate conf.py content from Sphinx configuration.

        Returns:
            Generated conf.py content as a string, or None if no Sphinx config.
        """
        if not self.sphinx_config:
            return None

        # Load conf.py template
        template_path = Path(__file__).parent / "templates" / "conf.py.jinja2"
        if not template_path.exists():
            logger.warning("⚠️  conf.py template not found")
            return None

        template_content = template_path.read_text(encoding="utf-8")
        env = Environment()
        template = env.from_string(template_content)

        # Prepare template context
        context = {
            "config_file_name": self.config_file.name,
            "sphinx": self.sphinx_config,
            "has_breathe": bool(self.doxygen_config),
        }

        # Process palette if available
        if self.palette_data:
            palette_colors = self.palette_data.get("colors", {})
            light_mode = self.palette_data.get("light_mode", {})
            dark_mode = self.palette_data.get("dark_mode", {})

            # Resolve color references
            if palette_colors:
                context["palette_raw_colors"] = self.flatten_palette_colors(palette_colors)
                context["light_palette"] = self.resolve_color_references(palette_colors, light_mode)
                context["dark_palette"] = self.resolve_color_references(palette_colors, dark_mode)
            else:
                context["light_palette"] = light_mode
                context["dark_palette"] = dark_mode

            context["has_light_palette"] = bool(light_mode)
            context["has_dark_palette"] = bool(dark_mode)
            context["palette_name"] = self.palette_data.get("name", "")
        else:
            context["has_light_palette"] = False
            context["has_dark_palette"] = False

        # Check if we have any theme options
        context["has_theme_options"] = bool(
            self.sphinx_config.get("html_theme_options")
            or context.get("has_light_palette")
            or context.get("has_dark_palette")
        )

        return template.render(context)


def main() -> None:
    """Main entry point for the Introligo command-line tool.

    Parses command-line arguments and executes the documentation generation.
    """
    parser = argparse.ArgumentParser(
        description="Introligo - Generate rich Sphinx RST documentation from YAML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s config.yaml -o docs
  %(prog)s config.yaml -o docs --dry-run
  %(prog)s config.yaml -o docs -t custom_template.jinja2
        """,
    )
    parser.add_argument("config", type=Path, help="YAML configuration file")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("docs"), help="Output directory (default: docs)"
    )
    parser.add_argument("-t", "--template", type=Path, help="Custom Jinja2 template file")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be generated without creating files"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Fail immediately if any page fails to generate"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    try:
        generator = IntroligoGenerator(
            config_file=args.config,
            output_dir=args.output,
            template_file=args.template,
            dry_run=args.dry_run,
            strict=args.strict,
        )
        generated_files = generator.generate_all()
        generator.write_files(generated_files)

        # Generate and write Breathe configuration if Doxygen is configured
        breathe_config = generator.generate_breathe_config()
        if breathe_config and not args.dry_run:
            generator.generated_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py to make it a package
            init_path = generator.generated_dir / "__init__.py"
            init_content = '''"""AUTO-GENERATED documentation files by Introligo.

WARNING: This directory and all files within are AUTO-GENERATED.
DO NOT EDIT manually - changes will be OVERWRITTEN.

To modify the documentation:
1. Edit your introligo YAML configuration file
2. Regenerate using: python -m introligo <config.yaml> -o <output_dir>
"""
'''
            init_path.write_text(init_content, encoding="utf-8")

            breathe_config_path = generator.generated_dir / "breathe_config.py"
            breathe_config_path.write_text(breathe_config, encoding="utf-8")
            logger.info(f"📝 Generated Breathe configuration: {breathe_config_path}")
            logger.info("💡 Import this in your conf.py: from generated.breathe_config import *")

        # Generate and write conf.py if Sphinx configuration is present
        conf_py_content = generator.generate_conf_py()
        if conf_py_content:
            if args.dry_run:
                logger.info("🔍 Would generate conf.py")
            else:
                conf_py_path = generator.output_dir / "conf.py"
                conf_py_path.write_text(conf_py_content, encoding="utf-8")
                logger.info(f"📝 Generated Sphinx configuration: {conf_py_path}")
                logger.info(
                    "💡 Your conf.py has been auto-generated. "
                    "To modify it, edit your introligo config and regenerate."
                )

        if not args.dry_run:
            logger.info(f"🎉 Successfully generated {len(generated_files)} RST files!")
            logger.info(f"📁 Output directory: {args.output}")
            logger.info("💡 Run 'sphinx-build' or your preview script to build HTML")
        else:
            logger.info(f"🔍 Dry run complete - would generate {len(generated_files)} files")

    except IntroligoError as e:
        logger.error(f"⛔ {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"⛔ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
