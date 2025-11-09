#!/usr/bin/env python
"""Automatic diagram generation from Protocol Buffer definitions.

This module generates PlantUML and Graphviz diagrams from parsed protobuf structures,
including class diagrams, service diagrams, and dependency graphs.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ProtobufDiagramGenerator:
    """Generate diagrams from protobuf structures."""

    def __init__(self):
        """Initialize the diagram generator."""
        self.parsed_files: List[Dict[str, Any]] = []

    def add_parsed_file(self, parsed: Dict[str, Any]) -> None:
        """Add a parsed protobuf file to the generator.

        Args:
            parsed: Parsed protobuf structure from ProtoDocExtractor.
        """
        self.parsed_files.append(parsed)

    def generate_class_diagram(
        self,
        package_filter: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """Generate a PlantUML class diagram showing messages and enums.

        Args:
            package_filter: Optional package name to filter by.
            title: Optional diagram title.

        Returns:
            PlantUML diagram as string.
        """
        lines = ["@startuml"]

        if title:
            lines.append(f"title {title}")
            lines.append("")

        # Group by package
        packages: Dict[str, Dict[str, List]] = {}

        for parsed in self.parsed_files:
            pkg = parsed.get("package", "")

            # Filter by package if specified
            if package_filter and pkg != package_filter:
                continue

            if pkg not in packages:
                packages[pkg] = {"messages": [], "enums": []}

            packages[pkg]["messages"].extend(parsed.get("messages", []))
            packages[pkg]["enums"].extend(parsed.get("enums", []))

        # Generate diagram for each package
        for pkg_name, pkg_data in packages.items():
            if pkg_name:
                lines.append(f'package "{pkg_name}" {{')
                lines.append("")

            # Add enums
            for enum in pkg_data["enums"]:
                lines.extend(self._format_enum_for_class_diagram(enum))

            # Add messages
            for message in pkg_data["messages"]:
                lines.extend(self._format_message_for_class_diagram(message))

            if pkg_name:
                lines.append("}")
                lines.append("")

        # Add relationships
        lines.append("")
        lines.append("' Relationships")
        for parsed in self.parsed_files:
            pkg = parsed.get("package", "")
            if package_filter and pkg != package_filter:
                continue

            for message in parsed.get("messages", []):
                lines.extend(self._extract_relationships(message, pkg))

        lines.append("@enduml")
        return "\n".join(lines)

    def generate_service_diagram(
        self,
        package_filter: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """Generate a PlantUML component diagram showing services.

        Args:
            package_filter: Optional package name to filter by.
            title: Optional diagram title.

        Returns:
            PlantUML diagram as string.
        """
        lines = ["@startuml"]

        if title:
            lines.append(f"title {title}")
            lines.append("")

        lines.append("' Service components")
        lines.append("")

        for parsed in self.parsed_files:
            pkg = parsed.get("package", "")

            # Filter by package if specified
            if package_filter and pkg != package_filter:
                continue

            for service in parsed.get("services", []):
                lines.extend(self._format_service_component(service, pkg))

        lines.append("@enduml")
        return "\n".join(lines)

    def generate_sequence_diagram(
        self,
        service_name: str,
        rpc_name: Optional[str] = None,
        title: Optional[str] = None,
    ) -> str:
        """Generate a PlantUML sequence diagram for RPC calls.

        Args:
            service_name: Name of the service to diagram.
            rpc_name: Optional specific RPC method to show.
            title: Optional diagram title.

        Returns:
            PlantUML diagram as string.
        """
        lines = ["@startuml"]

        if title:
            lines.append(f"title {title}")
        else:
            lines.append(f"title {service_name} RPC Flow")
        lines.append("")

        lines.append("actor Client")
        lines.append(f'participant "{service_name}" as Service')
        lines.append("database Storage")
        lines.append("")

        # Find the service
        service_data = None
        for parsed in self.parsed_files:
            for service in parsed.get("services", []):
                if service["name"] == service_name:
                    service_data = service
                    break
            if service_data:
                break

        if not service_data:
            lines.append(f"note over Client,Storage: Service '{service_name}' not found")
            lines.append("@enduml")
            return "\n".join(lines)

        # Generate sequence for each RPC method
        methods = service_data.get("methods", [])
        if rpc_name:
            methods = [m for m in methods if m["name"] == rpc_name]

        for method in methods:
            method_name = method["name"]
            request_type = method["request_type"]
            response_type = method["response_type"]

            lines.append("")
            lines.append(f"== {method_name} ==")
            lines.append(f"Client -> Service: {method_name}({request_type})")
            lines.append("activate Service")

            # Add common processing steps
            if "Create" in method_name:
                lines.append("Service -> Storage: Store data")
                lines.append("Service <-- Storage: Success")
            elif "Get" in method_name or "List" in method_name:
                lines.append("Service -> Storage: Query data")
                lines.append("Service <-- Storage: Return data")
            elif "Update" in method_name:
                lines.append("Service -> Storage: Update data")
                lines.append("Service <-- Storage: Success")
            elif "Delete" in method_name:
                lines.append("Service -> Storage: Delete data")
                lines.append("Service <-- Storage: Success")
            else:
                lines.append("Service -> Storage: Process request")
                lines.append("Service <-- Storage: Result")

            lines.append(f"Client <-- Service: {response_type}")
            lines.append("deactivate Service")

        lines.append("")
        lines.append("@enduml")
        return "\n".join(lines)

    def generate_dependency_graph(
        self,
        title: Optional[str] = None,
        output_format: str = "graphviz",
    ) -> str:
        """Generate a dependency graph showing package relationships.

        Args:
            title: Optional diagram title.
            output_format: Output format ('graphviz' or 'plantuml').

        Returns:
            Diagram as string.
        """
        if output_format == "plantuml":
            return self._generate_dependency_graph_plantuml(title)
        return self._generate_dependency_graph_graphviz(title)

    def _generate_dependency_graph_graphviz(self, title: Optional[str] = None) -> str:
        """Generate Graphviz dependency graph.

        Args:
            title: Optional diagram title.

        Returns:
            Graphviz DOT format string.
        """
        lines = ["digraph ProtobufDependencies {"]
        lines.append("    rankdir=LR;")
        lines.append("    node [shape=box, style=filled, fillcolor=lightblue];")
        lines.append("")

        if title:
            lines.append(f'    label="{title}";')
            lines.append("    labelloc=t;")
            lines.append("")

        # Track packages and their dependencies
        packages: Set[str] = set()
        dependencies: Set[Tuple[str, str]] = set()

        for parsed in self.parsed_files:
            pkg = parsed.get("package", "")
            if pkg:
                packages.add(pkg)

                # Look for references to other packages in fields
                for message in parsed.get("messages", []):
                    for field in message.get("fields", []):
                        dep_pkg = self._extract_package_from_type(field.get("type", ""))
                        if dep_pkg and dep_pkg != pkg:
                            dependencies.add((pkg, dep_pkg))

        # Add nodes
        for pkg in sorted(packages):
            node_name = pkg.replace(".", "_")
            lines.append(f'    {node_name} [label="{pkg}"];')

        lines.append("")

        # Add edges
        for src, dst in sorted(dependencies):
            src_node = src.replace(".", "_")
            dst_node = dst.replace(".", "_")
            lines.append(f"    {src_node} -> {dst_node};")

        lines.append("}")
        return "\n".join(lines)

    def _generate_dependency_graph_plantuml(self, title: Optional[str] = None) -> str:
        """Generate PlantUML dependency graph.

        Args:
            title: Optional diagram title.

        Returns:
            PlantUML format string.
        """
        lines = ["@startuml"]

        if title:
            lines.append(f"title {title}")
            lines.append("")

        # Track packages
        packages: Set[str] = set()
        dependencies: Set[Tuple[str, str]] = set()

        for parsed in self.parsed_files:
            pkg = parsed.get("package", "")
            if pkg:
                packages.add(pkg)

                # Look for references
                for message in parsed.get("messages", []):
                    for field in message.get("fields", []):
                        dep_pkg = self._extract_package_from_type(field.get("type", ""))
                        if dep_pkg and dep_pkg != pkg:
                            dependencies.add((pkg, dep_pkg))

        # Add components
        for pkg in sorted(packages):
            lines.append(f'package "{pkg}" {{')
            lines.append("}")

        lines.append("")

        # Add dependencies
        for src, dst in sorted(dependencies):
            lines.append(f'"{src}" --> "{dst}"')

        lines.append("@enduml")
        return "\n".join(lines)

    def _format_message_for_class_diagram(self, message: Dict[str, Any]) -> List[str]:
        """Format a message as a PlantUML class.

        Args:
            message: Message dictionary.

        Returns:
            List of PlantUML lines.
        """
        lines = []
        msg_name = message["name"]

        lines.append(f"class {msg_name} {{")

        # Add fields
        for field in message.get("fields", []):
            field_name = field["name"]
            field_type = field["type"]
            label = field.get("label", "")

            # Format field with label (repeated, optional)
            if label == "repeated":
                lines.append(f"    +{field_type}[] {field_name}")
            else:
                lines.append(f"    +{field_type} {field_name}")

        lines.append("}")
        lines.append("")
        return lines

    def _format_enum_for_class_diagram(self, enum: Dict[str, Any]) -> List[str]:
        """Format an enum as a PlantUML enum.

        Args:
            enum: Enum dictionary.

        Returns:
            List of PlantUML lines.
        """
        lines = []
        enum_name = enum["name"]

        lines.append(f"enum {enum_name} {{")

        # Add values
        for value in enum.get("values", []):
            value_name = value["name"]
            lines.append(f"    {value_name}")

        lines.append("}")
        lines.append("")
        return lines

    def _format_service_component(self, service: Dict[str, Any], package: str) -> List[str]:
        """Format a service as a PlantUML component.

        Args:
            service: Service dictionary.
            package: Package name.

        Returns:
            List of PlantUML lines.
        """
        lines = []
        service_name = service["name"]

        if package:
            lines.append(f'package "{package}" {{')

        lines.append(f"interface {service_name} {{")

        # Add RPC methods
        for method in service.get("methods", []):
            method_name = method["name"]
            request_type = method["request_type"]
            response_type = method["response_type"]
            lines.append(f"    +{method_name}({request_type}): {response_type}")

        lines.append("}")

        if package:
            lines.append("}")

        lines.append("")
        return lines

    def _extract_relationships(self, message: Dict[str, Any], package: str) -> List[str]:
        """Extract relationships from a message.

        Args:
            message: Message dictionary.
            package: Package name.

        Returns:
            List of PlantUML relationship lines.
        """
        lines = []
        msg_name = message["name"]

        for field in message.get("fields", []):
            field_type = field["type"]
            label = field.get("label", "")

            # Check if field type is a custom message (not a primitive)
            if self._is_message_type(field_type):
                # Composition relationship (contains)
                if label == "repeated":
                    lines.append(f'{msg_name} "1" *-- "*" {field_type}')
                else:
                    lines.append(f'{msg_name} "1" *-- "1" {field_type}')

        return lines

    def _is_message_type(self, type_name: str) -> bool:
        """Check if a type is a message (not a primitive).

        Args:
            type_name: Type name to check.

        Returns:
            True if it's a message type, False otherwise.
        """
        primitives = {
            "int32",
            "int64",
            "uint32",
            "uint64",
            "sint32",
            "sint64",
            "fixed32",
            "fixed64",
            "sfixed32",
            "sfixed64",
            "float",
            "double",
            "bool",
            "string",
            "bytes",
        }
        return type_name not in primitives and not type_name.startswith("map<")

    def _extract_package_from_type(self, type_name: str) -> Optional[str]:
        """Extract package name from a qualified type.

        Args:
            type_name: Type name (e.g., 'user.v1.User').

        Returns:
            Package name or None.
        """
        if "." in type_name:
            parts = type_name.split(".")
            if len(parts) >= 2:
                return ".".join(parts[:-1])
        return None


def generate_proto_diagrams(
    parsed_files: List[Dict[str, Any]],
    diagram_configs: List[Dict[str, str]],
    output_dir: Path,
) -> List[Dict[str, str]]:
    """Generate diagrams from parsed protobuf files.

    Args:
        parsed_files: List of parsed protobuf structures.
        diagram_configs: List of diagram configuration dictionaries.
        output_dir: Directory to write diagram files.

    Returns:
        List of diagram file paths with metadata.
    """
    generator = ProtobufDiagramGenerator()

    # Add all parsed files
    for parsed in parsed_files:
        generator.add_parsed_file(parsed)

    generated_diagrams = []

    # Create diagrams directory
    diagrams_dir = output_dir / "diagrams" / "generated"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    for config in diagram_configs:
        diagram_type = config.get("type", "class")
        title = config.get("title")
        package_filter = config.get("package")
        service_name = config.get("service")
        rpc_name = config.get("rpc")
        format_type = config.get("format", "plantuml")

        diagram_content = ""
        file_extension = ".puml"

        if diagram_type == "class":
            diagram_content = generator.generate_class_diagram(package_filter, title)
        elif diagram_type == "service":
            diagram_content = generator.generate_service_diagram(package_filter, title)
        elif diagram_type == "sequence":
            if not service_name:
                logger.warning("Sequence diagram requires 'service' parameter")
                continue
            diagram_content = generator.generate_sequence_diagram(service_name, rpc_name, title)
        elif diagram_type == "dependencies":
            format_type = config.get("format", "graphviz")
            diagram_content = generator.generate_dependency_graph(title, format_type)
            file_extension = ".dot" if format_type == "graphviz" else ".puml"
        else:
            logger.warning(f"Unknown diagram type: {diagram_type}")
            continue

        # Generate filename
        if title:
            filename = re.sub(r"[^\w\s-]", "", title.lower())
            filename = re.sub(r"[-\s]+", "_", filename)
        else:
            filename = f"{diagram_type}_diagram"

        if package_filter:
            filename = f"{package_filter.replace('.', '_')}_{filename}"

        filename = f"{filename}{file_extension}"
        diagram_path = diagrams_dir / filename

        # Write diagram file
        with open(diagram_path, "w", encoding="utf-8") as f:
            f.write(diagram_content)

        logger.info(f"Generated diagram: {diagram_path}")

        generated_diagrams.append(
            {
                "path": str(diagram_path.relative_to(output_dir.parent)),
                "title": title or f"{diagram_type.capitalize()} Diagram",
                "type": diagram_type,
            }
        )

    return generated_diagrams
