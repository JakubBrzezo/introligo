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
        if not self.check_cargo_available():
            logger.warning("Cargo is not installed - skipping documentation extraction")
            return None

        if not self.crate_path:
            logger.warning("No crate path specified")
            return None

        try:
            # Build documentation with cargo doc
            cmd = ["cargo", "doc", "--no-deps", "--message-format=json"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.crate_path),
            )

            if result.returncode == 0:
                logger.info(f"Successfully built documentation for crate at {self.crate_path}")

                # Extract module-level documentation from lib.rs or main.rs
                lib_rs = self.crate_path / "src" / "lib.rs"
                main_rs = self.crate_path / "src" / "main.rs"

                source_file = lib_rs if lib_rs.exists() else (main_rs if main_rs.exists() else None)

                if source_file:
                    return self._parse_rust_source(source_file)
                return None
            else:
                logger.warning(f"cargo doc failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while building docs for crate at {self.crate_path}")
            return None
        except Exception as e:
            logger.error(f"Error building docs: {e}")
            return None

    def _parse_rust_source(self, source_file: Path) -> str:
        """Parse Rust source file to extract documentation.

        Args:
            source_file: Path to the Rust source file.

        Returns:
            Documentation content as string.
        """
        try:
            with open(source_file, encoding="utf-8") as f:
                content = f.read()

            doc_parts = []

            # Extract module-level documentation (//! comments)
            module_docs = re.findall(r"//!\s*(.+)", content)
            if module_docs:
                doc_parts.append("Module Documentation")
                doc_parts.append("~" * 20)
                doc_parts.append("")
                doc_parts.extend(module_docs)
                doc_parts.append("")

            # Extract public items with their documentation
            items = self._extract_public_items(content)
            if items:
                doc_parts.append("")
                doc_parts.append("Public API")
                doc_parts.append("~" * 10)
                doc_parts.append("")
                doc_parts.extend(items)

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
        result = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Look for doc comments (/// or /** */)
            if line.startswith("///") or line.startswith("/**"):
                doc_lines = []

                # Collect all consecutive doc comments
                while i < len(lines) and (
                    lines[i].strip().startswith("///") or lines[i].strip().startswith("/**")
                ):
                    doc_line = lines[i].strip()
                    if doc_line.startswith("///") or doc_line.startswith("/**"):
                        doc_lines.append(doc_line[3:].strip())
                    i += 1

                # Now look for the item definition (pub fn, pub struct, pub enum, pub trait)
                if i < len(lines):
                    item_line = lines[i].strip()

                    # Check if it's a public item
                    if item_line.startswith("pub "):
                        # Extract the signature
                        signature = item_line
                        i += 1

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

                        # Format the documentation
                        result.append("")
                        result.append(".. code-block:: rust")
                        result.append("")
                        result.append(f"   {signature}")
                        result.append("")

                        if doc_lines:
                            for doc_line in doc_lines:
                                if doc_line:
                                    result.append(doc_line)
                        result.append("")
                        continue

            i += 1

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
