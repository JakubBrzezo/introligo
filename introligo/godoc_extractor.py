#!/usr/bin/env python
"""Go documentation extractor for Introligo.

This module extracts documentation from Go packages using `go doc` and converts
it to reStructuredText format for inclusion in Sphinx documentation.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class GoDocExtractor:
    """Extract and convert Go documentation to RST format."""

    def __init__(self, package_path: Optional[Path] = None):
        """Initialize the GoDoc extractor.

        Args:
            package_path: Optional path to the Go package directory.
        """
        self.package_path = package_path

    def check_go_available(self) -> bool:
        """Check if Go is installed and available.

        Returns:
            True if Go is available, False otherwise.
        """
        try:
            result = subprocess.run(
                ["go", "version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def extract_package_doc(self, package_name: str) -> Optional[str]:
        """Extract documentation for a Go package using go doc.

        Args:
            package_name: The Go package name (e.g., 'github.com/user/pkg')

        Returns:
            Raw go doc output as string, or None if extraction fails.
        """
        if not self.check_go_available():
            logger.warning("Go is not installed - skipping documentation extraction")
            return None

        try:
            cmd = ["go", "doc", "-all", package_name]
            if self.package_path:
                # Run from package directory
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.package_path),
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            if result.returncode == 0:
                logger.info(f"Successfully extracted documentation for {package_name}")
                return result.stdout
            else:
                logger.warning(f"go doc failed for {package_name}: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while extracting docs for {package_name}")
            return None
        except Exception as e:
            logger.error(f"Error extracting docs for {package_name}: {e}")
            return None

    def convert_to_rst(self, godoc_output: Optional[str]) -> str:
        """Convert go doc output to reStructuredText format.

        Args:
            godoc_output: Raw output from go doc command.

        Returns:
            Formatted RST content.
        """
        if not godoc_output:
            return ""

        lines = godoc_output.split("\n")
        rst_lines: List[str] = []
        in_code_block = False

        for i, line in enumerate(lines):
            # Skip empty lines at the start
            if not rst_lines and not line.strip():
                continue

            # Detect package declaration line (first line typically)
            if i == 0 and line.startswith("package "):
                # Skip package line, we'll add our own title
                continue

            # Detect function/type declarations (lines starting with "func" or "type")
            if re.match(r"^(func|type|const|var)\s+", line):
                # If we were in a code block, close it
                if in_code_block:
                    rst_lines.append("")
                    in_code_block = False

                # Extract the declaration
                rst_lines.append("")
                rst_lines.append(".. code-block:: go")
                rst_lines.append("")
                rst_lines.append("   " + line)
                in_code_block = True
                continue

            # Indented lines after a declaration are part of the signature
            if in_code_block and line.startswith("    "):
                rst_lines.append("   " + line)
                continue

            # End of code block
            if in_code_block and line and not line.startswith("    "):
                rst_lines.append("")
                in_code_block = False

            # Regular documentation line
            if line.strip():
                # Check if it's a section heading (all caps or special format)
                if line.isupper() and len(line.strip()) > 2:
                    rst_lines.append("")
                    rst_lines.append(line.strip())
                    rst_lines.append("~" * len(line.strip()))
                    rst_lines.append("")
                else:
                    rst_lines.append(line)
            else:
                rst_lines.append("")

        # Close any open code block
        if in_code_block:
            rst_lines.append("")

        return "\n".join(rst_lines)

    def extract_and_convert(self, package_name: str) -> Tuple[bool, str]:
        """Extract Go documentation and convert to RST.

        Args:
            package_name: The Go package name to document.

        Returns:
            Tuple of (success: bool, rst_content: str)
        """
        # Try to extract documentation
        godoc_output = self.extract_package_doc(package_name)

        if godoc_output:
            rst_content = self.convert_to_rst(godoc_output)
            return True, rst_content
        else:
            # Return a helpful message if extraction failed
            fallback = f"""
.. note::

   Automatic documentation extraction from Go package ``{package_name}``
   was not available. This can happen if:

   - Go is not installed on the system
   - The package path is not accessible
   - The package has not been downloaded (try ``go get {package_name}``)

   To view the full API documentation:

   - Visit https://pkg.go.dev/{package_name}
   - Or run: ``go doc -all {package_name}``
"""
            return False, fallback

    def extract_multiple_packages(self, package_names: List[str]) -> List[Tuple[str, bool, str]]:
        """Extract documentation for multiple Go packages.

        Args:
            package_names: List of package names to document.

        Returns:
            List of tuples: (package_name, success, rst_content)
        """
        results = []
        for package_name in package_names:
            success, content = self.extract_and_convert(package_name)
            results.append((package_name, success, content))
        return results
