"""Tests for IntroligoGenerator class."""

from pathlib import Path

import pytest

from introligo import IntroligoError, IntroligoGenerator


class TestIntroligoGeneratorInit:
    """Test IntroligoGenerator initialization."""

    def test_generator_initialization(self, sample_yaml_config: Path, temp_dir: Path):
        """Test basic generator initialization."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(
            config_file=sample_yaml_config,
            output_dir=output_dir,
        )

        assert generator.config_file == sample_yaml_config
        assert generator.output_dir == output_dir
        assert generator.generated_dir == output_dir / "generated"
        assert generator.dry_run is False
        assert generator.strict is False

    def test_generator_with_template(self, sample_yaml_config: Path, temp_dir: Path):
        """Test generator with custom template."""
        output_dir = temp_dir / "output"
        template_file = temp_dir / "template.jinja2"
        template_file.write_text("{{ title }}", encoding="utf-8")

        generator = IntroligoGenerator(
            config_file=sample_yaml_config,
            output_dir=output_dir,
            template_file=template_file,
        )

        assert generator.template_file == template_file

    def test_generator_dry_run(self, sample_yaml_config: Path, temp_dir: Path):
        """Test generator in dry-run mode."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(
            config_file=sample_yaml_config,
            output_dir=output_dir,
            dry_run=True,
        )

        assert generator.dry_run is True

    def test_generator_strict_mode(self, sample_yaml_config: Path, temp_dir: Path):
        """Test generator in strict mode."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(
            config_file=sample_yaml_config,
            output_dir=output_dir,
            strict=True,
        )

        assert generator.strict is True


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_config_success(self, sample_yaml_config: Path, temp_dir: Path):
        """Test successful config loading."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()

        assert "modules" in generator.config
        assert "my_module" in generator.config["modules"]

    def test_load_config_missing_file(self, temp_dir: Path):
        """Test loading non-existent config file."""
        missing_file = temp_dir / "missing.yaml"
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(missing_file, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.load_config()

        assert "Configuration file not found" in str(exc_info.value)

    def test_load_config_invalid_yaml(self, temp_dir: Path):
        """Test loading invalid YAML."""
        invalid_file = temp_dir / "invalid.yaml"
        invalid_file.write_text("invalid: yaml: syntax: error:", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(invalid_file, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.load_config()

        assert "Invalid YAML" in str(exc_info.value)

    def test_load_config_not_dict(self, temp_dir: Path):
        """Test loading config that's not a dictionary."""
        config_file = temp_dir / "list.yaml"
        config_file.write_text("- item1\n- item2", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.load_config()

        assert "must be a YAML dictionary" in str(exc_info.value)

    def test_load_config_no_modules(self, temp_dir: Path):
        """Test loading config without modules key."""
        config_file = temp_dir / "no_modules.yaml"
        config_file.write_text("other_key: value", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.load_config()

        assert "must contain a 'modules' dictionary" in str(exc_info.value)

    def test_load_config_with_doxygen(self, doxygen_config: Path, temp_dir: Path):
        """Test loading config with Doxygen settings."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(doxygen_config, output_dir)
        generator.load_config()

        assert "doxygen" in generator.config
        assert generator.doxygen_config["project_name"] == "test_project"

    def test_load_config_with_include(self, sample_include_config: Path, temp_dir: Path):
        """Test loading config with !include directive."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_include_config, output_dir)
        generator.load_config()

        assert "included_module" in generator.config["modules"]


class TestBuildPageTree:
    """Test page tree building."""

    def test_build_page_tree_basic(self, sample_yaml_config: Path, temp_dir: Path):
        """Test building basic page tree."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()
        generator.build_page_tree()

        assert len(generator.page_tree) > 0
        # Check that we have root nodes
        root_ids = {node.page_id for node in generator.page_tree}
        assert "my_module" in root_ids

    def test_build_page_tree_with_parent(self, sample_yaml_config: Path, temp_dir: Path):
        """Test page tree with parent-child relationships."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()
        generator.build_page_tree()

        # Find parent module
        parent_node = None
        for node in generator.page_tree:
            if node.page_id == "parent_module":
                parent_node = node
                break

        assert parent_node is not None
        assert len(parent_node.children) == 1
        assert parent_node.children[0].page_id == "child_module"

    def test_build_page_tree_invalid_config(self, temp_dir: Path):
        """Test building tree with invalid page config."""
        config_file = temp_dir / "invalid_page.yaml"
        config_content = """
modules:
  valid_module:
    title: "Valid"
  invalid_module: "not a dict"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()
        generator.build_page_tree()

        # Should skip invalid module
        ids = {node.page_id for node in generator.page_tree}
        assert "valid_module" in ids
        assert "invalid_module" not in ids


class TestTemplateLoading:
    """Test template loading and processing."""

    def test_load_default_template(self, sample_yaml_config: Path, temp_dir: Path):
        """Test loading default template."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        template = generator.load_template()
        assert template is not None

    def test_load_custom_template(self, sample_yaml_config: Path, temp_dir: Path):
        """Test loading custom template."""
        template_file = temp_dir / "custom.jinja2"
        template_file.write_text("Custom: {{ title }}", encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir, template_file=template_file)

        template = generator.load_template()
        result = template.render(title="Test")
        assert "Custom: Test" in result

    def test_get_default_template(self, sample_yaml_config: Path, temp_dir: Path):
        """Test getting default template content."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        template_content = generator.get_default_template()
        assert "{{ title }}" in template_content
        assert "automodule" in template_content


class TestUsageExamples:
    """Test usage examples processing."""

    def test_process_usage_examples_list_of_dicts(self, sample_yaml_config: Path, temp_dir: Path):
        """Test processing usage examples as list of dicts."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        examples = [
            {
                "title": "Example 1",
                "description": "First example",
                "language": "python",
                "code": "print('hello')",
            }
        ]

        processed = generator.process_usage_examples(examples)
        assert len(processed) == 1
        assert processed[0]["title"] == "Example 1"
        assert processed[0]["code"] == "print('hello')"

    def test_process_usage_examples_list_of_strings(self, sample_yaml_config: Path, temp_dir: Path):
        """Test processing usage examples as list of strings."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        examples = ["code1", "code2"]
        processed = generator.process_usage_examples(examples)

        assert len(processed) == 2
        assert processed[0]["title"] == "Example"
        assert processed[0]["code"] == "code1"

    def test_process_usage_examples_single_dict(self, sample_yaml_config: Path, temp_dir: Path):
        """Test processing single example as dict."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        example = {"title": "Single", "code": "test()"}
        processed = generator.process_usage_examples(example)

        assert len(processed) == 1
        assert processed[0]["title"] == "Single"

    def test_process_usage_examples_single_string(self, sample_yaml_config: Path, temp_dir: Path):
        """Test processing single example as string."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        processed = generator.process_usage_examples("simple code")

        assert len(processed) == 1
        assert processed[0]["code"] == "simple code"

    def test_process_usage_examples_empty(self, sample_yaml_config: Path, temp_dir: Path):
        """Test processing empty examples."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        assert generator.process_usage_examples(None) == []
        assert generator.process_usage_examples([]) == []


class TestMarkdownInclusion:
    """Test markdown file inclusion."""

    def test_include_markdown_file(
        self, config_with_markdown: Path, markdown_file: Path, temp_dir: Path
    ):
        """Test including markdown file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_with_markdown, output_dir)

        content = generator.include_markdown_file(markdown_file.name)
        assert "Version 1.0.0" in content
        assert "Feature 1" in content

    def test_include_markdown_missing_file(self, sample_yaml_config: Path, temp_dir: Path):
        """Test including non-existent markdown file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.include_markdown_file("missing.md")

        assert "Markdown file not found" in str(exc_info.value)

    def test_convert_markdown_to_rst_headers(self, sample_yaml_config: Path, temp_dir: Path):
        """Test markdown to RST header conversion."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        markdown = "# H1\n## H2\n### H3\n#### H4"
        rst = generator._convert_markdown_to_rst(markdown)

        assert "==" in rst  # H1 underline
        assert "---" in rst or "--" in rst  # H2 underline
        assert "~~~" in rst or "~~" in rst  # H3 underline
        assert "^^^" in rst or "^^" in rst  # H4 underline

    def test_convert_markdown_to_rst_code_blocks(self, sample_yaml_config: Path, temp_dir: Path):
        """Test markdown to RST code block conversion."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        markdown = "```python\nprint('hello')\n```"
        rst = generator._convert_markdown_to_rst(markdown)

        assert ".. code-block:: python" in rst
        assert "   print('hello')" in rst

    def test_convert_markdown_skip_changelog_h1(self, sample_yaml_config: Path, temp_dir: Path):
        """Test skipping first Changelog H1."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        markdown = "# Changelog\n## Version 1.0"
        rst = generator._convert_markdown_to_rst(markdown)

        # Changelog H1 should be skipped
        assert "Changelog\n========" not in rst
        assert "Version 1.0" in rst


class TestLatexInclusion:
    """Test LaTeX file inclusion."""

    def test_include_latex_file(self, config_with_latex: Path, latex_file: Path, temp_dir: Path):
        """Test including LaTeX file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_with_latex, output_dir)

        content = generator.include_latex_file(latex_file.name)
        assert ".. math::" in content
        assert "E = mc^2" in content
        assert "\\frac{d}{dx}" in content
        assert "\\sum_{i=1}^{n}" in content

    def test_include_latex_missing_file(self, sample_yaml_config: Path, temp_dir: Path):
        """Test including non-existent LaTeX file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.include_latex_file("missing.tex")

        assert "LaTeX file not found" in str(exc_info.value)

    def test_convert_latex_to_rst_basic(self, sample_yaml_config: Path, temp_dir: Path):
        """Test converting basic LaTeX to RST math directive."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        latex = r"E = mc^2"
        rst = generator._convert_latex_to_rst(latex)

        assert ".. math::" in rst
        assert "   E = mc^2" in rst

    def test_convert_latex_with_document_wrapper(
        self, latex_file_with_document: Path, sample_yaml_config: Path, temp_dir: Path
    ):
        """Test converting LaTeX with document wrapper."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        latex_content = latex_file_with_document.read_text(encoding="utf-8")
        rst = generator._convert_latex_to_rst(latex_content)

        # Document wrapper should be stripped
        assert "\\documentclass" not in rst
        assert "\\usepackage" not in rst
        assert "\\begin{document}" not in rst
        assert "\\end{document}" not in rst

        # Math content should be present
        assert ".. math::" in rst
        assert "E = mc^2" in rst

    def test_convert_latex_multiline(self, sample_yaml_config: Path, temp_dir: Path):
        """Test converting multiline LaTeX equations."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        latex = r"""\begin{align}
E &= mc^2 \\
F &= ma
\end{align}"""
        rst = generator._convert_latex_to_rst(latex)

        assert ".. math::" in rst
        assert "\\begin{align}" in rst
        assert "E &= mc^2" in rst
        assert "F &= ma" in rst


class TestRSTGeneration:
    """Test RST content generation."""

    def test_generate_rst_content_basic(self, sample_yaml_config: Path, temp_dir: Path):
        """Test basic RST content generation."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert node.title in content
        assert "=" in content  # Title underline

    def test_generate_rst_with_doxygen(self, doxygen_config: Path, temp_dir: Path):
        """Test RST generation with Doxygen configuration."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(doxygen_config, output_dir)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        # Find cpp_module node
        node = None
        for n in generator.page_tree:
            if n.page_id == "cpp_module":
                node = n
                break

        assert node is not None, "cpp_module node not found"
        content = generator.generate_rst_content(node, template)
        assert "doxygenfile" in content
        assert "test_project" in content


class TestIndexGeneration:
    """Test index.rst generation."""

    def test_generate_index(self, sample_yaml_config: Path, temp_dir: Path):
        """Test index.rst generation."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()
        generator.build_page_tree()

        index_content = generator.generate_index(generator.page_tree)

        assert "API Documentation" in index_content
        assert ".. toctree::" in index_content
        assert "Introligo" in index_content

    def test_generate_index_custom_title(self, temp_dir: Path):
        """Test index generation with custom title."""
        config_file = temp_dir / "config.yaml"
        config_content = """
index:
  title: "Custom Documentation"
  description: "Custom description"
  overview: "Overview text"

modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()
        generator.build_page_tree()

        index_content = generator.generate_index(generator.page_tree)

        assert "Custom Documentation" in index_content
        assert "Custom description" in index_content
        assert "Overview text" in index_content


class TestFileGeneration:
    """Test file generation and writing."""

    def test_generate_all_nodes(self, sample_yaml_config: Path, temp_dir: Path):
        """Test generating all nodes."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        generated = generator.generate_all_nodes(generator.page_tree, template)

        assert len(generated) > 0
        for content, path in generated.values():
            assert isinstance(content, str)
            assert isinstance(path, Path)

    def test_generate_all(self, sample_yaml_config: Path, temp_dir: Path):
        """Test complete generation process."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        generated_files = generator.generate_all()

        assert len(generated_files) > 0
        # Should include index.rst
        assert any("index.rst" in str(path) for _, path in generated_files.values())

    def test_write_files(self, sample_yaml_config: Path, temp_dir: Path):
        """Test writing generated files to disk."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        generated_files = generator.generate_all()
        generator.write_files(generated_files)

        # Check that files were created
        assert output_dir.exists()
        index_file = output_dir / "index.rst"
        assert index_file.exists()

    def test_write_files_dry_run(self, sample_yaml_config: Path, temp_dir: Path):
        """Test dry-run mode doesn't write files."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir, dry_run=True)

        generated_files = generator.generate_all()
        generator.write_files(generated_files)

        # Check that files were NOT created
        index_file = output_dir / "index.rst"
        assert not index_file.exists()

    def test_generate_all_strict_mode_error(self, temp_dir: Path):
        """Test strict mode raises error on generation failure."""
        config_file = temp_dir / "config.yaml"
        # Create config that might cause issues
        config_content = """
modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir, strict=False)

        # Should not raise error in non-strict mode
        generated_files = generator.generate_all()
        assert len(generated_files) > 0


class TestDoxygenConfiguration:
    """Test Doxygen configuration generation."""

    def test_generate_breathe_config(self, doxygen_config: Path, temp_dir: Path):
        """Test generating Breathe configuration."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(doxygen_config, output_dir)
        generator.load_config()

        breathe_config = generator.generate_breathe_config()

        assert breathe_config is not None
        assert "breathe_projects" in breathe_config
        assert "test_project" in breathe_config
        assert "doxygen/xml" in breathe_config

    def test_generate_breathe_config_no_doxygen(self, sample_yaml_config: Path, temp_dir: Path):
        """Test breathe config returns None without Doxygen config."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)
        generator.load_config()

        breathe_config = generator.generate_breathe_config()
        assert breathe_config is None

    def test_generate_breathe_config_no_xml_path(self, temp_dir: Path):
        """Test breathe config returns None without xml_path."""
        config_file = temp_dir / "config.yaml"
        config_content = """
doxygen:
  project_name: "test"

modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()

        breathe_config = generator.generate_breathe_config()
        assert breathe_config is None


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_full_generation_workflow(self, sample_yaml_config: Path, temp_dir: Path):
        """Test complete generation workflow."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        # Generate all files
        generated_files = generator.generate_all()
        generator.write_files(generated_files)

        # Verify structure
        assert output_dir.exists()
        assert (output_dir / "index.rst").exists()
        assert (output_dir / "generated").exists()

    def test_no_index_generation(self, temp_dir: Path):
        """Test disabling index generation."""
        config_file = temp_dir / "config.yaml"
        config_content = """
generate_index: false

modules:
  test:
    title: "Test"
"""
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        generated_files = generator.generate_all()

        # Should not include index.rst
        assert not any("index.rst" in str(path) for _, path in generated_files.values())

    def test_include_latex_file_read_error(self, temp_dir: Path):
        """Test error handling when reading LaTeX file fails (lines 1005-1006)."""
        config_content = """
modules:
  test_module:
    title: "Test Module"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        # Create a file with invalid encoding to cause read error
        latex_file = temp_dir / "latex_file.tex"
        # Write binary data that will cause encoding error
        latex_file.write_bytes(b"\x80\x81\x82\x83")

        with pytest.raises(IntroligoError, match="Error reading LaTeX file"):
            generator.include_latex_file(str(latex_file))

    def test_auto_configure_without_sphinx_config(self, temp_dir: Path):
        """Test auto_configure_extensions when sphinx is not in config (line 1753)."""
        config_content = """
modules:
  test_module:
    title: "Test Module"
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content, encoding="utf-8")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)

        # Should return early without error when sphinx not in config
        generator.auto_configure_extensions()
        # No exception should be raised
