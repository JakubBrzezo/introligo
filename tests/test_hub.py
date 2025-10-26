"""Tests for documentation hub functionality."""

from pathlib import Path
from textwrap import dedent

import pytest

from introligo.__main__ import IntroligoGenerator
from introligo.hub import DocumentationHub, DocumentType


@pytest.fixture
def hub_test_project(tmp_path):
    """Create a test project with various documentation files."""
    # Create project structure
    (tmp_path / "docs").mkdir()
    (tmp_path / "examples").mkdir()

    # Create README
    (tmp_path / "README.md").write_text(
        dedent("""
        # Test Project

        This is a test project for the documentation hub.

        ## Features

        - Feature 1
        - Feature 2
        """)
    )

    # Create CHANGELOG
    (tmp_path / "CHANGELOG.md").write_text(
        dedent("""
        # Changelog

        ## Version 1.0.0

        - Initial release
        """)
    )

    # Create CONTRIBUTING
    (tmp_path / "CONTRIBUTING.md").write_text(
        dedent("""
        # Contributing

        We welcome contributions!
        """)
    )

    # Create LICENSE
    (tmp_path / "LICENSE").write_text(
        dedent("""
        MIT License

        Copyright (c) 2025 Test
        """)
    )

    # Create some docs
    (tmp_path / "docs" / "guide.md").write_text(
        dedent("""
        # User Guide

        This is a user guide.
        """)
    )

    (tmp_path / "docs" / "tutorial.md").write_text(
        dedent("""
        # Tutorial

        Step by step tutorial.
        """)
    )

    return tmp_path


def test_hub_discovery_disabled_by_default(tmp_path, hub_test_project):
    """Test that hub discovery is disabled by default."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        dedent("""
        index:
          title: "Test Docs"

        modules:
          test:
            title: "Test"
        """)
    )

    config = {
        "index": {"title": "Test Docs"},
        "modules": {"test": {"title": "Test"}},
    }

    hub = DocumentationHub(config_file, config)
    assert not hub.is_enabled()


def test_hub_discovery_enabled(tmp_path, hub_test_project):
    """Test that hub discovery works when enabled."""
    config_file = hub_test_project / "config.yaml"
    config_file.write_text(
        dedent("""
        index:
          title: "Test Docs Hub"

        discovery:
          enabled: true
          scan_paths:
            - "."
          auto_include:
            readme: true
            changelog: true
            contributing: true
            license: true
            markdown_docs: "docs/**/*.md"
        """)
    )

    config = {
        "index": {"title": "Test Docs Hub"},
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {
                "readme": True,
                "changelog": True,
                "contributing": True,
                "license": True,
                "markdown_docs": "docs/**/*.md",
            },
        },
    }

    hub = DocumentationHub(config_file, config)
    assert hub.is_enabled()

    discovered = hub.discover_documentation()

    # Should discover README, CHANGELOG, CONTRIBUTING, LICENSE, and 2 docs
    assert len(discovered) >= 4  # At least the main files

    # Check that we found expected document types
    doc_types = {doc["type"] for doc in discovered}
    assert DocumentType.README in doc_types
    assert DocumentType.CHANGELOG in doc_types
    assert DocumentType.CONTRIBUTING in doc_types
    assert DocumentType.LICENSE in doc_types


def test_hub_categorization(tmp_path, hub_test_project):
    """Test that documents are categorized correctly."""
    config_file = hub_test_project / "config.yaml"

    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {
                "readme": True,
                "changelog": True,
            },
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Check categories
    for doc in discovered:
        if doc["type"] == DocumentType.README:
            # Root README should be in getting_started
            if doc["relative_path"] == Path("README.md"):
                assert doc["category"] == "getting_started"
        elif doc["type"] == DocumentType.CHANGELOG:
            assert doc["category"] == "about"


def test_hub_module_generation(tmp_path, hub_test_project):
    """Test that hub generates module configurations."""
    config_file = hub_test_project / "config.yaml"

    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {
                "readme": True,
                "changelog": True,
            },
        },
    }

    hub = DocumentationHub(config_file, config)
    hub.discover_documentation()
    modules = hub.generate_hub_modules()

    assert len(modules) > 0

    # Should have created category modules
    assert any("getting_started" in key for key in modules)
    assert any("about" in key for key in modules)

    # Check that modules have correct structure
    for _module_id, module_config in modules.items():
        assert "title" in module_config
        if "parent" in module_config:
            # This is a doc module
            assert "file_includes" in module_config or "description" in module_config


def test_hub_integration_with_generator(tmp_path, hub_test_project):
    """Test that hub integrates with IntroligoGenerator."""
    config_file = hub_test_project / "config.yaml"
    config_file.write_text(
        dedent("""
        index:
          title: "Test Docs Hub"

        discovery:
          enabled: true
          scan_paths:
            - "."
          auto_include:
            readme: true
            changelog: true

        modules: {}
        """)
    )

    output_dir = tmp_path / "output"
    generator = IntroligoGenerator(
        config_file=config_file,
        output_dir=output_dir,
        dry_run=True,
    )

    # This should load config and discover docs
    generator.load_config()

    # Check that modules were added
    modules = generator.config.get("modules", {})
    assert len(modules) > 0

    # Check that hub was initialized
    assert generator.hub is not None
    assert generator.hub.is_enabled()


def test_hub_discovery_not_enabled_returns_empty(tmp_path):
    """Test that disabled discovery returns empty list."""
    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": False}}

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    assert discovered == []


def test_hub_auto_include_options_false(tmp_path, hub_test_project):
    """Test that auto_include options can be disabled."""
    config_file = hub_test_project / "config.yaml"

    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {
                "readme": False,
                "changelog": False,
                "contributing": False,
                "license": False,
            },
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Should not discover anything since all options are False
    assert len(discovered) == 0


def test_hub_nonexistent_scan_path(tmp_path):
    """Test that nonexistent scan paths are handled gracefully."""
    config_file = tmp_path / "config.yaml"

    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["nonexistent_dir"],
            "auto_include": {
                "readme": True,
                "changelog": True,
            },
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Should return empty list without error
    assert discovered == []


def test_hub_exclude_patterns(tmp_path):
    """Test that exclude patterns work correctly."""
    # Create files in excluded directories
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "README.md").write_text("# Node Module README")

    (tmp_path / "_build").mkdir()
    (tmp_path / "_build" / "README.md").write_text("# Build README")

    # Create file in included directory
    (tmp_path / "README.md").write_text("# Root README")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"readme": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Should only find the root README, not the ones in excluded dirs
    assert len(discovered) == 1
    assert discovered[0]["relative_path"] == Path("README.md")


def test_hub_user_defined_exclude_patterns(tmp_path):
    """Test that user-defined exclude patterns work."""
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "README.md").write_text("# Private README")
    (tmp_path / "README.md").write_text("# Root README")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"readme": True},
            "exclude_patterns": ["private"],
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Should only find root README
    assert len(discovered) == 1
    assert "private" not in str(discovered[0]["relative_path"])


def test_hub_title_extraction_from_rst(tmp_path):
    """Test title extraction from RST files."""
    rst_file = tmp_path / "doc.rst"
    rst_file.write_text(
        dedent("""
        Documentation Title
        ===================

        Some content here.
        """)
    )

    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": True}}

    hub = DocumentationHub(config_file, config)
    title = hub._extract_title_from_file(rst_file)

    assert title == "Documentation Title"


def test_hub_title_extraction_fallback_to_filename(tmp_path):
    """Test title extraction falls back to filename."""
    doc_file = tmp_path / "my-important-doc.md"
    doc_file.write_text("No headings in this file.")

    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": True}}

    hub = DocumentationHub(config_file, config)
    title = hub._extract_title_from_file(doc_file)

    assert title == "My Important Doc"


def test_hub_title_extraction_handles_read_error(tmp_path):
    """Test title extraction handles file read errors."""
    doc_file = tmp_path / "unreadable.md"
    doc_file.write_text("# Title")
    doc_file.chmod(0o000)  # Make file unreadable

    try:
        config_file = tmp_path / "config.yaml"
        config = {"discovery": {"enabled": True}}

        hub = DocumentationHub(config_file, config)
        title = hub._extract_title_from_file(doc_file)

        # Should fallback to filename
        assert title == "Unreadable"
    finally:
        doc_file.chmod(0o644)  # Restore permissions for cleanup


def test_hub_pattern_discovery_skips_directories(tmp_path):
    """Test that pattern discovery skips directories."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide")
    (tmp_path / "docs" / "subdir").mkdir()  # This is a directory, not a file

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {
                "markdown_docs": "docs/**/*"  # Will match both files and dirs
            },
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Should only find the file, not the directory
    assert len(discovered) == 1
    assert discovered[0]["path"].is_file()


def test_hub_changelog_variants(tmp_path):
    """Test that different CHANGELOG variants are discovered."""
    (tmp_path / "CHANGELOG").write_text("Plain CHANGELOG")
    (tmp_path / "HISTORY.md").write_text("# History")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"changelog": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Should find both CHANGELOG variants
    assert len(discovered) >= 2
    filenames = {doc["path"].name for doc in discovered}
    assert "CHANGELOG" in filenames or "HISTORY.md" in filenames


def test_hub_license_variants(tmp_path):
    """Test that different LICENSE variants are discovered."""
    (tmp_path / "LICENSE.txt").write_text("MIT License")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"license": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    assert len(discovered) == 1
    assert discovered[0]["path"].name == "LICENSE.txt"


def test_hub_contributing_variants(tmp_path):
    """Test that different CONTRIBUTING variants are discovered."""
    (tmp_path / "CONTRIBUTING").write_text("Contributing guidelines")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"contributing": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    assert len(discovered) == 1
    assert discovered[0]["path"].name == "CONTRIBUTING"


def test_hub_categorize_readme_in_examples(tmp_path):
    """Test that READMEs in examples/ are categorized as guides."""
    (tmp_path / "examples").mkdir()
    readme = tmp_path / "examples" / "README.md"
    readme.write_text("# Example README")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"readme": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Find the examples README
    examples_readme = [d for d in discovered if "examples" in str(d["relative_path"])]
    assert len(examples_readme) > 0
    assert examples_readme[0]["category"] == "guides"


def test_hub_categorize_readme_in_tutorials(tmp_path):
    """Test that READMEs in tutorials/ are categorized as guides."""
    (tmp_path / "tutorials").mkdir()
    readme = tmp_path / "tutorials" / "README.md"
    readme.write_text("# Tutorial README")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"readme": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Find the tutorials README
    tutorial_readme = [d for d in discovered if "tutorials" in str(d["relative_path"])]
    assert len(tutorial_readme) > 0
    assert tutorial_readme[0]["category"] == "guides"


def test_hub_categorize_readme_in_docs(tmp_path):
    """Test that READMEs in docs/ are categorized as guides."""
    (tmp_path / "docs").mkdir()
    readme = tmp_path / "docs" / "README.md"
    readme.write_text("# Docs README")

    config_file = tmp_path / "config.yaml"
    config = {
        "discovery": {
            "enabled": True,
            "scan_paths": ["."],
            "auto_include": {"readme": True},
        },
    }

    hub = DocumentationHub(config_file, config)
    discovered = hub.discover_documentation()

    # Find the docs README
    docs_readme = [d for d in discovered if str(d["relative_path"]).startswith("docs")]
    assert len(docs_readme) > 0
    assert docs_readme[0]["category"] == "guides"


def test_hub_categorize_by_content_api(tmp_path):
    """Test content categorization for API docs."""
    doc = tmp_path / "api_doc.md"
    doc.write_text(
        dedent("""
        # API Reference

        This document describes the API classes and functions.
        Use the method calls to interact with the module.
        """)
    )

    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": True}}

    hub = DocumentationHub(config_file, config)
    category = hub._categorize_by_content(doc)

    assert category == "api"


def test_hub_categorize_by_content_guide(tmp_path):
    """Test content categorization for guides."""
    doc = tmp_path / "guide.md"
    doc.write_text(
        dedent("""
        # Step by Step Tutorial

        This is a walkthrough guide showing how to use the features.
        """)
    )

    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": True}}

    hub = DocumentationHub(config_file, config)
    category = hub._categorize_by_content(doc)

    assert category == "guides"


def test_hub_categorize_by_content_getting_started(tmp_path):
    """Test content categorization for getting started docs."""
    doc = tmp_path / "setup.md"
    doc.write_text(
        dedent("""
        # Installation Instructions

        This document covers installation and setup procedures.
        """)
    )

    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": True}}

    hub = DocumentationHub(config_file, config)
    category = hub._categorize_by_content(doc)

    assert category == "getting_started"


def test_hub_categorize_by_content_handles_exception(tmp_path):
    """Test that content categorization handles read errors."""
    doc = tmp_path / "unreadable.md"
    doc.write_text("# Content")
    doc.chmod(0o000)

    try:
        config_file = tmp_path / "config.yaml"
        config = {"discovery": {"enabled": True}}

        hub = DocumentationHub(config_file, config)
        category = hub._categorize_by_content(doc)

        # Should return default "guides" on error
        assert category == "guides"
    finally:
        doc.chmod(0o644)


def test_hub_generate_modules_empty_discovered_docs(tmp_path):
    """Test that generate_hub_modules returns empty dict when no docs discovered."""
    config_file = tmp_path / "config.yaml"
    config = {"discovery": {"enabled": True}}

    hub = DocumentationHub(config_file, config)
    # Don't call discover_documentation, so discovered_docs is empty

    modules = hub.generate_hub_modules()

    assert modules == {}
