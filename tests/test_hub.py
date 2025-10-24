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
