#!/usr/bin/env python
"""PageNode class for representing documentation pages in hierarchy.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import slugify


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
