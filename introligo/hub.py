#!/usr/bin/env python
"""
Documentation Hub functionality for Introligo.

This module provides auto-discovery and smart organization of documentation
across multiple formats (Markdown, RST, text) scattered throughout a repository.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DocumentType:
    """Enumeration of document types that can be auto-discovered."""

    README = "readme"
    CHANGELOG = "changelog"
    CONTRIBUTING = "contributing"
    LICENSE = "license"
    USER_GUIDE = "user_guide"
    API_DOC = "api_doc"
    TUTORIAL = "tutorial"
    GENERIC = "generic"


class DocumentationHub:
    """Hub for discovering and organizing documentation across a repository.

    The Hub can automatically discover common documentation files (README, CHANGELOG, etc.)
    and organize them into logical sections based on content analysis.
    """

    def __init__(self, config_file: Path, config: Dict[str, Any]):
        """Initialize the Documentation Hub.

        Args:
            config_file: Path to the configuration file (for relative path resolution).
            config: The loaded configuration dictionary.
        """
        self.config_file = config_file
        self.config = config
        self.hub_config = config.get("hub", {})
        self.discovery_config = config.get("discovery", {})
        self.discovered_docs: List[Dict[str, Any]] = []

    def is_enabled(self) -> bool:
        """Check if hub mode is enabled.

        Returns:
            True if hub or discovery is configured, False otherwise.
        """
        return bool(self.hub_config or self.discovery_config)

    def discover_documentation(self) -> List[Dict[str, Any]]:
        """Discover documentation files in the repository.

        Returns:
            List of discovered document dictionaries with type, path, and metadata.
        """
        if not self.discovery_config.get("enabled", False):
            logger.info("Hub discovery not enabled")
            return []

        logger.info("Discovering documentation files...")

        discovered = []
        repo_root = self.config_file.parent

        # Discover specific file types
        auto_include = self.discovery_config.get("auto_include", {})

        if auto_include.get("readme", False):
            discovered.extend(self._discover_readmes(repo_root))

        if auto_include.get("changelog", False):
            discovered.extend(self._discover_changelogs(repo_root))

        if auto_include.get("contributing", False):
            discovered.extend(self._discover_contributing(repo_root))

        if auto_include.get("license", False):
            discovered.extend(self._discover_licenses(repo_root))

        # Discover markdown docs by pattern
        if "markdown_docs" in auto_include:
            pattern = auto_include["markdown_docs"]
            discovered.extend(self._discover_by_pattern(repo_root, pattern, "markdown"))

        self.discovered_docs = discovered
        logger.info(f"✅ Discovered {len(discovered)} documentation files")

        return discovered

    def _discover_readmes(self, root: Path) -> List[Dict[str, Any]]:
        """Discover README files.

        Args:
            root: Root directory to search from.

        Returns:
            List of discovered README files with metadata.
        """
        readmes = []
        scan_paths = self.discovery_config.get("scan_paths", ["."])

        for scan_path in scan_paths:
            search_dir = root / scan_path
            if not search_dir.exists():
                continue

            # Look for README files (case-insensitive)
            for readme_file in search_dir.glob("**/README.md"):
                if self._should_exclude(readme_file, root):
                    continue

                readmes.append(
                    {
                        "type": DocumentType.README,
                        "path": readme_file,
                        "relative_path": readme_file.relative_to(root),
                        "title": self._extract_title_from_file(readme_file),
                        "category": self._categorize_readme(readme_file, root),
                    }
                )
                logger.info(f"  Found README: {readme_file.relative_to(root)}")

        return readmes

    def _discover_changelogs(self, root: Path) -> List[Dict[str, Any]]:
        """Discover CHANGELOG files.

        Args:
            root: Root directory to search from.

        Returns:
            List of discovered CHANGELOG files with metadata.
        """
        changelogs = []
        scan_paths = self.discovery_config.get("scan_paths", ["."])

        for scan_path in scan_paths:
            search_dir = root / scan_path
            if not search_dir.exists():
                continue

            # Look for CHANGELOG files
            for pattern in ["**/CHANGELOG.md", "**/CHANGELOG", "**/HISTORY.md"]:
                for changelog_file in search_dir.glob(pattern):
                    if self._should_exclude(changelog_file, root):
                        continue

                    changelogs.append(
                        {
                            "type": DocumentType.CHANGELOG,
                            "path": changelog_file,
                            "relative_path": changelog_file.relative_to(root),
                            "title": "Changelog",
                            "category": "about",
                        }
                    )
                    logger.info(f"  Found CHANGELOG: {changelog_file.relative_to(root)}")

        return changelogs

    def _discover_contributing(self, root: Path) -> List[Dict[str, Any]]:
        """Discover CONTRIBUTING files.

        Args:
            root: Root directory to search from.

        Returns:
            List of discovered CONTRIBUTING files with metadata.
        """
        contributing = []
        scan_paths = self.discovery_config.get("scan_paths", ["."])

        for scan_path in scan_paths:
            search_dir = root / scan_path
            if not search_dir.exists():
                continue

            for pattern in ["**/CONTRIBUTING.md", "**/CONTRIBUTING"]:
                for contrib_file in search_dir.glob(pattern):
                    if self._should_exclude(contrib_file, root):
                        continue

                    contributing.append(
                        {
                            "type": DocumentType.CONTRIBUTING,
                            "path": contrib_file,
                            "relative_path": contrib_file.relative_to(root),
                            "title": "Contributing",
                            "category": "about",
                        }
                    )
                    logger.info(f"  🤝 Found CONTRIBUTING: {contrib_file.relative_to(root)}")

        return contributing

    def _discover_licenses(self, root: Path) -> List[Dict[str, Any]]:
        """Discover LICENSE files.

        Args:
            root: Root directory to search from.

        Returns:
            List of discovered LICENSE files with metadata.
        """
        licenses = []
        scan_paths = self.discovery_config.get("scan_paths", ["."])

        for scan_path in scan_paths:
            search_dir = root / scan_path
            if not search_dir.exists():
                continue

            for pattern in ["**/LICENSE", "**/LICENSE.md", "**/LICENSE.txt"]:
                for license_file in search_dir.glob(pattern):
                    if self._should_exclude(license_file, root):
                        continue

                    licenses.append(
                        {
                            "type": DocumentType.LICENSE,
                            "path": license_file,
                            "relative_path": license_file.relative_to(root),
                            "title": "License",
                            "category": "about",
                        }
                    )
                    logger.info(f"  ⚖️  Found LICENSE: {license_file.relative_to(root)}")

        return licenses

    def _discover_by_pattern(
        self, root: Path, pattern: str, doc_format: str
    ) -> List[Dict[str, Any]]:
        """Discover documentation files by glob pattern.

        Args:
            root: Root directory to search from.
            pattern: Glob pattern to match files.
            doc_format: Format of the documents (markdown, rst, etc.).

        Returns:
            List of discovered files with metadata.
        """
        discovered = []

        for file_path in root.glob(pattern):
            if self._should_exclude(file_path, root):
                continue

            if not file_path.is_file():
                continue

            discovered.append(
                {
                    "type": DocumentType.GENERIC,
                    "path": file_path,
                    "relative_path": file_path.relative_to(root),
                    "title": self._extract_title_from_file(file_path),
                    "category": self._categorize_by_content(file_path),
                    "format": doc_format,
                }
            )
            logger.info(f"  Found doc: {file_path.relative_to(root)}")

        return discovered

    def _should_exclude(self, file_path: Path, root: Path) -> bool:
        """Check if a file should be excluded from discovery.

        Args:
            file_path: Path to check.
            root: Repository root for relative path calculation.

        Returns:
            True if file should be excluded, False otherwise.
        """
        # Common directories to exclude
        exclude_patterns = [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".tox",
            "build",
            "dist",
            "_build",
            ".pytest_cache",
        ]

        # User-defined exclusions
        user_exclude = self.discovery_config.get("exclude_patterns", [])
        exclude_patterns.extend(user_exclude)

        relative = file_path.relative_to(root)
        return any(exclude in str(relative) for exclude in exclude_patterns)

    def _extract_title_from_file(self, file_path: Path) -> str:
        """Extract title from a file (first heading or filename).

        Args:
            file_path: Path to the file.

        Returns:
            Extracted title string.
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # Try to find first markdown heading
            md_heading = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if md_heading:
                return md_heading.group(1).strip()

            # Try to find RST title (underlined with ==)
            rst_heading = re.search(r"^(.+)\n=+\s*$", content, re.MULTILINE)
            if rst_heading:
                return rst_heading.group(1).strip()

            # Fallback to filename
            return file_path.stem.replace("_", " ").replace("-", " ").title()
        except Exception:
            return file_path.stem.replace("_", " ").replace("-", " ").title()

    def _categorize_readme(self, readme_path: Path, root: Path) -> str:
        """Categorize a README file based on its location and content.

        Args:
            readme_path: Path to README file.
            root: Repository root.

        Returns:
            Category string (getting_started, guides, etc.).
        """
        relative = readme_path.relative_to(root)

        # Root README goes to getting started
        if relative == Path("README.md"):
            return "getting_started"

        # READMEs in examples/ or tutorials/ go to guides
        if "example" in str(relative).lower() or "tutorial" in str(relative).lower():
            return "guides"

        # READMEs in docs/ might be guides
        if "docs" in str(relative).lower():
            return "guides"

        # Default
        return "getting_started"

    def _categorize_by_content(self, file_path: Path) -> str:
        """Categorize a document by analyzing its content.

        Uses keyword analysis to determine the best category.

        Args:
            file_path: Path to the document.

        Returns:
            Category string.
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore").lower()

            # Check for API/reference keywords
            api_keywords = ["api", "reference", "class", "function", "method", "module"]
            if any(keyword in content for keyword in api_keywords):
                return "api"

            # Check for tutorial/guide keywords
            guide_keywords = ["tutorial", "guide", "how to", "step by step", "walkthrough"]
            if any(keyword in content for keyword in guide_keywords):
                return "guides"

            # Check for getting started keywords
            start_keywords = ["installation", "quick start", "getting started", "setup"]
            if any(keyword in content for keyword in start_keywords):
                return "getting_started"

            # Default to guides
            return "guides"
        except Exception:
            return "guides"

    def generate_hub_modules(self) -> Dict[str, Any]:
        """Generate module configurations from discovered documentation.

        Organizes discovered docs into logical modules/sections.

        Returns:
            Dictionary of module configurations to merge with existing config.
        """
        if not self.discovered_docs:
            return {}

        logger.info("🔧 Generating hub module structure...")

        # Organize by category
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for doc in self.discovered_docs:
            category = doc.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(doc)

        # Generate modules
        modules: Dict[str, Any] = {}
        category_titles = {
            "getting_started": "Getting Started",
            "guides": "User Guides",
            "api": "API Reference",
            "about": "About",
            "other": "Documentation",
        }

        for category, docs in categories.items():
            # Create a parent module for this category
            category_id = f"hub_{category}"
            modules[category_id] = {
                "title": category_titles.get(category, category.replace("_", " ").title()),
                "description": f"Auto-discovered {category.replace('_', ' ')} documentation",
            }

            # Add each document as a child module
            for i, doc in enumerate(docs):
                doc_id = f"hub_{category}_{i}"
                doc_path = str(doc["relative_path"])

                modules[doc_id] = {
                    "parent": category_id,
                    "title": doc["title"],
                    "description": f"Documentation from {doc_path}",
                    "file_includes": [doc_path],
                }

                logger.info(f"  📋 Added to hub: {doc['title']} ({category})")

        return modules
