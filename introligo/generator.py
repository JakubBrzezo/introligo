#!/usr/bin/env python
"""Main generator class for Introligo documentation generation.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from jinja2 import Environment, Template

from .errors import IntroligoError
from .godoc_extractor import GoDocExtractor
from .javadoc_extractor import JavaDocExtractor
from .markdown_converter import (
    convert_markdown_to_rst,
)
from .page_node import PageNode
from .protobuf_diagram_generator import generate_proto_diagrams
from .protodoc_extractor import ProtoDocExtractor
from .rustdoc_extractor import RustDocExtractor
from .utils import (
    convert_graphviz_to_rst,
    convert_mermaid_to_rst,
    convert_plantuml_to_rst,
    convert_svg_to_rst,
    count_display_width,
    process_rst_directives,
)
from .yaml_loader import IncludeLoader

# Support both direct execution and package import
try:
    from introligo.hub import DocumentationHub
except ModuleNotFoundError:
    from .hub import DocumentationHub

logger = logging.getLogger(__name__)


@dataclass
class PathConfig:
    """Configuration for file paths used by the generator."""

    config_file: Path
    output_dir: Path
    generated_dir: Path
    template_file: Optional[Path] = None


@dataclass
class GeneratorOptions:
    """Options for controlling generator behavior."""

    dry_run: bool = False
    strict: bool = False


@dataclass
class ExtensionFlags:
    """Flags indicating which Sphinx extensions are available."""

    has_plantuml_extension: bool = False
    has_mermaid_extension: bool = False


class IntroligoGenerator:
    """Main generator class for processing YAML and creating RST files."""

    def __init__(
        self,
        config_file: Path,
        output_dir: Path,
        *,
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
        self.paths = PathConfig(
            config_file=config_file,
            output_dir=output_dir,
            generated_dir=output_dir / "generated",
            template_file=template_file,
        )
        self.options = GeneratorOptions(dry_run=dry_run, strict=strict)
        self.extensions = ExtensionFlags()
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
        if not self.paths.config_file.exists():
            raise IntroligoError(f"Configuration file not found: {self.paths.config_file}")

        logger.info(f"📖 Loading configuration from {self.paths.config_file}")

        try:
            with open(self.paths.config_file, encoding="utf-8") as f:
                # Using custom IncludeLoader for YAML file inclusion feature
                self.config = yaml.load(f, Loader=IncludeLoader)  # nosec B506
        except yaml.YAMLError as e:
            raise IntroligoError(f"Invalid YAML in {self.paths.config_file}: {e}") from e

        if not isinstance(self.config, dict):
            raise IntroligoError("Configuration must be a YAML dictionary")

        modules = self.config.get("modules")
        if not isinstance(modules, dict):
            # Show deprecation warning if using old structure without hub/discovery
            if not self.config.get("hub") and not self.config.get("discovery"):
                raise IntroligoError("Configuration must contain a 'modules' dictionary")
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
            self.hub = DocumentationHub(self.paths.config_file, self.config)
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
{% set has_godoc = (
    godoc_package or godoc_packages or godoc_function or godoc_type
) -%}
{% set has_javadoc = (
    java_package or java_packages or java_source_files or javadoc_path
) -%}
{% set has_rustdoc = (
    rustdoc_crate or rustdoc_path
) -%}
{% if module or has_dox or has_godoc or has_javadoc or has_rustdoc -%}
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
{% elif language == 'go' %}
{% if godoc_extracted_content %}
{{ godoc_extracted_content }}
{% else %}
.. note::

   Go documentation extraction was not available. The package may not be installed
   or Go may not be available on the build system.

{% if godoc_package %}
   **Package:** ``{{ godoc_package }}``

   View full documentation at: https://pkg.go.dev/{{ godoc_package }}
{% elif godoc_packages %}
   **Packages:**

{% for package in godoc_packages %}
   * ``{{ package }}`` - https://pkg.go.dev/{{ package }}
{% endfor %}
{% endif %}
{% endif %}
{% elif language == 'java' %}
{% if javadoc_extracted_content %}
{{ javadoc_extracted_content }}
{% else %}
.. note::

   Java documentation extraction was not available. This can happen if:

   - The source files are not accessible
   - Java/javadoc is not installed on the system

{% if java_package %}
   **Package:** ``{{ java_package }}``

   To generate documentation:

   .. code-block:: bash

      javadoc -d docs {{ java_package }}

{% elif java_packages %}
   **Packages:**

{% for package in java_packages %}
   * ``{{ package }}``
{% endfor %}

   To generate documentation:

   .. code-block:: bash

      javadoc -d docs {{ java_packages|join(' ') }}

{% elif java_source_files %}
   **Source Files:**

{% for file in java_source_files %}
   * ``{{ file }}``
{% endfor %}

   To generate documentation:

   .. code-block:: bash

      javadoc -d docs {{ java_source_files|join(' ') }}

{% endif %}
{% endif %}
{% elif language == 'rust' %}
{% if rustdoc_extracted_content %}
{{ rustdoc_extracted_content }}
{% else %}
.. note::

   Rust documentation extraction was not available. This can happen if:

   - Cargo is not installed on the system
   - The crate path is not accessible
   - The crate has build errors

{% if rustdoc_crate %}
   **Crate:** ``{{ rustdoc_crate }}``

   To generate documentation:

   .. code-block:: bash

      cargo doc --open

   Or view at: https://docs.rs/{{ rustdoc_crate }}

{% elif rustdoc_path %}
   **Crate Path:** ``{{ rustdoc_path }}``

   To generate documentation:

   .. code-block:: bash

      cd {{ rustdoc_path }} && cargo doc --open

{% endif %}
{% endif %}
{% endif %}
{% elif language == 'protobuf' %}
{% if protodoc_extracted_content %}
{{ protodoc_extracted_content }}
{% else %}
.. note::

   Protobuf documentation extraction was not available. This can happen if:

   - protoc is not installed on the system
   - protoc-gen-doc plugin is not installed
   - The proto path is not accessible
   - The proto files have syntax errors

{% if proto_package %}
   **Package:** ``{{ proto_package }}``
{% endif %}
{% if proto_files %}
   **Proto Files:**

{% for file in proto_files %}
   * ``{{ file }}``
{% endfor %}
{% endif %}

   To generate documentation:

   .. code-block:: bash

      # Install protoc-gen-doc
      go install github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc@latest

      # Generate documentation
      protoc --doc_out=html,index.html:docs \\
          {{ proto_files|join(' ') if proto_files else '*.proto' }}

   Or view the proto files directly in your project at ``{{ proto_path }}``.

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

{% if diagram_includes %}
{% for diagram_content in diagram_includes %}

{{ diagram_content }}
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
        if self.paths.template_file and self.paths.template_file.exists():
            template_content = self.paths.template_file.read_text(encoding="utf-8")
            logger.info(f"Using custom template: {self.paths.template_file}")
        else:
            template_content = self.get_default_template()
            logger.info("Using enhanced default template")

        # Create environment with custom filter
        # Generating RST documentation, not HTML, XSS not applicable
        env = Environment()  # nosec B701
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
            md_path_obj = self.paths.config_file.parent / markdown_path

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
            latex_path_obj = self.paths.config_file.parent / latex_path

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
            rst_path_obj = self.paths.config_file.parent / rst_path

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
            txt_path_obj = self.paths.config_file.parent / txt_path

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

    def include_plantuml_file(self, plantuml_path: str, title: str = "") -> str:
        """Include a PlantUML file and convert it to RST with uml directive.

        Args:
            plantuml_path: Path to the PlantUML file (relative to config file).
            title: Optional title for the diagram.

        Returns:
            The content of the PlantUML file wrapped in RST uml directive.

        Raises:
            IntroligoError: If the PlantUML file cannot be read.
        """
        # Resolve path relative to the config file's directory
        puml_path_obj = Path(plantuml_path)
        if not puml_path_obj.is_absolute():
            puml_path_obj = self.paths.config_file.parent / plantuml_path

        if not puml_path_obj.exists():
            raise IntroligoError(f"PlantUML file not found: {puml_path_obj}")

        try:
            content = puml_path_obj.read_text(encoding="utf-8")
            rst_content = convert_plantuml_to_rst(
                content, title, self.extensions.has_plantuml_extension
            )
            logger.info(f"  📊 Included PlantUML: {puml_path_obj}")
            return rst_content
        except Exception as e:
            raise IntroligoError(f"Error reading PlantUML file {puml_path_obj}: {e}") from e

    def include_mermaid_file(self, mermaid_path: str, title: str = "") -> str:
        """Include a Mermaid file and convert it to RST with mermaid directive.

        Args:
            mermaid_path: Path to the Mermaid file (relative to config file).
            title: Optional title for the diagram.

        Returns:
            The content of the Mermaid file wrapped in RST mermaid directive.

        Raises:
            IntroligoError: If the Mermaid file cannot be read.
        """
        # Resolve path relative to the config file's directory
        mmd_path_obj = Path(mermaid_path)
        if not mmd_path_obj.is_absolute():
            mmd_path_obj = self.paths.config_file.parent / mermaid_path

        if not mmd_path_obj.exists():
            raise IntroligoError(f"Mermaid file not found: {mmd_path_obj}")

        try:
            content = mmd_path_obj.read_text(encoding="utf-8")
            rst_content = convert_mermaid_to_rst(
                content, title, self.extensions.has_mermaid_extension
            )
            logger.info(f"  📊 Included Mermaid: {mmd_path_obj}")
            return rst_content
        except Exception as e:
            raise IntroligoError(f"Error reading Mermaid file {mmd_path_obj}: {e}") from e

    def include_graphviz_file(self, graphviz_path: str, title: str = "") -> str:
        """Include a Graphviz DOT file and convert it to RST with graphviz directive.

        Args:
            graphviz_path: Path to the Graphviz file (relative to config file).
            title: Optional title for the diagram.

        Returns:
            The content of the Graphviz file wrapped in RST graphviz directive.

        Raises:
            IntroligoError: If the Graphviz file cannot be read.
        """
        # Resolve path relative to the config file's directory
        dot_path_obj = Path(graphviz_path)
        if not dot_path_obj.is_absolute():
            dot_path_obj = self.paths.config_file.parent / graphviz_path

        if not dot_path_obj.exists():
            raise IntroligoError(f"Graphviz file not found: {dot_path_obj}")

        try:
            content = dot_path_obj.read_text(encoding="utf-8")
            rst_content = convert_graphviz_to_rst(content, title)
            logger.info(f"  📊 Included Graphviz: {dot_path_obj}")
            return rst_content
        except Exception as e:
            raise IntroligoError(f"Error reading Graphviz file {dot_path_obj}: {e}") from e

    def include_svg_file(self, svg_path: str, title: str = "", alt_text: str = "") -> str:
        """Include an SVG file as an image in RST.

        Args:
            svg_path: Path to the SVG file (relative to config file).
            title: Optional title for the diagram.
            alt_text: Optional alt text for the image.

        Returns:
            RST image directive for the SVG file.

        Raises:
            IntroligoError: If the SVG file cannot be found.
        """
        # Resolve path relative to the config file's directory
        svg_path_obj = Path(svg_path)
        if not svg_path_obj.is_absolute():
            svg_path_obj = self.paths.config_file.parent / svg_path

        if not svg_path_obj.exists():
            raise IntroligoError(f"SVG file not found: {svg_path_obj}")

        try:
            # For SVG, we just reference the path, not read the content
            rst_content = convert_svg_to_rst(svg_path, title, alt_text)
            logger.info(f"  📊 Included SVG: {svg_path_obj}")
            return rst_content
        except Exception as e:
            raise IntroligoError(f"Error processing SVG file {svg_path_obj}: {e}") from e

    def include_file(self, file_path: str) -> str:
        """Include a file with auto-detection based on file extension.

        Supports:
        - .rst: included as-is
        - .md: converted to RST
        - .tex: wrapped in math directive
        - .txt: wrapped in literal block
        - .puml, .plantuml: PlantUML diagram
        - .mmd, .mermaid: Mermaid diagram
        - .dot, .gv: Graphviz diagram
        - .svg: SVG image

        Args:
            file_path: Path to the file (relative to config file).

        Returns:
            The processed content of the file.

        Raises:
            IntroligoError: If the file cannot be read or type is unsupported.
        """
        path_obj = Path(file_path)
        if not path_obj.is_absolute():
            path_obj = self.paths.config_file.parent / file_path

        if not path_obj.exists():
            raise IntroligoError(f"Include file not found: {path_obj}")

        suffix = path_obj.suffix.lower()
        filename = path_obj.name.upper()

        # Check for common text files without extensions (LICENSE, README, etc.)
        text_file_names = ["LICENSE", "COPYING", "AUTHORS", "CONTRIBUTORS", "NOTICE"]
        is_text_file = filename in text_file_names or filename.startswith("LICENSE")

        # Map file extensions to their handler methods
        extension_handlers = {
            ".rst": self.include_rst_file,
            ".md": self.include_markdown_file,
            ".tex": self.include_latex_file,
            ".txt": self.include_txt_file,
            ".puml": self.include_plantuml_file,
            ".plantuml": self.include_plantuml_file,
            ".mmd": self.include_mermaid_file,
            ".mermaid": self.include_mermaid_file,
            ".dot": self.include_graphviz_file,
            ".gv": self.include_graphviz_file,
            ".svg": self.include_svg_file,
        }

        # Handle text files without extensions
        if is_text_file:
            return self.include_txt_file(file_path)

        # Dispatch to appropriate handler
        handler = extension_handlers.get(suffix)
        if handler:
            return handler(file_path)  # type: ignore[no-any-return, operator]

        raise IntroligoError(
            f"Unsupported file type '{suffix}' for file: {path_obj}. "
            f"Supported types: .rst, .md, .tex, .txt, .puml, .plantuml, "
            f".mmd, .mermaid, .dot, .gv, .svg"
        )

    def _generate_protobuf_diagrams(
        self,
        proto_extractor,
        protobuf_diagrams: List,
        proto_files: Optional[List[str]],
        *,
        proto_package: Optional[str],
        diagram_content: List[str],
    ) -> None:
        """Generate and include protobuf diagrams.

        Args:
            proto_extractor: ProtoDoc extractor instance.
            protobuf_diagrams: List of diagram configurations.
            proto_files: Optional list of proto files to process.
            proto_package: Optional package filter.
            diagram_content: List to append generated diagram content to.
        """
        logger.info(f"  📊 Generating {len(protobuf_diagrams)} automatic protobuf diagram(s)")
        try:
            # Parse all proto files to get structure
            proto_file_paths = proto_extractor.find_proto_files(proto_files)
            parsed_files = self._parse_proto_files(proto_extractor, proto_file_paths, proto_package)

            if parsed_files:
                # Generate diagrams
                generated = generate_proto_diagrams(
                    parsed_files, protobuf_diagrams, self.paths.output_dir
                )

                # Add generated diagrams to diagram_includes
                self._include_generated_diagrams(generated, diagram_content)
        except Exception as e:
            logger.warning(f"Failed to generate protobuf diagrams: {e}")

    def _parse_proto_files(
        self, proto_extractor, proto_file_paths: List[Path], proto_package: Optional[str]
    ) -> List[Dict]:
        """Parse proto files and filter by package if specified.

        Args:
            proto_extractor: ProtoDoc extractor instance.
            proto_file_paths: List of proto file paths.
            proto_package: Optional package filter.

        Returns:
            List of parsed proto file data.
        """
        parsed_files = []
        for proto_file in proto_file_paths:
            with open(proto_file, encoding="utf-8") as f:
                content = f.read()
            parsed = proto_extractor.parse_proto_file(content)
            if not proto_package or parsed.get("package") == proto_package:
                parsed_files.append(parsed)
        return parsed_files

    def _include_generated_diagrams(
        self, generated: List[Dict], diagram_content: List[str]
    ) -> None:
        """Include generated diagrams in the documentation.

        Args:
            generated: List of generated diagram metadata.
            diagram_content: List to append diagram content to.
        """
        for gen_diagram in generated:
            diagram_path = gen_diagram["path"]
            diagram_title = gen_diagram["title"]

            # Determine diagram type and include it
            suffix = Path(diagram_path).suffix.lower()
            try:
                content = self._include_diagram_by_type(diagram_path, diagram_title, suffix)
                diagram_content.append(content)
            except Exception as e:
                logger.warning(f"Failed to include generated diagram {diagram_path}: {e}")

    def _include_diagram_by_type(self, diagram_path: str, diagram_title: str, suffix: str) -> str:
        """Include a diagram based on its file type.

        Args:
            diagram_path: Path to the diagram file.
            diagram_title: Title for the diagram.
            suffix: File suffix (e.g., '.puml', '.dot').

        Returns:
            RST content for the diagram.
        """
        if suffix in [".puml", ".plantuml"]:
            return self.include_plantuml_file(diagram_path, diagram_title)
        if suffix in [".dot", ".gv"]:
            return self.include_graphviz_file(diagram_path, diagram_title)
        return self.include_file(diagram_path)

    def _check_protobuf_diagram_types(self, protobuf_diagrams) -> Tuple[bool, bool]:
        """Check protobuf diagrams to determine required extensions.

        Args:
            protobuf_diagrams: Protobuf diagram configuration.

        Returns:
            Tuple of (has_plantuml, has_graphviz).
        """
        has_plantuml = False
        has_graphviz = False

        if not isinstance(protobuf_diagrams, list):
            return has_plantuml, has_graphviz

        for diagram_config in protobuf_diagrams:
            if not isinstance(diagram_config, dict):
                continue

            diagram_type = diagram_config.get("type", "class")
            diagram_format = diagram_config.get("format", "plantuml")

            # Most diagram types use PlantUML by default
            if diagram_type in ["class", "service", "sequence"]:
                has_plantuml = True
            elif diagram_type == "dependencies":
                # Dependencies can be PlantUML or Graphviz
                if diagram_format == "graphviz":
                    has_graphviz = True
                else:
                    has_plantuml = True

        return has_plantuml, has_graphviz

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
                current_output_dir = node.get_output_dir(self.paths.generated_dir)
                relative_path = child.get_relative_path_from(
                    current_output_dir, self.paths.generated_dir
                )
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

        # Process diagram includes (PlantUML, Mermaid, Graphviz, SVG)
        diagram_includes = config.get("diagram_includes", [])
        if isinstance(diagram_includes, str):
            diagram_includes = [diagram_includes]

        diagram_content = []
        for diagram_spec in diagram_includes:
            try:
                if isinstance(diagram_spec, dict):
                    # Detailed diagram specification with path and optional title
                    diagram_path = diagram_spec.get("path", "")
                    diagram_title = diagram_spec.get("title", "")
                    if diagram_path:
                        # Extract file extension to determine diagram type
                        suffix = Path(diagram_path).suffix.lower()
                        if suffix in [".puml", ".plantuml"]:
                            content = self.include_plantuml_file(diagram_path, diagram_title)
                        elif suffix in [".mmd", ".mermaid"]:
                            content = self.include_mermaid_file(diagram_path, diagram_title)
                        elif suffix in [".dot", ".gv"]:
                            content = self.include_graphviz_file(diagram_path, diagram_title)
                        elif suffix == ".svg":
                            alt_text = diagram_spec.get("alt_text", "")
                            content = self.include_svg_file(diagram_path, diagram_title, alt_text)
                        else:
                            # Fallback to generic include
                            content = self.include_file(diagram_path)
                        diagram_content.append(content)
                elif isinstance(diagram_spec, str):
                    # Simple path string
                    content = self.include_file(diagram_spec)
                    diagram_content.append(content)
            except IntroligoError as e:
                logger.warning(f"{e}")

        # Handle godoc_packages (list) or godoc_package (single string)
        godoc_package = config.get("godoc_package", "")
        godoc_packages = config.get("godoc_packages", [])

        # If godoc_package is set but godoc_packages is not, convert to list
        if godoc_package and not godoc_packages:
            godoc_packages = [godoc_package]

        # Extract Go documentation if Go language is specified
        godoc_extracted_content = ""

        # Check if manual documentation is provided
        manual_godoc = config.get("godoc_manual_content")

        if config.get("language") == "go" and (godoc_package or godoc_packages):
            if manual_godoc:
                # Use manually provided documentation
                godoc_extracted_content = manual_godoc
                logger.info("Using manually provided Go documentation")
            else:
                # Try automatic extraction
                # Determine package path (relative to config file)
                godoc_path = config.get("godoc_path")
                if godoc_path:
                    godoc_path_obj = Path(godoc_path)
                    if not godoc_path_obj.is_absolute():
                        godoc_path_obj = self.paths.config_file.parent / godoc_path
                else:
                    # Try to use config file's parent directory
                    godoc_path_obj = self.paths.config_file.parent

                extractor = GoDocExtractor(package_path=godoc_path_obj)

                if godoc_packages:
                    # Extract for multiple packages
                    results = extractor.extract_multiple_packages(godoc_packages)
                    content_parts = []
                    for pkg_name, success, content in results:
                        if success:
                            content_parts.append(f"Package: ``{pkg_name}``\n")
                            content_parts.append("~" * (len(pkg_name) + 11) + "\n\n")
                        content_parts.append(content)
                        content_parts.append("\n\n")
                    godoc_extracted_content = "".join(content_parts)
                elif godoc_package:
                    # Extract for single package
                    success, content = extractor.extract_and_convert(godoc_package)
                    godoc_extracted_content = content

        # Handle Java documentation extraction
        java_source_files = config.get("java_source_files", [])
        java_package = config.get("java_package", "")
        java_packages = config.get("java_packages", [])
        javadoc_path = config.get("javadoc_path", "")

        # Extract Java documentation if Java language is specified
        javadoc_extracted_content = ""

        # Check if manual documentation is provided
        manual_javadoc = config.get("java_manual_content")

        if config.get("language") == "java":
            if manual_javadoc:
                # Use manually provided documentation
                javadoc_extracted_content = manual_javadoc
                logger.info("Using manually provided Java documentation")
            else:
                # Try automatic extraction
                # Determine source path (relative to config file)
                java_source_path = config.get("java_source_path")
                if java_source_path:
                    java_source_path_obj = Path(java_source_path)
                    if not java_source_path_obj.is_absolute():
                        java_source_path_obj = self.paths.config_file.parent / java_source_path
                else:
                    # Try to use config file's parent directory
                    java_source_path_obj = self.paths.config_file.parent

                java_extractor = JavaDocExtractor(source_path=java_source_path_obj)

                if java_packages:
                    # Extract for multiple packages
                    content_parts = []
                    for pkg_name in java_packages:
                        # Convert package name to directory path (com.example -> com/example)
                        pkg_path = java_source_path_obj / pkg_name.replace(".", "/")
                        success, content = java_extractor.extract_package(pkg_path, pkg_name)
                        if success:
                            content_parts.append(content)
                            content_parts.append("\n\n")
                    javadoc_extracted_content = "".join(content_parts)
                elif java_package:
                    # Extract for single package
                    pkg_path = java_source_path_obj / java_package.replace(".", "/")
                    success, content = java_extractor.extract_package(pkg_path, java_package)
                    javadoc_extracted_content = content
                elif java_source_files:
                    # Extract from specific source files
                    java_file_paths = []
                    for file_path in java_source_files:
                        file_path_obj = Path(file_path)
                        if not file_path_obj.is_absolute():
                            file_path_obj = self.paths.config_file.parent / file_path
                        java_file_paths.append(file_path_obj)

                    results = java_extractor.extract_multiple_files(java_file_paths)
                    content_parts = []
                    for filename, success, content in results:
                        if success:
                            content_parts.append(f"{filename}\n")
                            content_parts.append("~" * len(filename) + "\n\n")
                        content_parts.append(content)
                        content_parts.append("\n\n")
                    javadoc_extracted_content = "".join(content_parts)

        # Handle Rust documentation extraction
        rustdoc_crate = config.get("rustdoc_crate", "")
        rustdoc_path = config.get("rustdoc_path", "")

        # Extract Rust documentation if Rust language is specified
        rustdoc_extracted_content = ""

        # Check if manual documentation is provided
        manual_rustdoc = config.get("rustdoc_manual_content")

        if config.get("language") == "rust":
            if manual_rustdoc:
                # Use manually provided documentation
                rustdoc_extracted_content = manual_rustdoc
                logger.info("Using manually provided Rust documentation")
            else:
                # Try automatic extraction
                # Determine crate path (relative to config file)
                if rustdoc_path:
                    rustdoc_path_obj = Path(rustdoc_path)
                    if not rustdoc_path_obj.is_absolute():
                        rustdoc_path_obj = self.paths.config_file.parent / rustdoc_path
                else:
                    # Try to use config file's parent directory
                    rustdoc_path_obj = self.paths.config_file.parent

                rust_extractor = RustDocExtractor(crate_path=rustdoc_path_obj)
                success, content = rust_extractor.extract_and_convert(rustdoc_crate)
                rustdoc_extracted_content = content

        # Handle Protobuf documentation extraction
        proto_files = config.get("proto_files", [])
        proto_package = config.get("proto_package", "")
        proto_path = config.get("proto_path", "")

        # Extract Protobuf documentation if protobuf language is specified
        protodoc_extracted_content = ""
        proto_extractor = None

        # Check if manual documentation is provided
        manual_protodoc = config.get("protodoc_manual_content")

        if config.get("language") == "protobuf":
            if manual_protodoc:
                # Use manually provided documentation
                protodoc_extracted_content = manual_protodoc
                logger.info("Using manually provided Protobuf documentation")
            else:
                # Try automatic extraction
                # Determine proto path (relative to config file)
                if proto_path:
                    proto_path_obj = Path(proto_path)
                    if not proto_path_obj.is_absolute():
                        proto_path_obj = self.paths.config_file.parent / proto_path
                else:
                    # Try to use config file's parent directory
                    proto_path_obj = self.paths.config_file.parent

                proto_extractor = ProtoDocExtractor(proto_path=proto_path_obj)
                success, content = proto_extractor.extract_and_convert(
                    proto_files if proto_files else None, proto_package if proto_package else None
                )
                protodoc_extracted_content = content

        # Generate automatic diagrams from protobuf if configured
        # This can work independently of language setting
        protobuf_diagrams = config.get("protobuf_diagrams", [])
        if protobuf_diagrams:
            # Create proto_extractor if not already created (for diagram-only generation)
            if not proto_extractor and proto_path:
                proto_path_obj = Path(proto_path)
                if not proto_path_obj.is_absolute():
                    proto_path_obj = self.paths.config_file.parent / proto_path
                proto_extractor = ProtoDocExtractor(proto_path=proto_path_obj)

            if proto_extractor:
                self._generate_protobuf_diagrams(
                    proto_extractor,
                    protobuf_diagrams,
                    proto_files,
                    proto_package=proto_package,
                    diagram_content=diagram_content,
                )

        # Process custom_sections to convert unsupported directives
        custom_sections = config.get("custom_sections", [])
        processed_custom_sections = []
        for section in custom_sections:
            if isinstance(section, dict) and "content" in section:
                processed_section = section.copy()
                processed_section["content"] = process_rst_directives(
                    section["content"],
                    self.extensions.has_plantuml_extension,
                    self.extensions.has_mermaid_extension,
                )
                processed_custom_sections.append(processed_section)
            else:
                processed_custom_sections.append(section)

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
            "godoc_package": godoc_package,
            "godoc_packages": godoc_packages,
            "godoc_function": config.get("godoc_function", ""),
            "godoc_type": config.get("godoc_type", ""),
            "godoc_extracted_content": godoc_extracted_content,
            "java_source_files": java_source_files,
            "java_package": java_package,
            "java_packages": java_packages,
            "javadoc_path": javadoc_path,
            "javadoc_extracted_content": javadoc_extracted_content,
            "rustdoc_crate": rustdoc_crate,
            "rustdoc_path": rustdoc_path,
            "rustdoc_extracted_content": rustdoc_extracted_content,
            "proto_files": proto_files,
            "proto_package": proto_package,
            "proto_path": proto_path,
            "protodoc_extracted_content": protodoc_extracted_content,
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
            "custom_sections": processed_custom_sections,
            "markdown_includes": markdown_content,
            "latex_includes": latex_content,
            "rst_includes": rst_content,
            "file_includes": file_content,
            "diagram_includes": diagram_content,
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
            relative_path = node.get_relative_path_from(
                self.paths.generated_dir, self.paths.generated_dir
            )
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
                output_file = node.get_output_file(self.paths.generated_dir)
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
        generated_files = self.generate_all_nodes(self.page_tree, template, self.options.strict)

        if self.config.get("generate_index", True):
            index_content = self.generate_index(self.page_tree)
            index_path = self.paths.output_dir / "index.rst"
            generated_files[str(index_path)] = (index_content, index_path)
            logger.info("  📋 Generated: index.rst")

        return generated_files

    def write_files(self, generated_files: Dict[str, Tuple[str, Path]]) -> None:
        """Write all generated files to disk.

        Args:
            generated_files: Dictionary mapping file paths to (content, Path) tuples.
        """
        if self.options.dry_run:
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
            xml_path_obj = self.paths.config_file.parent / xml_path
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
                config_relative = self.paths.config_file.parent / palette_name
                if config_relative.exists():
                    palette_path = config_relative
                else:
                    raise IntroligoError(
                        f"Palette not found: {palette_name}. "
                        f"Tried: {palette_path}, {package_palette}, {config_relative}"
                    )

        try:
            with open(palette_path, encoding="utf-8") as f:
                # Using custom IncludeLoader for YAML file inclusion feature
                palette_data: Dict[str, Any] = yaml.load(f, Loader=IncludeLoader)  # nosec B506
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
            Note: Variable names starting with '--' will have the prefix removed since
            Furo adds it automatically when generating CSS.
        """
        resolved = {}
        for key, value in theme_mapping.items():
            # Strip '--' prefix from variable names since Furo adds it automatically
            clean_key = key.lstrip("-") if key.startswith("--") else key
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
                            resolved[clean_key] = color_value
                        else:
                            logger.warning(
                                f"Color reference not found: {ref} "
                                f"(available shades: {list(palette_colors[color_group].keys())})"
                            )
                            resolved[clean_key] = value
                    else:
                        logger.warning(
                            f"Color group not found: {color_group} "
                            f"(available groups: {list(palette_colors.keys())})"
                        )
                        resolved[clean_key] = value
                else:
                    logger.warning(f"Invalid color reference format: {value}")
                    resolved[clean_key] = value
            else:
                resolved[clean_key] = value

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
                # Check if this module has Go-specific fields
                if any(
                    key in module_config
                    for key in [
                        "godoc_package",
                        "godoc_packages",
                        "godoc_function",
                        "godoc_type",
                    ]
                ):
                    languages.add("go")
                # Check if this module has Java-specific fields
                if any(
                    key in module_config
                    for key in [
                        "java_source_files",
                        "java_package",
                        "java_packages",
                        "javadoc_path",
                    ]
                ):
                    languages.add("java")
                # Check if this module has Rust-specific fields
                if any(
                    key in module_config
                    for key in [
                        "rustdoc_crate",
                        "rustdoc_path",
                    ]
                ):
                    languages.add("rust")

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

        # Note: Go documentation uses simple code blocks
        # sphinxcontrib.golangdomain is outdated and incompatible with Sphinx 4.0+
        # For Go, we use manual documentation with code-block directives
        if "go" in languages:
            logger.info("  Go language detected - using code-block documentation")

        # Note: Java documentation uses simple code blocks
        # Similar to Go, we extract Java documentation and format with code-block directives
        if "java" in languages:
            logger.info("  Java language detected - using code-block documentation")

        # Note: Rust documentation uses simple code blocks
        # Similar to Go and Java, we extract Rust documentation and format
        # with code-block directives
        if "rust" in languages:
            logger.info("  Rust language detected - using code-block documentation")

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

        # Auto-add diagram extensions if diagram_includes or file_includes
        # with diagram files are found
        def has_diagram_files(include_list):
            """Check if include list contains diagram files."""
            if not include_list:
                return False, False, False

            has_plantuml = False
            has_mermaid = False
            has_graphviz = False

            items = include_list if isinstance(include_list, list) else [include_list]
            for item in items:
                if isinstance(item, str):
                    path = item
                elif isinstance(item, dict):
                    path = item.get("path", "")
                else:
                    path = ""
                if path:
                    suffix = Path(path).suffix.lower()
                    if suffix in [".puml", ".plantuml"]:
                        has_plantuml = True
                    elif suffix in [".mmd", ".mermaid"]:
                        has_mermaid = True
                    elif suffix in [".dot", ".gv"]:
                        has_graphviz = True

            return has_plantuml, has_mermaid, has_graphviz

        has_plantuml_global = False
        has_mermaid_global = False
        has_graphviz_global = False

        for module_config in self.config.get("modules", {}).values():
            if not isinstance(module_config, dict):
                continue

            # Check diagram_includes
            if "diagram_includes" in module_config:
                p, m, g = has_diagram_files(module_config["diagram_includes"])
                has_plantuml_global = has_plantuml_global or p
                has_mermaid_global = has_mermaid_global or m
                has_graphviz_global = has_graphviz_global or g

            # Check file_includes for diagram files
            if "file_includes" in module_config:
                p, m, g = has_diagram_files(module_config["file_includes"])
                has_plantuml_global = has_plantuml_global or p
                has_mermaid_global = has_mermaid_global or m
                has_graphviz_global = has_graphviz_global or g

            # Check protobuf_diagrams for auto-generated diagrams
            if "protobuf_diagrams" in module_config:
                p, g = self._check_protobuf_diagram_types(module_config["protobuf_diagrams"])
                has_plantuml_global = has_plantuml_global or p
                has_graphviz_global = has_graphviz_global or g

        # Helper function to check if a package is available
        def is_package_available(package_name: str) -> bool:
            """Check if a Python package is available for import."""
            try:
                __import__(package_name.replace("-", "_"))
                return True
            except ImportError:
                return False

        # Add diagram extensions as needed (only if packages are available)
        if has_graphviz_global and "sphinx.ext.graphviz" not in extensions:
            # sphinx.ext.graphviz is built-in to Sphinx, always available
            extensions.append("sphinx.ext.graphviz")
            logger.info("  Auto-added diagram extension: sphinx.ext.graphviz")

        if has_plantuml_global and "sphinxcontrib.plantuml" not in extensions:
            if is_package_available("sphinxcontrib.plantuml"):
                extensions.append("sphinxcontrib.plantuml")
                self.extensions.has_plantuml_extension = True
                logger.info("  Auto-added diagram extension: sphinxcontrib.plantuml")
            else:
                self.extensions.has_plantuml_extension = False
                logger.warning(
                    "  PlantUML diagrams detected but sphinxcontrib-plantuml not installed"
                )
                logger.warning("  Install with: pip install sphinxcontrib-plantuml")
                logger.warning("  Diagrams will be shown as code blocks")

        if has_mermaid_global and "sphinxcontrib.mermaid" not in extensions:
            if is_package_available("sphinxcontrib.mermaid"):
                extensions.append("sphinxcontrib.mermaid")
                self.extensions.has_mermaid_extension = True
                logger.info("  Auto-added diagram extension: sphinxcontrib.mermaid")
            else:
                self.extensions.has_mermaid_extension = False
                logger.warning(
                    "  Mermaid diagrams detected but sphinxcontrib-mermaid not installed"
                )
                logger.warning("  Install with: pip install sphinxcontrib-mermaid")
                logger.warning("  Diagrams will be shown as code blocks")

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
        # Generating Python config file, not HTML, XSS not applicable
        env = Environment()  # nosec B701
        template = env.from_string(template_content)

        # Prepare template context
        context = {
            "config_file_name": self.paths.config_file.name,
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
