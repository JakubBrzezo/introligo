#!/usr/bin/env python
"""Java documentation extractor for Introligo.

This module extracts documentation from Java packages using javadoc and converts
it to reStructuredText format for inclusion in Sphinx documentation.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class JavaDocExtractor:
    """Extract and convert Java documentation to RST format."""

    def __init__(self, source_path: Optional[Path] = None):
        """Initialize the JavaDoc extractor.

        Args:
            source_path: Optional path to the Java source directory.
        """
        self.source_path = source_path

    def check_java_available(self) -> bool:
        """Check if Java and javadoc are installed and available.

        Returns:
            True if Java and javadoc are available, False otherwise.
        """
        try:
            # Check Java
            java_result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # Check javadoc
            javadoc_result = subprocess.run(
                ["javadoc", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return java_result.returncode == 0 and javadoc_result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def extract_from_source(self, java_file: Path) -> Optional[str]:
        """Extract documentation directly from Java source file.

        Args:
            java_file: Path to the Java source file.

        Returns:
            Raw Java source with comments, or None if extraction fails.
        """
        try:
            with open(java_file, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading Java file {java_file}: {e}")
            return None

    def parse_java_source(self, source_content: str, class_name: str = "") -> str:
        """Parse Java source and extract key documentation elements.

        Args:
            source_content: The Java source code content.
            class_name: Optional class name for context.

        Returns:
            Formatted RST content with Java documentation.
        """
        if not source_content:
            return ""

        rst_lines: List[str] = []
        lines = source_content.split("\n")
        i = 0
        current_javadoc = []

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Detect Javadoc comment start
            if stripped.startswith("/**"):
                current_javadoc = [line]
                i += 1
                # Collect the entire Javadoc block
                while i < len(lines):
                    javadoc_line = lines[i]
                    current_javadoc.append(javadoc_line)
                    if javadoc_line.strip().endswith("*/"):
                        break
                    i += 1
                i += 1
                # Don't continue - fall through to check if next line is a declaration
                if i >= len(lines):
                    break
                line = lines[i]
                stripped = line.strip()

            # Detect class declaration
            if re.match(r"^(public\s+)?(abstract\s+)?(final\s+)?class\s+\w+", stripped):
                if current_javadoc:
                    # Add the javadoc as a comment block
                    rst_lines.extend(self._convert_javadoc_to_rst(current_javadoc))
                    current_javadoc = []

                # Add class declaration as code block
                rst_lines.append("")
                rst_lines.append(".. code-block:: java")
                rst_lines.append("")
                rst_lines.append("   " + stripped)
                rst_lines.append("")

            # Detect interface declaration
            elif re.match(r"^(public\s+)?(abstract\s+)?interface\s+\w+", stripped):
                if current_javadoc:
                    rst_lines.extend(self._convert_javadoc_to_rst(current_javadoc))
                    current_javadoc = []

                rst_lines.append("")
                rst_lines.append(".. code-block:: java")
                rst_lines.append("")
                rst_lines.append("   " + stripped)
                rst_lines.append("")

            # Detect method declaration
            elif re.match(
                r"^(public|protected|private)\s+(static\s+)?(final\s+)?(\w+(<.*?>)?|\w+\[\])\s+\w+\s*\(",
                stripped,
            ):
                if current_javadoc:
                    rst_lines.extend(self._convert_javadoc_to_rst(current_javadoc))
                    current_javadoc = []

                # Extract method signature (may span multiple lines)
                method_lines = [stripped]
                if "{" not in stripped and ";" not in stripped:
                    i += 1
                    while i < len(lines) and "{" not in lines[i] and ";" not in lines[i]:
                        method_lines.append(lines[i].strip())
                        i += 1
                    if i < len(lines):
                        method_lines.append(lines[i].strip())

                # Clean up the method signature
                method_sig = " ".join(method_lines)
                method_sig = re.sub(r"\s*\{.*", "", method_sig)  # Remove body
                method_sig = re.sub(r"\s*;.*", ";", method_sig)  # Keep semicolon

                rst_lines.append("")
                rst_lines.append(".. code-block:: java")
                rst_lines.append("")
                rst_lines.append("   " + method_sig)
                rst_lines.append("")

            # Detect field declaration
            elif re.match(
                r"^(public|protected|private)\s+(static\s+)?(final\s+)?(\w+(<.*?>)?|\w+\[\])\s+\w+(\s*=.*)?;",
                stripped,
            ):
                if current_javadoc:
                    rst_lines.extend(self._convert_javadoc_to_rst(current_javadoc))
                    current_javadoc = []

                rst_lines.append("")
                rst_lines.append(".. code-block:: java")
                rst_lines.append("")
                rst_lines.append("   " + stripped)
                rst_lines.append("")

            i += 1

        return "\n".join(rst_lines)

    def _convert_javadoc_to_rst(self, javadoc_lines: List[str]) -> List[str]:
        """Convert Javadoc comment to RST formatted text.

        Args:
            javadoc_lines: Lines of Javadoc comment.

        Returns:
            List of RST formatted lines.
        """
        rst_lines = []
        description_lines = []
        params = []
        returns = []
        throws = []

        for line in javadoc_lines:
            # Remove leading/trailing whitespace and comment markers
            clean_line = line.strip()
            clean_line = re.sub(r"^/\*\*", "", clean_line)
            clean_line = re.sub(r"\*/$", "", clean_line)
            clean_line = re.sub(r"^\*\s?", "", clean_line)

            if not clean_line:
                continue

            # Parse Javadoc tags (ignore @author, @version, @since, @see, @deprecated for now)
            if clean_line.startswith("@param"):
                params.append(clean_line)
            elif clean_line.startswith("@return"):
                returns.append(clean_line)
            elif clean_line.startswith("@throws") or clean_line.startswith("@exception"):
                throws.append(clean_line)
            elif (
                clean_line.startswith("@author")
                or clean_line.startswith("@version")
                or clean_line.startswith("@since")
                or clean_line.startswith("@see")
                or clean_line.startswith("@deprecated")
            ):
                # Skip these tags for now - could be added to metadata later
                continue
            else:
                description_lines.append(clean_line)

        # Build RST output
        if description_lines:
            rst_lines.append("")
            for desc_line in description_lines:
                rst_lines.append(desc_line)
            rst_lines.append("")

        if params:
            rst_lines.append("**Parameters:**")
            rst_lines.append("")
            for param in params:
                # Extract param name and description
                match = re.match(r"@param\s+(\w+)\s+(.*)", param)
                if match:
                    param_name, param_desc = match.groups()
                    rst_lines.append(f"- ``{param_name}``: {param_desc}")
            rst_lines.append("")

        if returns:
            rst_lines.append("**Returns:**")
            rst_lines.append("")
            for ret in returns:
                ret_desc = re.sub(r"@returns?\s+", "", ret)
                rst_lines.append(f"  {ret_desc}")
            rst_lines.append("")

        if throws:
            rst_lines.append("**Throws:**")
            rst_lines.append("")
            for throw in throws:
                # Extract exception name and description
                match = re.match(r"@(throws|exception)\s+(\w+)\s+(.*)", throw)
                if match:
                    _, exc_name, exc_desc = match.groups()
                    rst_lines.append(f"- ``{exc_name}``: {exc_desc}")
            rst_lines.append("")

        return rst_lines

    def extract_and_convert(self, java_file: Path, class_name: str = "") -> Tuple[bool, str]:
        """Extract Java documentation and convert to RST.

        Args:
            java_file: Path to the Java source file.
            class_name: Optional class name for context.

        Returns:
            Tuple of (success: bool, rst_content: str)
        """
        # Try to extract from source
        source_content = self.extract_from_source(java_file)

        if source_content:
            rst_content = self.parse_java_source(source_content, class_name)
            return True, rst_content
        else:
            # Return a helpful message if extraction failed
            fallback = f"""
.. note::

   Automatic documentation extraction from Java file ``{java_file.name}``
   was not available. This can happen if:

   - The file path is not accessible
   - The file has encoding issues

   To generate full API documentation, consider using:

   - Javadoc: ``javadoc -d docs {java_file.name}``
   - Or manual documentation below
"""
            return False, fallback

    def extract_multiple_files(self, java_files: List[Path]) -> List[Tuple[str, bool, str]]:
        """Extract documentation for multiple Java files.

        Args:
            java_files: List of Java file paths to document.

        Returns:
            List of tuples: (filename, success, rst_content)
        """
        results = []
        for java_file in java_files:
            # Extract class name from file
            class_name = java_file.stem
            success, content = self.extract_and_convert(java_file, class_name)
            results.append((java_file.name, success, content))
        return results

    def extract_package(self, package_path: Path, package_name: str) -> Tuple[bool, str]:
        """Extract documentation for an entire Java package.

        Args:
            package_path: Path to the package directory.
            package_name: Name of the package (e.g., 'com.example.myapp').

        Returns:
            Tuple of (success: bool, rst_content: str)
        """
        if not package_path.exists() or not package_path.is_dir():
            fallback = f"""
.. note::

   Java package directory ``{package_path}`` not found.

   Package: ``{package_name}``
"""
            return False, fallback

        # Find all Java files in the package
        java_files = list(package_path.glob("*.java"))

        if not java_files:
            fallback = f"""
.. note::

   No Java files found in package directory ``{package_path}``.

   Package: ``{package_name}``
"""
            return False, fallback

        # Extract documentation from all files
        rst_lines = []
        rst_lines.append(f"Package: ``{package_name}``")
        rst_lines.append("=" * (len(package_name) + 11))
        rst_lines.append("")

        any_success = False
        for java_file in sorted(java_files):
            success, content = self.extract_and_convert(java_file)
            if success:
                any_success = True
                rst_lines.append("")
                rst_lines.append(f"{java_file.stem}")
                rst_lines.append("-" * len(java_file.stem))
                rst_lines.append("")
                rst_lines.append(content)

        return any_success, "\n".join(rst_lines)
