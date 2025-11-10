#!/usr/bin/env python
"""Rust documentation extractor for Introligo.

This module extracts documentation from Rust crates using `cargo doc` and converts
it to reStructuredText format for inclusion in Sphinx documentation.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RustDocExtractor:
    """Extract and convert Rust documentation to RST format."""

    def __init__(self, crate_path: Optional[Path] = None):
        """Initialize the RustDoc extractor.

        Args:
            crate_path: Optional path to the Rust crate directory.
        """
        self.crate_path = crate_path

    def check_cargo_available(self) -> bool:
        """Check if Cargo is installed and available.

        Returns:
            True if Cargo is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["cargo", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def extract_crate_metadata(self) -> Optional[Dict]:
        """Extract crate metadata from Cargo.toml.

        Returns:
            Dictionary with crate metadata, or None if extraction fails.
        """
        if not self.crate_path:
            return None

        try:
            cmd = ["cargo", "metadata", "--no-deps", "--format-version=1"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.crate_path),
            )

            if result.returncode == 0:
                metadata = json.loads(result.stdout)
                # Get the first package (usually the current crate)
                if metadata.get("packages"):
                    package: Dict = metadata["packages"][0]
                    return package
            return None

        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not extract crate metadata: {e}")
            return None

    def extract_crate_doc(self, crate_name: Optional[str] = None) -> Optional[str]:
        """Extract documentation for a Rust crate using cargo doc.

        Args:
            crate_name: The Rust crate name (optional, uses current crate if not provided)

        Returns:
            Summary documentation as string, or None if extraction fails.
        """
        if not self.crate_path:
            logger.warning("No crate path specified")
            return None

        # If Cargo is not available, fall back to source parsing immediately
        if not self.check_cargo_available():
            return self._extract_without_cargo()

        try:
            return self._extract_with_cargo(crate_name)
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while building docs for crate at {self.crate_path}")
            return None
        except Exception as e:
            logger.error(f"Error building docs: {e}")
            return None

    def _extract_without_cargo(self) -> Optional[str]:
        """Extract documentation when Cargo is not available.

        Returns:
            Documentation string, or None if extraction fails.
        """
        logger.warning("Cargo is not installed - using direct source parsing")
        lib_rs = self.crate_path / "src" / "lib.rs" if self.crate_path else None
        main_rs = self.crate_path / "src" / "main.rs" if self.crate_path else None
        source_file = (
            lib_rs
            if lib_rs and lib_rs.exists()
            else (main_rs if main_rs and main_rs.exists() else None)
        )
        if source_file:
            return self._parse_rust_source(source_file)
        return None

    def _extract_with_cargo(self, crate_name: Optional[str] = None) -> Optional[str]:
        """Extract documentation using Cargo toolchain.

        Args:
            crate_name: The crate name (optional).

        Returns:
            Documentation string, or None if extraction fails.
        """
        # Try to generate JSON documentation (requires Rust 1.78+)
        logger.info(f"Attempting to generate rustdoc JSON for crate at {self.crate_path}")
        json_doc = self._try_rustdoc_json(crate_name)

        if json_doc:
            logger.info("Successfully extracted documentation from rustdoc JSON")
            return json_doc

        # Prefer source parsing over HTML parsing - it produces better formatted output
        logger.info("Rustdoc JSON not available, using direct source parsing")
        lib_rs = self.crate_path / "src" / "lib.rs" if self.crate_path else None
        main_rs = self.crate_path / "src" / "main.rs" if self.crate_path else None
        source_file = (
            lib_rs
            if lib_rs and lib_rs.exists()
            else (main_rs if main_rs and main_rs.exists() else None)
        )

        if source_file:
            logger.info(f"Parsing source file: {source_file}")
            return self._parse_rust_source(source_file)

        # Last resort: Try cargo doc HTML parsing (produces less formatted output)
        logger.info("Source file not found, trying cargo doc HTML parsing")
        cmd = ["cargo", "doc", "--no-deps", "--message-format=json"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(self.crate_path),
        )

        if result.returncode == 0:
            logger.info(f"Successfully built HTML documentation for crate at {self.crate_path}")

            # Try to extract from generated docs
            extracted = self._extract_from_cargo_doc(crate_name)
            if extracted:
                logger.info("Successfully extracted documentation from cargo doc HTML output")
                return extracted

        logger.warning("All extraction methods failed")
        return None

    def _try_rustdoc_json(self, crate_name: Optional[str] = None) -> Optional[str]:
        """Try to generate and parse rustdoc JSON output.

        Args:
            crate_name: The crate name (optional).

        Returns:
            Extracted documentation as string, or None if JSON output is not available.
        """
        try:
            # Try using RUSTDOCFLAGS to enable JSON output
            cmd = [
                "cargo",
                "rustdoc",
                "--lib",
                "--",
                "-Z",
                "unstable-options",
                "--output-format",
                "json",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.crate_path),
            )

            if result.returncode == 0 and self.crate_path:
                # Look for generated JSON file
                target_doc = self.crate_path / "target" / "doc"

                # Get the actual crate name from metadata if not provided
                if not crate_name:
                    metadata = self.extract_crate_metadata()
                    if metadata:
                        crate_name = metadata.get("name", "").replace("-", "_")

                if crate_name:
                    json_file = target_doc / f"{crate_name}.json"
                    if json_file.exists():
                        return self._parse_rustdoc_json(json_file)

            return None

        except (subprocess.TimeoutExpired, Exception) as e:
            logger.debug(f"Rustdoc JSON generation not available: {e}")
            return None

    def _parse_rustdoc_json(self, json_file: Path) -> Optional[str]:
        """Parse rustdoc JSON output to extract documentation.

        Args:
            json_file: Path to the JSON file.

        Returns:
            Formatted documentation as string, or None if parsing fails.
        """
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            doc_parts = []

            # Extract crate-level documentation
            if "index" in data and "crate_id" in data["index"]:
                crate_id = data["index"]["crate_id"]
                if crate_id in data["index"]["items"]:
                    crate_item = data["index"]["items"][crate_id]
                    if "docs" in crate_item and crate_item["docs"]:
                        doc_parts.append(crate_item["docs"])
                        doc_parts.append("")

            # Extract items (this would need more comprehensive parsing)
            # For now, fall back to source parsing
            return None

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not parse rustdoc JSON: {e}")
            return None

    def _extract_from_cargo_doc(self, crate_name: Optional[str] = None) -> Optional[str]:
        """Extract documentation from cargo doc generated files.

        Args:
            crate_name: The crate name (optional).

        Returns:
            Extracted documentation as string, or None if extraction fails.
        """
        try:
            # Get crate name from metadata
            if not crate_name:
                metadata = self.extract_crate_metadata()
                if metadata:
                    crate_name = metadata.get("name", "").replace("-", "_")

            if not crate_name or not self.crate_path:
                return None

            # Look for generated documentation in target/doc
            target_doc = self.crate_path / "target" / "doc" / crate_name

            if not target_doc.exists():
                logger.debug(f"Documentation directory not found: {target_doc}")
                return None

            # Check for index.html
            index_html = target_doc / "index.html"

            if index_html.exists():
                logger.info(f"Found generated documentation at {index_html}")
                # Parse HTML to extract text documentation
                return self._parse_rustdoc_html(index_html, crate_name)

            return None

        except Exception as e:
            logger.warning(f"Could not extract from cargo doc output: {e}")
            return None

    def _parse_rustdoc_html(self, html_file: Path, crate_name: str) -> Optional[str]:
        """Parse rustdoc HTML to extract documentation.

        Args:
            html_file: Path to the HTML file.
            crate_name: Name of the crate.

        Returns:
            Extracted documentation as string, or None if parsing fails.
        """
        try:
            with open(html_file, encoding="utf-8") as f:
                html_content = f.read()

            doc_parts = []

            # Extract main documentation from HTML
            # Look for the module documentation section
            module_doc_match = re.search(
                r'<div class="docblock"[^>]*>(.*?)</div>', html_content, re.DOTALL
            )

            if module_doc_match:
                doc_html = module_doc_match.group(1)

                # Convert HTML to text (basic conversion)
                # Remove HTML tags
                doc_text = re.sub(r"<[^>]+>", "", doc_html)
                # Decode HTML entities
                doc_text = doc_text.replace("&lt;", "<").replace("&gt;", ">")
                doc_text = doc_text.replace("&amp;", "&").replace("&quot;", '"')
                # Clean up whitespace
                lines = [line.strip() for line in doc_text.split("\n")]
                doc_text = "\n".join(line for line in lines if line)

                if doc_text:
                    doc_parts.append("Crate Documentation (from cargo doc)")
                    doc_parts.append("=" * 40)
                    doc_parts.append("")
                    doc_parts.append(doc_text)
                    doc_parts.append("")
                    logger.info("Successfully extracted module documentation from HTML")

            # Also try to get list of public items
            # Look for function/struct/enum listings
            items_match = re.findall(
                r'<h3[^>]*><a[^>]+class="[^"]*(?:fn|struct|enum)[^"]*"[^>]*>([^<]+)</a>',
                html_content,
            )

            if items_match:
                doc_parts.append("")
                doc_parts.append("Public Items")
                doc_parts.append("=" * 20)
                doc_parts.append("")
                for item in items_match[:20]:  # Limit to first 20 items
                    doc_parts.append(f"- {item}")
                    doc_parts.append("")
                logger.info(f"Found {len(items_match)} public items in documentation")

            if doc_parts:
                return "\n".join(doc_parts)

            return None

        except Exception as e:
            logger.warning(f"Could not parse rustdoc HTML: {e}")
            return None

    def _parse_rust_source(self, source_file: Path) -> str:
        """Parse Rust source file to extract documentation.

        Args:
            source_file: Path to the Rust source file.

        Returns:
            Documentation content as string.
        """
        try:
            logger.info(f"Parsing Rust source file directly: {source_file}")

            with open(source_file, encoding="utf-8") as f:
                content = f.read()

            doc_parts = []

            # Add note about extraction method
            doc_parts.append(".. note::")
            doc_parts.append("")
            doc_parts.append("   Documentation extracted from Rust source code via direct parsing.")
            doc_parts.append(
                "   This provides well-formatted documentation with proper RST structure."
            )
            doc_parts.append("")
            doc_parts.append("")

            # Extract module-level documentation (//! comments)
            # Use [ \t]* instead of \s* to avoid matching newlines
            module_docs = re.findall(r"//![ \t]*(.*)$", content, re.MULTILINE)
            if module_docs:
                # Process module docs to convert markdown headers to RST
                processed_docs = self._process_doc_comments(module_docs)
                # Filter out leading empty lines
                while processed_docs and not processed_docs[0].strip():
                    processed_docs.pop(0)
                doc_parts.extend(processed_docs)
                doc_parts.append("")
                doc_parts.append("")

            # Extract public items with their documentation
            items = self._extract_public_items(content)
            if items:
                # Add API reference header at lower level (---) to reduce ToC clutter
                doc_parts.append("API Reference")
                doc_parts.append("-" * 13)
                doc_parts.append("")
                doc_parts.extend(items)

            item_count = len(items) if items else 0
            logger.info(f"Successfully parsed {item_count} public items from source")
            return "\n".join(doc_parts)

        except Exception as e:
            logger.error(f"Error parsing Rust source {source_file}: {e}")
            return ""

    def _extract_public_items(self, content: str) -> List[str]:
        """Extract public functions, structs, enums, and traits from Rust source.

        Args:
            content: Rust source code content.

        Returns:
            List of formatted documentation strings.
        """
        # Categorize items by type
        functions = []
        structs = []
        enums = []
        traits = []
        others = []

        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for doc comments (/// or /** */)
            if line.startswith("///") or line.startswith("/**"):
                doc_lines, i = self._collect_doc_comments(lines, i)
                item_doc, i = self._process_documented_item(lines, i, doc_lines)

                if item_doc:
                    signature = item_doc["signature"]
                    doc = item_doc["doc"]

                    # Categorize by type
                    if "pub fn " in signature or "pub async fn " in signature:
                        functions.append(doc)
                    elif "pub struct " in signature:
                        structs.append(doc)
                    elif "pub enum " in signature:
                        enums.append(doc)
                    elif "pub trait " in signature:
                        traits.append(doc)
                    else:
                        others.append(doc)
                    continue

            i += 1

        # Assemble the results with section headers
        return self._assemble_categorized_items(
            structs, enums, functions, traits=traits, others=others
        )

    def _collect_doc_comments(self, lines: List[str], start_index: int) -> Tuple[List[str], int]:
        """Collect consecutive doc comment lines.

        Args:
            lines: All source lines.
            start_index: Starting index for collection.

        Returns:
            Tuple of (doc_lines, next_index).
        """
        doc_lines = []
        i = start_index

        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("///") or line.startswith("/**"):
                cleaned = line[3:].strip()
                doc_lines.append(cleaned)
                i += 1
            else:
                break

        return doc_lines, i

    def _process_documented_item(
        self, lines: List[str], start_index: int, doc_lines: List[str]
    ) -> Tuple[Optional[Dict], int]:
        """Process a documented public item.

        Args:
            lines: All source lines.
            start_index: Starting index (should be at the item definition).
            doc_lines: Documentation comment lines.

        Returns:
            Tuple of (item_dict or None, next_index).
        """
        if start_index >= len(lines):
            return None, start_index

        item_line = lines[start_index].strip()
        if not item_line.startswith("pub "):
            return None, start_index

        # Extract the signature
        signature, i = self._extract_signature(lines, start_index)

        # Process doc lines to convert markdown to RST
        processed_docs = self._process_doc_comments(doc_lines)

        # Format the item
        item_doc = []
        item_doc.append("")
        item_doc.append(".. code-block:: rust")
        item_doc.append("")
        item_doc.append(f"   {signature}")
        item_doc.append("")
        item_doc.extend(processed_docs)
        item_doc.append("")

        return {"signature": signature, "doc": item_doc}, i

    def _extract_signature(self, lines: List[str], start_index: int) -> Tuple[str, int]:
        """Extract a complete signature from lines.

        Args:
            lines: All source lines.
            start_index: Starting index.

        Returns:
            Tuple of (signature, next_index).
        """
        signature = lines[start_index].strip()
        i = start_index + 1

        # For multi-line signatures, collect until we hit {, ;, or where
        while i < len(lines) and not any(c in signature for c in ["{", ";"]):
            next_line = lines[i].strip()
            if next_line:
                signature += " " + next_line
            i += 1
            if "where" in next_line or "{" in next_line or ";" in next_line:
                break

        # Clean up signature
        signature = signature.split("{")[0].split("where")[0].strip()
        return signature, i

    def _assemble_categorized_items(
        self,
        structs: List[List[str]],
        enums: List[List[str]],
        functions: List[List[str]],
        *,
        traits: List[List[str]],
        others: List[List[str]],
    ) -> List[str]:
        """Assemble categorized items into a single result list.

        Args:
            structs: List of struct documentation.
            enums: List of enum documentation.
            functions: List of function documentation.
            traits: List of trait documentation.
            others: List of other item documentation.

        Returns:
            Assembled list of documentation strings.
        """
        result = []

        if structs:
            result.append("Structs")
            result.append("~~~~~~~")
            result.append("")
            for struct_doc in structs:
                result.extend(struct_doc)

        if enums:
            result.append("Enumerations")
            result.append("~~~~~~~~~~~~")
            result.append("")
            for enum_doc in enums:
                result.extend(enum_doc)

        if functions:
            result.append("Functions")
            result.append("~~~~~~~~~")
            result.append("")
            for func_doc in functions:
                result.extend(func_doc)

        if traits:
            result.append("Traits")
            result.append("~~~~~~")
            result.append("")
            for trait_doc in traits:
                result.extend(trait_doc)

        if others:
            result.append("Other Items")
            result.append("~~~~~~~~~~~")
            result.append("")
            for other_doc in others:
                result.extend(other_doc)

        return result

    def _process_doc_comments(self, doc_lines: List[str]) -> List[str]:
        """Process Rust doc comments and convert markdown to RST.

        Args:
            doc_lines: List of documentation comment lines.

        Returns:
            Processed lines with markdown converted to RST.
        """
        result = []
        in_code_block = False

        # Rustdoc standard section headers that should be bold, not headers
        rustdoc_sections = {
            "Arguments",
            "Parameters",
            "Returns",
            "Return",
            "Return Value",
            "Errors",
            "Error",
            "Panics",
            "Panic",
            "Safety",
            "Example",
            "Examples",
            "Note",
            "Notes",
            "Warning",
            "Warnings",
            "See Also",
            "See also",
        }

        for line in doc_lines:
            # Detect code fences
            if line.strip().startswith("```"):
                if in_code_block:
                    # End code block
                    result.append("")
                    in_code_block = False
                else:
                    # Start code block
                    lang = line.strip()[3:].strip() or "rust"
                    result.append("")
                    result.append(f".. code-block:: {lang}")
                    result.append("")
                    in_code_block = True
                continue

            if in_code_block:
                # Indent code block content
                result.append(f"   {line}")
            else:
                # Convert markdown headers to RST
                # Check for rustdoc standard sections first
                if line.startswith("# "):
                    title = line[2:].strip()

                    # If this is a standard rustdoc section, make it bold instead of a header
                    if title in rustdoc_sections:
                        result.append("")
                        result.append(f"**{title}:**")
                        result.append("")
                    else:
                        # Module-level headers -> use ===
                        result.append("")
                        result.append(title)
                        result.append("=" * len(title))
                        result.append("")
                elif line.startswith("## "):
                    # Module subsections -> use ---
                    title = line[3:].strip()
                    result.append("")
                    result.append(title)
                    result.append("-" * len(title))
                    result.append("")
                elif line.startswith("### "):
                    # Minor subsections -> use ~~~
                    title = line[4:].strip()
                    result.append("")
                    result.append(title)
                    result.append("~" * len(title))
                    result.append("")
                elif line.strip().startswith("- ") or line.strip().startswith("* "):
                    # Keep list items as-is
                    result.append(line)
                else:
                    result.append(line)

        return result

    def convert_to_rst(
        self, rustdoc_output: Optional[str], crate_name: Optional[str] = None
    ) -> str:
        """Convert extracted Rust documentation to reStructuredText format.

        Args:
            rustdoc_output: Raw documentation extracted from Rust source.
            crate_name: Optional crate name for fallback message.

        Returns:
            Formatted RST content.
        """
        if not rustdoc_output:
            return ""

        # The output is already reasonably formatted, just return it
        return rustdoc_output

    def extract_and_convert(self, crate_name: Optional[str] = None) -> Tuple[bool, str]:
        """Extract Rust documentation and convert to RST.

        Args:
            crate_name: The Rust crate name (optional).

        Returns:
            Tuple of (success: bool, rst_content: str)
        """
        # Get crate metadata
        metadata = self.extract_crate_metadata()
        if metadata:
            actual_crate_name = metadata.get("name", crate_name or "unknown")
        else:
            actual_crate_name = crate_name or "unknown"

        # Try to extract documentation
        rustdoc_output = self.extract_crate_doc(actual_crate_name)

        if rustdoc_output:
            rst_content = self.convert_to_rst(rustdoc_output, actual_crate_name)
            return True, rst_content
        else:
            # Return a helpful message if extraction failed
            fallback = f"""
.. note::

   Automatic documentation extraction from Rust crate ``{actual_crate_name}``
   was not available. This can happen if:

   - Cargo is not installed on the system
   - The crate path is not accessible
   - The crate has build errors

   To generate full API documentation, consider using:

   - Cargo doc: ``cargo doc --open`` in the crate directory
   - Or view on https://docs.rs/{actual_crate_name}
"""
            return False, fallback

    def extract_multiple_crates(self, crate_paths: List[Path]) -> List[Tuple[str, bool, str]]:
        """Extract documentation for multiple Rust crates.

        Args:
            crate_paths: List of paths to crate directories.

        Returns:
            List of tuples: (crate_name, success, rst_content)
        """
        results = []
        for crate_path in crate_paths:
            # Temporarily set the crate path
            original_path = self.crate_path
            self.crate_path = crate_path

            # Extract metadata to get crate name
            metadata = self.extract_crate_metadata()
            if metadata:
                crate_name = metadata.get("name", str(crate_path.name))
            else:
                crate_name = str(crate_path.name)

            success, content = self.extract_and_convert(crate_name)
            results.append((crate_name, success, content))

            # Restore original path
            self.crate_path = original_path

        return results
