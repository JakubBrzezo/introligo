#!/usr/bin/env python
"""Protobuf documentation extractor for Introligo.

This module extracts documentation from Protocol Buffer files via direct parsing
and converts it to reStructuredText format for inclusion in Sphinx documentation.

The parser supports:
- File-level comments
- Message definitions with field-level comments
- Enum definitions with value-level comments
- Service definitions with RPC method comments
- Both inline (//) and block (/* */) comment styles

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ProtoDocExtractor:
    """Extract and convert Protocol Buffer documentation to RST format."""

    def __init__(self, proto_path: Optional[Path] = None):
        """Initialize the ProtoDoc extractor.

        Args:
            proto_path: Optional path to the directory containing .proto files.
        """
        self.proto_path = proto_path

    def check_protoc_available(self) -> bool:
        """Check if protoc is installed and available.

        Returns:
            True if protoc is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["protoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def check_protoc_gen_doc_available(self) -> bool:
        """Check if protoc-gen-doc plugin is installed and available.

        Returns:
            True if protoc-gen-doc is available, False otherwise.
        """
        try:
            # Try to find protoc-gen-doc in PATH
            result = subprocess.run(
                ["protoc-gen-doc", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def find_proto_files(self, proto_files: Optional[List[str]] = None) -> List[Path]:
        """Find all .proto files in the proto path.

        Args:
            proto_files: Optional list of specific proto files to document.

        Returns:
            List of Path objects for proto files.
        """
        if not self.proto_path or not self.proto_path.exists():
            return []

        if proto_files:
            # Use specified files
            result = []
            for pf in proto_files:
                proto_file = Path(pf)
                if not proto_file.is_absolute():
                    proto_file = self.proto_path / proto_file
                if proto_file.exists():
                    result.append(proto_file)
            return result

        # Find all .proto files recursively
        return list(self.proto_path.rglob("*.proto"))

    def extract_proto_doc(
        self, proto_files: Optional[List[str]] = None, package_name: Optional[str] = None
    ) -> Optional[str]:
        """Extract documentation from Protocol Buffer files via direct parsing.

        Args:
            proto_files: Optional list of specific proto files to document.
            package_name: Optional package name for filtering.

        Returns:
            Documentation as string, or None if extraction fails.
        """
        if not self.proto_path:
            logger.warning("No proto path specified")
            return None

        # Use direct parsing as the primary method
        return self._parse_proto_sources(proto_files, package_name)

    def _parse_protoc_gen_doc_json(
        self, json_file: Path, package_name: Optional[str] = None
    ) -> Optional[str]:
        """Parse protoc-gen-doc JSON output to extract documentation.

        Args:
            json_file: Path to the JSON file.
            package_name: Optional package name for filtering.

        Returns:
            Formatted documentation as string, or None if parsing fails.
        """
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            doc_parts = []

            # Add note about extraction method
            doc_parts.append(".. note::")
            doc_parts.append("")
            doc_parts.append(
                "   Documentation extracted from Protocol Buffer files using protoc-gen-doc."
            )
            doc_parts.append("")
            doc_parts.append("")

            # Process files
            files = data.get("files", [])
            for file_data in files:
                file_desc = file_data.get("description", "")
                package = file_data.get("package", "")

                # Filter by package if specified
                if package_name and package != package_name:
                    continue

                # File header
                if file_desc:
                    doc_parts.append(file_desc.strip())
                    doc_parts.append("")

                # Process messages
                messages = file_data.get("messages", [])
                if messages:
                    doc_parts.append("Messages")
                    doc_parts.append("~~~~~~~~")
                    doc_parts.append("")
                    for msg in messages:
                        self._format_message_json(msg, doc_parts)

                # Process enums
                enums = file_data.get("enums", [])
                if enums:
                    doc_parts.append("Enumerations")
                    doc_parts.append("~~~~~~~~~~~~")
                    doc_parts.append("")
                    for enum in enums:
                        self._format_enum_json(enum, doc_parts)

                # Process services
                services = file_data.get("services", [])
                if services:
                    doc_parts.append("Services")
                    doc_parts.append("~~~~~~~~")
                    doc_parts.append("")
                    for service in services:
                        self._format_service(service, doc_parts)

            if doc_parts:
                return "\n".join(doc_parts)

            return None

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not parse protoc-gen-doc JSON: {e}")
            return None

    def _format_message_json(self, message: Dict, doc_parts: List[str], indent: int = 0) -> None:
        """Format a protobuf message from JSON for RST output.

        Args:
            message: Message data dictionary from protoc-gen-doc JSON.
            doc_parts: List to append formatted lines to.
            indent: Indentation level for nested messages.
        """
        msg_name = message.get("fullName", message.get("name", "Unknown"))
        msg_desc = message.get("description", "")

        prefix = "   " * indent

        # Message name as code block
        doc_parts.append(f"{prefix}.. code-block:: protobuf")
        doc_parts.append(f"{prefix}")
        doc_parts.append(f"{prefix}   message {msg_name} {{")

        # Fields
        fields = message.get("fields", [])
        for field in fields:
            field_name = field.get("name", "")
            field_type = field.get("type", "")
            field_label = field.get("label", "")
            field_num = field.get("number", "")
            doc_parts.append(
                f"{prefix}       {field_label} {field_type} {field_name} = {field_num};"
            )

        doc_parts.append(f"{prefix}   }}")
        doc_parts.append(f"{prefix}")

        # Description
        if msg_desc:
            doc_parts.append(f"{prefix}{msg_desc.strip()}")
            doc_parts.append(f"{prefix}")

        # Field details
        if fields:
            doc_parts.append(f"{prefix}**Fields:**")
            doc_parts.append(f"{prefix}")
            for field in fields:
                field_name = field.get("name", "")
                field_desc = field.get("description", "")
                field_type = field.get("type", "")
                doc_parts.append(f"{prefix}- ``{field_name}`` ({field_type}): {field_desc}")

        doc_parts.append("")

        # Process nested messages
        nested = message.get("messages", [])
        for nested_msg in nested:
            self._format_message_json(nested_msg, doc_parts, indent + 1)

    def _format_enum_json(self, enum: Dict, doc_parts: List[str]) -> None:
        """Format a protobuf enum from JSON for RST output.

        Args:
            enum: Enum data dictionary from protoc-gen-doc JSON.
            doc_parts: List to append formatted lines to.
        """
        enum_name = enum.get("fullName", enum.get("name", "Unknown"))
        enum_desc = enum.get("description", "")

        # Enum name as code block
        doc_parts.append(".. code-block:: protobuf")
        doc_parts.append("")
        doc_parts.append(f"   enum {enum_name} {{")

        # Values
        values = enum.get("values", [])
        for value in values:
            value_name = value.get("name", "")
            value_num = value.get("number", "")
            doc_parts.append(f"       {value_name} = {value_num};")

        doc_parts.append("   }")
        doc_parts.append("")

        # Description
        if enum_desc:
            doc_parts.append(enum_desc.strip())
            doc_parts.append("")

        # Value details
        if values:
            doc_parts.append("**Values:**")
            doc_parts.append("")
            for value in values:
                value_name = value.get("name", "")
                value_desc = value.get("description", "")
                doc_parts.append(f"- ``{value_name}``: {value_desc}")

        doc_parts.append("")

    def _format_service(self, service: Dict, doc_parts: List[str]) -> None:
        """Format a protobuf service for RST output.

        Args:
            service: Service data dictionary.
            doc_parts: List to append formatted lines to.
        """
        service_name = service.get("fullName", service.get("name", "Unknown"))
        service_desc = service.get("description", "")

        # Service name
        doc_parts.append(".. code-block:: protobuf")
        doc_parts.append("")
        doc_parts.append(f"   service {service_name} {{")

        # Methods
        methods = service.get("methods", [])
        for method in methods:
            method_name = method.get("name", "")
            request_type = method.get("requestType", "")
            response_type = method.get("responseType", "")
            doc_parts.append(f"       rpc {method_name}({request_type}) returns ({response_type});")

        doc_parts.append("   }")
        doc_parts.append("")

        # Description
        if service_desc:
            doc_parts.append(service_desc.strip())
            doc_parts.append("")

        # Method details
        if methods:
            doc_parts.append("**Methods:**")
            doc_parts.append("")
            for method in methods:
                method_name = method.get("name", "")
                method_desc = method.get("description", "")
                request_type = method.get("requestType", "")
                response_type = method.get("responseType", "")
                doc_parts.append(f"- ``{method_name}``")
                if method_desc:
                    doc_parts.append(f"  {method_desc.strip()}")
                doc_parts.append(f"  Request: ``{request_type}``")
                doc_parts.append(f"  Response: ``{response_type}``")
                doc_parts.append("")

        doc_parts.append("")

    def _parse_proto_sources(
        self, proto_files: Optional[List[str]] = None, package_name: Optional[str] = None
    ) -> str:
        """Parse protobuf source files directly to extract documentation.

        Args:
            proto_files: Optional list of specific proto files to document.
            package_name: Optional package name for filtering.

        Returns:
            Documentation content as string.
        """
        try:
            proto_file_paths = self.find_proto_files(proto_files)
            if not proto_file_paths:
                return ""

            logger.info(f"Parsing {len(proto_file_paths)} proto file(s) directly")

            doc_parts = []

            # Add note about extraction method
            doc_parts.append(".. note::")
            doc_parts.append("")
            doc_parts.append(
                "   Documentation extracted from Protocol Buffer source files via direct parsing."
            )
            doc_parts.append("")
            doc_parts.append("")

            for proto_file in proto_file_paths:
                with open(proto_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse the entire proto file structure
                parsed = self._parse_proto_file(content)

                # Filter by package if specified
                if package_name and parsed.get("package") != package_name:
                    continue

                # Format the parsed content as RST
                formatted = self._format_parsed_proto(parsed, proto_file.name)
                if formatted:
                    doc_parts.extend(formatted)

            return "\n".join(doc_parts)

        except Exception as e:
            logger.error(f"Error parsing proto sources: {e}")
            return ""

    def _normalize_comment(self, comment: str) -> str:
        """Normalize a comment by removing comment markers and extra whitespace.

        Args:
            comment: Raw comment string.

        Returns:
            Normalized comment text.
        """
        lines = []
        for line in comment.split("\n"):
            stripped = line.strip()
            # Remove // or /* */ markers
            if stripped.startswith("//") or stripped.startswith("/*"):
                stripped = stripped[2:].strip()
            if stripped.endswith("*/"):
                stripped = stripped[:-2].strip()
            # Remove leading * from block comment continuation lines
            if stripped.startswith("*") and not stripped.startswith("**"):
                stripped = stripped[1:].strip()
            if stripped:
                lines.append(stripped)
        return " ".join(lines) if lines else ""

    def _process_cross_references(self, text: str) -> str:
        """Process @Ref keywords in text and convert to RST cross-references.

        Converts @Ref TypeName to :ref:`TypeName` for Sphinx cross-referencing.

        Args:
            text: Text containing @Ref keywords.

        Returns:
            Text with @Ref converted to RST cross-reference syntax.
        """
        import re

        # Match @Ref followed by one or more word characters (letters, digits, underscores, dots)
        # This will match: @Ref User, @Ref user.v1.User, @Ref CreateUserRequest, etc.
        pattern = r"@Ref\s+([\w.]+)"

        def replace_ref(match):
            ref_name = match.group(1)
            # Convert to Sphinx :ref: directive for clickable links
            # Format: :ref:`Display Text <label>`
            # We use the type name as both the label and display text
            return f":ref:`{ref_name} <proto-{ref_name}>`"

        return re.sub(pattern, replace_ref, text)

    def _parse_asyncapi_keywords(self, comment: str) -> Tuple[str, Dict[str, str]]:
        """Parse AsyncAPI validation keywords from a comment.

        Supports keywords used by AsyncAPI protobuf schema parser:
        - @Example, @Min/@Minimum, @Max/@Maximum, @Pattern
        - @ExclusiveMinimum, @ExclusiveMaximum, @MultipleOf
        - @MinLength, @MaxLength, @MinItems, @MaxItems, @Default
        - @Ref for cross-references (converted to RST format)

        Args:
            comment: Comment text to parse.

        Returns:
            Tuple of (description_without_keywords, keywords_dict).
        """
        keywords = {}
        description_lines = []

        # Define keyword mappings (alias -> canonical name)
        # Order matters: longer keywords must come first to avoid partial matches
        keyword_aliases = [
            ("@ExclusiveMinimum", "exclusiveMinimum"),
            ("@ExclusiveMaximum", "exclusiveMaximum"),
            ("@MinLength", "minLength"),
            ("@MaxLength", "maxLength"),
            ("@MinItems", "minItems"),
            ("@MaxItems", "maxItems"),
            ("@MultipleOf", "multipleOf"),
            ("@Minimum", "minimum"),
            ("@Maximum", "maximum"),
            ("@Min", "minimum"),
            ("@Max", "maximum"),
            ("@Pattern", "pattern"),
            ("@Example", "example"),
            ("@Default", "default"),
        ]

        # Split comment into lines and process each
        for line in comment.split("\n"):
            line = line.strip()
            found_keyword = False

            # Check if line starts with a keyword (check longer keywords first)
            for keyword, canonical_name in keyword_aliases:
                if line.startswith(keyword):
                    # Extract value after keyword
                    value = line[len(keyword) :].strip()
                    # Remove leading colon or equals sign if present
                    if value.startswith(":") or value.startswith("="):
                        value = value[1:].strip()
                    if value:
                        keywords[canonical_name] = value
                    found_keyword = True
                    break

            # If no keyword found, treat as description
            if not found_keyword and line:
                description_lines.append(line)

        description = " ".join(description_lines)
        # Process @ref cross-references in the description
        description = self._process_cross_references(description)
        return description, keywords

    def _extract_comments_before(self, lines: List[str], start_idx: int) -> str:
        """Extract comments that appear before a given line index.

        Args:
            lines: List of file lines.
            start_idx: Index to start looking backwards from.

        Returns:
            Extracted comment text (preserves newlines for keyword parsing).
        """
        comments: List[str] = []
        idx = start_idx - 1

        # Look backwards for comments
        while idx >= 0:
            line = lines[idx].strip()
            if not line:
                # Empty line - stop if we already have comments
                if comments:
                    break
                idx -= 1
                continue
            elif line.startswith("//"):
                comments.insert(0, line)
                idx -= 1
            elif "*/" in line:
                # End of block comment - collect the whole block
                block_lines = [line]
                idx -= 1
                while idx >= 0:
                    block_lines.insert(0, lines[idx].strip())
                    if "/*" in lines[idx]:
                        break
                    idx -= 1
                comments = block_lines + comments
                idx -= 1
            else:
                # Non-comment, non-empty line
                break

        # Don't normalize yet - return with newlines preserved for keyword parsing
        return "\n".join(comments)

    def _extract_inline_comment(self, line: str) -> Tuple[str, str]:
        """Extract inline comment from a line.

        Args:
            line: Line to extract comment from.

        Returns:
            Tuple of (line_without_comment, comment).
        """
        # Look for // style comment
        if "//" in line:
            # Make sure it's not in a string
            parts = line.split("//", 1)
            return parts[0].rstrip(), self._normalize_comment(parts[1])
        return line, ""

    def _parse_proto_file(self, content: str) -> Dict[str, Any]:
        """Parse a protobuf file and extract all elements with their comments.

        Args:
            content: Content of the proto file.

        Returns:
            Dictionary containing parsed structure.
        """
        lines = content.split("\n")
        result: Dict[str, Any] = {
            "file_comment": "",
            "syntax": "",
            "package": "",
            "imports": [],
            "options": [],
            "messages": [],
            "enums": [],
            "services": [],
        }

        # Extract file-level comments (before package, including those after syntax)
        file_comments = []
        found_syntax = False
        for _i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("syntax"):
                found_syntax = True
                continue
            elif stripped.startswith("package"):
                break
            elif stripped.startswith("//") or stripped.startswith("/*"):
                file_comments.append(stripped)
            elif found_syntax and not stripped:
                # Empty line after syntax is ok
                continue
            elif stripped and found_syntax and not stripped.startswith("//"):
                # Non-comment after syntax means we're done with file comments
                break

        result["file_comment"] = self._normalize_comment("\n".join(file_comments))

        # Extract package
        package_match = re.search(r"package\s+([\w.]+)\s*;", content)
        if package_match:
            result["package"] = package_match.group(1)

        # Extract syntax
        syntax_match = re.search(r'syntax\s*=\s*"([^"]+)"\s*;', content)
        if syntax_match:
            result["syntax"] = syntax_match.group(1)

        # Parse messages, enums, and services
        result["messages"] = self._parse_messages(content, lines)
        result["enums"] = self._parse_enums(content, lines)
        result["services"] = self._parse_services(content, lines)

        return result

    def _parse_messages(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse all message definitions from proto content.

        Args:
            content: Full proto file content.
            lines: Split lines for comment extraction.

        Returns:
            List of parsed message dictionaries.
        """
        messages = []
        # Pattern to match message keyword and name
        pattern = r"message\s+(\w+)\s*\{"

        for match in re.finditer(pattern, content):
            msg_name = match.group(1)

            # Find the matching closing brace by counting braces
            start_pos = match.end()
            brace_count = 1
            pos = start_pos

            while pos < len(content) and brace_count > 0:
                if content[pos] == "{":
                    brace_count += 1
                elif content[pos] == "}":
                    brace_count -= 1
                pos += 1

            # Extract message body (between braces)
            msg_body = content[start_pos : pos - 1]

            # Find line number for comment extraction
            line_idx = content[: match.start()].count("\n")
            raw_comment = self._extract_comments_before(lines, line_idx)
            comment = self._normalize_comment(raw_comment)
            # Process cross-references in message-level comments
            comment = self._process_cross_references(comment)

            # Parse fields
            fields = self._parse_fields(msg_body, msg_body.split("\n"))

            messages.append({"name": msg_name, "comment": comment, "fields": fields})

        return messages

    def _parse_fields(self, body: str, body_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse fields from a message or other block.

        Args:
            body: Body text to parse.
            body_lines: Split body lines for comment extraction.

        Returns:
            List of parsed field dictionaries.
        """
        fields = []
        # Pattern to match field declarations
        # Matches: [repeated|optional] type name = number;
        pattern = r"(repeated|optional)?\s*(\w+)\s+(\w+)\s*=\s*(\d+)\s*;"

        for match in re.finditer(pattern, body):
            label = match.group(1) or ""
            field_type = match.group(2)
            field_name = match.group(3)
            field_number = match.group(4)

            # Find line for comment extraction
            line_idx = body[: match.start()].count("\n")

            # If the match includes a leading newline, the actual line is one more
            if line_idx < len(body_lines) and body[match.start() : match.start() + 1] == "\n":
                line_idx += 1

            # Extract preceding comment (raw, with newlines)
            raw_comment = self._extract_comments_before(body_lines, line_idx)

            # Check for inline comment
            if line_idx < len(body_lines):
                _, inline_comment = self._extract_inline_comment(body_lines[line_idx])
                if inline_comment and not raw_comment:
                    raw_comment = inline_comment

            # Normalize comment (remove comment markers but keep newlines for keyword parsing)
            normalized_lines = []
            for line in raw_comment.split("\n"):
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("/*"):
                    stripped = stripped[2:].strip()
                if stripped.endswith("*/"):
                    stripped = stripped[:-2].strip()
                if stripped.startswith("*") and not stripped.startswith("**"):
                    stripped = stripped[1:].strip()
                if stripped:
                    normalized_lines.append(stripped)

            normalized_comment = "\n".join(normalized_lines)

            # Parse AsyncAPI keywords from comment
            description, keywords = self._parse_asyncapi_keywords(normalized_comment)

            fields.append(
                {
                    "name": field_name,
                    "type": field_type,
                    "label": label,
                    "number": field_number,
                    "comment": description,
                    "keywords": keywords,
                }
            )

        return fields

    def _parse_enums(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse all enum definitions from proto content.

        Args:
            content: Full proto file content.
            lines: Split lines for comment extraction.

        Returns:
            List of parsed enum dictionaries.
        """
        enums = []
        # Pattern to match enum keyword and name
        pattern = r"enum\s+(\w+)\s*\{"

        for match in re.finditer(pattern, content):
            enum_name = match.group(1)

            # Find the matching closing brace by counting braces
            start_pos = match.end()
            brace_count = 1
            pos = start_pos

            while pos < len(content) and brace_count > 0:
                if content[pos] == "{":
                    brace_count += 1
                elif content[pos] == "}":
                    brace_count -= 1
                pos += 1

            # Extract enum body (between braces)
            enum_body = content[start_pos : pos - 1]

            # Find line number for comment extraction
            line_idx = content[: match.start()].count("\n")
            raw_comment = self._extract_comments_before(lines, line_idx)
            comment = self._normalize_comment(raw_comment)
            # Process cross-references in enum-level comments
            comment = self._process_cross_references(comment)

            # Parse enum values
            values = self._parse_enum_values(enum_body, enum_body.split("\n"))

            enums.append({"name": enum_name, "comment": comment, "values": values})

        return enums

    def _parse_enum_values(self, body: str, body_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse enum values from an enum body.

        Args:
            body: Enum body text.
            body_lines: Split body lines for comment extraction.

        Returns:
            List of parsed enum value dictionaries.
        """
        values = []
        # Pattern to match enum value declarations
        pattern = r"(\w+)\s*=\s*(\d+)\s*;"

        for match in re.finditer(pattern, body):
            value_name = match.group(1)
            value_number = match.group(2)

            # Find line for comment extraction
            line_idx = body[: match.start()].count("\n")

            # Extract preceding comment
            raw_comment = self._extract_comments_before(body_lines, line_idx)

            # Check for inline comment
            if line_idx < len(body_lines):
                _, inline_comment = self._extract_inline_comment(body_lines[line_idx])
                if inline_comment and not raw_comment:
                    raw_comment = inline_comment

            comment = self._normalize_comment(raw_comment)
            # Process cross-references in enum value comments
            comment = self._process_cross_references(comment)

            values.append({"name": value_name, "number": value_number, "comment": comment})

        return values

    def _parse_services(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse all service definitions from proto content.

        Args:
            content: Full proto file content.
            lines: Split lines for comment extraction.

        Returns:
            List of parsed service dictionaries.
        """
        services = []
        # Pattern to match service keyword and name
        pattern = r"service\s+(\w+)\s*\{"

        for match in re.finditer(pattern, content):
            service_name = match.group(1)

            # Find the matching closing brace by counting braces
            start_pos = match.end()
            brace_count = 1
            pos = start_pos

            while pos < len(content) and brace_count > 0:
                if content[pos] == "{":
                    brace_count += 1
                elif content[pos] == "}":
                    brace_count -= 1
                pos += 1

            # Extract service body (between braces)
            service_body = content[start_pos : pos - 1]

            # Find line number for comment extraction
            line_idx = content[: match.start()].count("\n")
            raw_comment = self._extract_comments_before(lines, line_idx)
            comment = self._normalize_comment(raw_comment)
            # Process cross-references in service-level comments
            comment = self._process_cross_references(comment)

            # Parse RPC methods
            methods = self._parse_rpc_methods(service_body, service_body.split("\n"))

            services.append({"name": service_name, "comment": comment, "methods": methods})

        return services

    def _parse_rpc_methods(self, body: str, body_lines: List[str]) -> List[Dict[str, Any]]:
        """Parse RPC methods from a service body.

        Args:
            body: Service body text.
            body_lines: Split body lines for comment extraction.

        Returns:
            List of parsed RPC method dictionaries.
        """
        methods = []
        # Pattern to match RPC declarations
        pattern = r"rpc\s+(\w+)\s*\(\s*(\w+)\s*\)\s*returns\s*\(\s*(\w+)\s*\)\s*;"

        for match in re.finditer(pattern, body):
            method_name = match.group(1)
            request_type = match.group(2)
            response_type = match.group(3)

            # Find line for comment extraction
            line_idx = body[: match.start()].count("\n")

            # Extract preceding comment
            raw_comment = self._extract_comments_before(body_lines, line_idx)

            # Check for inline comment
            if line_idx < len(body_lines):
                _, inline_comment = self._extract_inline_comment(body_lines[line_idx])
                if inline_comment and not raw_comment:
                    raw_comment = inline_comment

            comment = self._normalize_comment(raw_comment)
            # Process cross-references in RPC method comments
            comment = self._process_cross_references(comment)

            methods.append(
                {
                    "name": method_name,
                    "request_type": request_type,
                    "response_type": response_type,
                    "comment": comment,
                }
            )

        return methods

    def _format_parsed_proto(self, parsed: Dict[str, Any], filename: str) -> List[str]:
        """Format parsed proto structure as RST documentation.

        Args:
            parsed: Parsed proto structure.
            filename: Name of the proto file.

        Returns:
            List of RST documentation lines.
        """
        doc_parts = []

        # File-level comment
        if parsed.get("file_comment"):
            doc_parts.append(parsed["file_comment"])
            doc_parts.append("")

        # Package info
        if parsed.get("package"):
            doc_parts.append(f"**Package:** ``{parsed['package']}``")
            doc_parts.append("")

        # Messages
        if parsed.get("messages"):
            doc_parts.append("Messages")
            doc_parts.append("~~~~~~~~")
            doc_parts.append("")

            for msg in parsed["messages"]:
                doc_parts.extend(self._format_message(msg))

        # Enums
        if parsed.get("enums"):
            doc_parts.append("Enumerations")
            doc_parts.append("~~~~~~~~~~~~")
            doc_parts.append("")

            for enum in parsed["enums"]:
                doc_parts.extend(self._format_enum(enum))

        # Services
        if parsed.get("services"):
            doc_parts.append("Services")
            doc_parts.append("~~~~~~~~")
            doc_parts.append("")

            for service in parsed["services"]:
                doc_parts.extend(self._format_service_new(service))

        return doc_parts

    def _format_message(self, msg: Dict[str, Any]) -> List[str]:
        """Format a message definition as RST.

        Args:
            msg: Message dictionary.

        Returns:
            List of RST lines.
        """
        lines = []

        # Add label for cross-referencing
        lines.append(f".. _proto-{msg['name']}:")
        lines.append("")

        # Message header
        lines.append(f"**{msg['name']}**")
        lines.append("")

        if msg.get("comment"):
            lines.append(msg["comment"])
            lines.append("")

        # Message definition
        lines.append(".. code-block:: protobuf")
        lines.append("")
        lines.append(f"   message {msg['name']} {{")

        for field in msg.get("fields", []):
            field_line = "      "
            if field.get("label"):
                field_line += f"{field['label']} "
            field_line += f"{field['type']} {field['name']} = {field['number']};"
            lines.append(field_line)

        lines.append("   }")
        lines.append("")

        # Field descriptions
        has_descriptions = any(f.get("comment") or f.get("keywords") for f in msg.get("fields", []))
        if has_descriptions:
            lines.append("**Fields:**")
            lines.append("")
            for field in msg.get("fields", []):
                field_desc = f"- ``{field['name']}`` ({field['type']})"
                if field.get("comment"):
                    field_desc += f": {field['comment']}"
                lines.append(field_desc)

                # Add AsyncAPI keywords if present
                keywords = field.get("keywords", {})
                if keywords:
                    for key, value in keywords.items():
                        lines.append(f"  - *{key}*: ``{value}``")

            lines.append("")

        return lines

    def _format_enum(self, enum: Dict[str, Any]) -> List[str]:
        """Format an enum definition as RST.

        Args:
            enum: Enum dictionary.

        Returns:
            List of RST lines.
        """
        lines = []

        # Add label for cross-referencing
        lines.append(f".. _proto-{enum['name']}:")
        lines.append("")

        # Enum header
        lines.append(f"**{enum['name']}**")
        lines.append("")

        if enum.get("comment"):
            lines.append(enum["comment"])
            lines.append("")

        # Enum definition
        lines.append(".. code-block:: protobuf")
        lines.append("")
        lines.append(f"   enum {enum['name']} {{")

        for value in enum.get("values", []):
            lines.append(f"      {value['name']} = {value['number']};")

        lines.append("   }")
        lines.append("")

        # Value descriptions
        if any(v.get("comment") for v in enum.get("values", [])):
            lines.append("**Values:**")
            lines.append("")
            for value in enum.get("values", []):
                value_desc = f"- ``{value['name']}``"
                if value.get("comment"):
                    value_desc += f": {value['comment']}"
                lines.append(value_desc)
            lines.append("")

        return lines

    def _format_service_new(self, service: Dict[str, Any]) -> List[str]:
        """Format a service definition as RST.

        Args:
            service: Service dictionary.

        Returns:
            List of RST lines.
        """
        lines = []

        # Add label for cross-referencing
        lines.append(f".. _proto-{service['name']}:")
        lines.append("")

        # Service header
        lines.append(f"**{service['name']}**")
        lines.append("")

        if service.get("comment"):
            lines.append(service["comment"])
            lines.append("")

        # Service definition
        lines.append(".. code-block:: protobuf")
        lines.append("")
        lines.append(f"   service {service['name']} {{")

        for method in service.get("methods", []):
            lines.append(
                f"      rpc {method['name']}({method['request_type']}) "
                f"returns ({method['response_type']});"
            )

        lines.append("   }")
        lines.append("")

        # Method descriptions
        if any(m.get("comment") for m in service.get("methods", [])):
            lines.append("**Methods:**")
            lines.append("")
            for method in service.get("methods", []):
                lines.append(f"- ``{method['name']}``")
                if method.get("comment"):
                    lines.append(f"  {method['comment']}")
                lines.append(f"  Request: ``{method['request_type']}``")
                lines.append(f"  Response: ``{method['response_type']}``")
                lines.append("")

        return lines

    def convert_to_rst(
        self, protodoc_output: Optional[str], package_name: Optional[str] = None
    ) -> str:
        """Convert extracted protobuf documentation to reStructuredText format.

        Args:
            protodoc_output: Raw documentation extracted from proto files.
            package_name: Optional package name for fallback message.

        Returns:
            Formatted RST content.
        """
        if not protodoc_output:
            return ""

        # The output is already formatted as RST
        return protodoc_output

    def extract_and_convert(
        self, proto_files: Optional[List[str]] = None, package_name: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Extract protobuf documentation and convert to RST.

        Args:
            proto_files: Optional list of specific proto files to document.
            package_name: Optional package name for filtering.

        Returns:
            Tuple of (success: bool, rst_content: str)
        """
        # Try to extract documentation
        protodoc_output = self.extract_proto_doc(proto_files, package_name)

        if protodoc_output:
            rst_content = self.convert_to_rst(protodoc_output, package_name)
            return True, rst_content
        else:
            # Return a helpful message if extraction failed
            pkg_info = f"``{package_name}``" if package_name else "the specified files"
            fallback = f"""
.. note::

   Automatic documentation extraction from Protocol Buffer files for {pkg_info}
   was not available. This can happen if:

   - No .proto files were found in the specified path
   - protoc is not installed on the system
   - The proto files have syntax errors

   To generate full API documentation, consider:

   - Installing protoc: https://grpc.io/docs/protoc-installation/
   - Installing protoc-gen-doc:
     ``go install github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc@latest``
   - Or view proto files directly in your project
"""
            return False, fallback
