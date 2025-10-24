#!/usr/bin/env python
"""Main generator class for Introligo documentation generation.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from jinja2 import Environment, Template

from .errors import IntroligoError
from .markdown_converter import (
    convert_markdown_links_to_rst,
    convert_markdown_table_to_rst,
    convert_markdown_to_rst,
)
from .page_node import PageNode
from .utils import count_display_width
from .yaml_loader import IncludeLoader

# Support both direct execution and package import
try:
    from introligo.hub import DocumentationHub
except ModuleNotFoundError:
    from .hub import DocumentationHub

logger = logging.getLogger(__name__)


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
        self.hub: Optional[DocumentationHub] = None

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
            # Show deprecation warning if using old structure without hub/discovery
            if not self.config.get("hub") and not self.config.get("discovery"):
                raise IntroligoError("Configuration must contain a 'modules' dictionary")
            else:
                # Hub mode - modules will be generated
                logger.info("Hub mode detected - modules will be auto-generated")
                self.config["modules"] = {}
                modules = {}

        # Load Doxygen configuration if present
        if "doxygen" in self.config:
            self.doxygen_config = self.config["doxygen"]
            project_name = self.doxygen_config.get("project_name", "default")
            logger.info(f"✅ Loaded Doxygen configuration: {project_name}")

        # Initialize documentation hub if configured
        if self.config.get("hub") or self.config.get("discovery"):
            self.hub = DocumentationHub(self.config_file, self.config)
            logger.info("🌐 Documentation Hub initialized")

            # Discover documentation if enabled
            if self.hub.is_enabled():
                discovered = self.hub.discover_documentation()
                if discovered:
                    # Generate hub modules and merge with existing modules
                    hub_modules = self.hub.generate_hub_modules()
                    self.config["modules"].update(hub_modules)
                    modules = self.config["modules"]
                    logger.info(f"✅ Hub added {len(hub_modules)} auto-discovered modules")

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
                logger.warning(f"Skipping invalid page config: {page_id}")
                continue

            node = PageNode(page_id, page_config)
            if node.slug in seen_slugs:
                logger.warning(f"Duplicate slug detected: {node.slug} (page {page_id})")
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
        logger.info(f"Built page tree with {len(root_nodes)} root pages")

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

{% if description -%}
{{ description }}
{%- else -%}
Documentation for {{ module if module else title }}.
{%- endif %}

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

{% if example.description -%}
{{ example.description }}

{% endif -%}
.. code-block:: {{ example.language or 'python' }}

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
{% if how_it_works.description -%}
{{ how_it_works.description }}
{%- endif %}
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
.. code-block:: {{ example.language or 'python' }}

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
.. code-block:: {{ example.language or 'bash' }}

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
            logger.info(f"Using custom template: {self.template_file}")
        else:
            template_content = self.get_default_template()
            logger.info("Using enhanced default template")

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
            content = convert_markdown_to_rst(content)
            logger.info(f"  Included markdown: {md_path_obj}")
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
            logger.info(f"  Included RST: {rst_path_obj}")
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
            logger.info(f"  Included text: {txt_path_obj}")
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
        filename = path_obj.name.upper()

        # Check for common text files without extensions (LICENSE, README, etc.)
        text_file_names = ["LICENSE", "COPYING", "AUTHORS", "CONTRIBUTORS", "NOTICE"]
        is_text_file = filename in text_file_names or filename.startswith("LICENSE")

        if suffix == ".rst":
            return self.include_rst_file(file_path)
        elif suffix == ".md":
            return self.include_markdown_file(file_path)
        elif suffix == ".tex":
            return self.include_latex_file(file_path)
        elif suffix == ".txt" or is_text_file:
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

    def _convert_markdown_to_rst(self, markdown: str, doc_type: Optional[str] = None) -> str:
        """Convert basic markdown syntax to reStructuredText.

        Args:
            markdown: Markdown content to convert.
            doc_type: Type of document (readme, changelog, license) for special handling.

        Returns:
            RST-compatible content.
        """
        lines = markdown.split("\n")
        result = []
        in_code_block = False
        code_language = ""
        first_h1_found = False

        # Special handling for changelogs
        skip_first_h1 = doc_type == "changelog"

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
                rst_table, new_index = convert_markdown_table_to_rst(lines, i)
                if rst_table:
                    result.extend(rst_table)
                    i = new_index
                    continue

            # Convert markdown links to RST (before processing headers)
            line = convert_markdown_links_to_rst(line)

            # Handle headers
            if line.startswith("# "):
                # H1
                title = line[2:].strip()
                # Skip first H1 for changelogs or if title matches doc type
                if skip_first_h1 and not first_h1_found:
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

        # Special formatting for license files
        if doc_type == "license":
            # Wrap in a literal block to preserve exact formatting
            result = [".. code-block:: text", ""] + ["   " + line for line in result]

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
                logger.warning(f"{e}")

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
                logger.warning(f"{e}")

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
                logger.warning(f"{e}")

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
                logger.warning(f"{e}")

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
                logger.info(f"  Generated: {node.title} -> {output_file}")

                if node.children:
                    child_files = self.generate_all_nodes(node.children, template, strict)
                    generated_files.update(child_files)
            except Exception as e:
                if strict:
                    raise IntroligoError(
                        f"Strict mode: failed to generate {node.page_id}: {e}"
                    ) from e
                logger.error(f"Failed to generate {node.page_id}: {e}")
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

        logger.info("Generating RST files for page tree...")
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
            logger.info("DRY RUN - Would generate:")
            for _, full_path in generated_files.values():
                logger.info(f"  {full_path}")
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
                                f"Color reference not found: {ref} "
                                f"(available shades: {list(palette_colors[color_group].keys())})"
                            )
                            resolved[key] = value
                    else:
                        logger.warning(
                            f"Color group not found: {color_group} "
                            f"(available groups: {list(palette_colors.keys())})"
                        )
                        resolved[key] = value
                else:
                    logger.warning(f"Invalid color reference format: {value}")
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
        logger.info(f"Detected project languages: {', '.join(languages)}")

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
                    logger.info(f"  Auto-added Python extension: {ext}")

        # Auto-add C/C++ extensions
        if ("c" in languages or "cpp" in languages) and "breathe" not in extensions:
            extensions.append("breathe")
            logger.info("  Auto-added C/C++ extension: breathe")

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
                    logger.info(f"  Auto-added math extension: {ext}")

        # Update the sphinx config with auto-detected extensions
        self.sphinx_config["extensions"] = extensions

    def load_sphinx_config(self) -> None:
        """Load Sphinx configuration from the config file."""
        if "sphinx" not in self.config:
            logger.info("No 'sphinx' configuration found, skipping conf.py generation")
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
            logger.warning("conf.py template not found")
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
