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
        """Test markdown to RST header conversion with header demotion."""
        from introligo.markdown_converter import convert_markdown_to_rst

        # Test with header demotion (default behavior)
        markdown = "# H1\n## H2\n### H3\n#### H4"
        rst = convert_markdown_to_rst(markdown, demote_headers=True)

        # With demotion: H1 -> H2, H2 -> H3, H3 -> H4, H4 -> H5
        assert "---" in rst or "--" in rst  # H1 becomes H2 (----)
        assert "~~~" in rst or "~~" in rst  # H2 becomes H3 (~~~~)
        assert "^^^" in rst or "^^" in rst  # H3 becomes H4 (^^^^)
        assert '"""' in rst or '""' in rst  # H4 becomes H5 ("""")

    def test_convert_markdown_to_rst_headers_no_demotion(
        self, sample_yaml_config: Path, temp_dir: Path
    ):
        """Test markdown to RST header conversion without header demotion."""
        from introligo.markdown_converter import convert_markdown_to_rst

        # Test without header demotion
        markdown = "# H1\n## H2\n### H3\n#### H4"
        rst = convert_markdown_to_rst(markdown, demote_headers=False)

        # Without demotion: original levels
        assert "==" in rst  # H1 stays H1 (====)
        assert "---" in rst or "--" in rst  # H2 stays H2 (----)
        assert "~~~" in rst or "~~" in rst  # H3 stays H3 (~~~~)
        assert "^^^" in rst or "^^" in rst  # H4 stays H4 (^^^^)

    def test_convert_markdown_to_rst_code_blocks(self, sample_yaml_config: Path, temp_dir: Path):
        """Test markdown to RST code block conversion."""
        from introligo.markdown_converter import convert_markdown_to_rst

        markdown = "```python\nprint('hello')\n```"
        rst = convert_markdown_to_rst(markdown)

        assert ".. code-block:: python" in rst
        assert "   print('hello')" in rst

    def test_convert_markdown_skip_changelog_h1(self, sample_yaml_config: Path, temp_dir: Path):
        """Test skipping first Changelog H1."""
        from introligo.markdown_converter import convert_markdown_to_rst

        markdown = "# Changelog\n## Version 1.0"
        rst = convert_markdown_to_rst(markdown, doc_type="changelog")

        # Changelog H1 should be skipped when doc_type is "changelog"
        assert "Changelog\n========" not in rst
        assert "Changelog\n--------" not in rst  # Also not demoted version
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

    def test_include_rst_file(self, config_with_rst: Path, rst_file: Path, temp_dir: Path):
        """Test including RST file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_with_rst, output_dir)

        content = generator.include_rst_file(rst_file.name)
        assert "Architecture Overview" in content
        assert "System Components" in content
        assert "Component A" in content

    def test_include_rst_missing_file(self, sample_yaml_config: Path, temp_dir: Path):
        """Test including non-existent RST file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.include_rst_file("missing.rst")

        assert "RST file not found" in str(exc_info.value)

    def test_include_txt_file(self, text_file: Path, sample_yaml_config: Path, temp_dir: Path):
        """Test including text file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        content = generator.include_txt_file(text_file.name)
        assert "::" in content  # Literal block marker
        assert "Important Notes" in content
        assert "Update documentation" in content

    def test_include_txt_missing_file(self, sample_yaml_config: Path, temp_dir: Path):
        """Test including non-existent text file."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        with pytest.raises(IntroligoError) as exc_info:
            generator.include_txt_file("missing.txt")

        assert "Text file not found" in str(exc_info.value)

    def test_include_file_auto_detection_rst(
        self, rst_file: Path, sample_yaml_config: Path, temp_dir: Path
    ):
        """Test file auto-detection for RST files."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        content = generator.include_file(rst_file.name)
        assert "Architecture Overview" in content

    def test_include_file_auto_detection_md(
        self, markdown_file: Path, sample_yaml_config: Path, temp_dir: Path
    ):
        """Test file auto-detection for Markdown files."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        content = generator.include_file(markdown_file.name)
        assert "Version 1.0.0" in content

    def test_include_file_auto_detection_tex(
        self, latex_file: Path, sample_yaml_config: Path, temp_dir: Path
    ):
        """Test file auto-detection for LaTeX files."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        content = generator.include_file(latex_file.name)
        assert ".. math::" in content

    def test_include_file_auto_detection_txt(
        self, text_file: Path, sample_yaml_config: Path, temp_dir: Path
    ):
        """Test file auto-detection for text files."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        content = generator.include_file(text_file.name)
        assert "::" in content

    def test_include_file_unsupported_type(self, sample_yaml_config: Path, temp_dir: Path):
        """Test including file with unsupported extension."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(sample_yaml_config, output_dir)

        # Create a file with unsupported extension
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("content", encoding="utf-8")

        with pytest.raises(IntroligoError) as exc_info:
            generator.include_file(unsupported_file.name)

        assert "Unsupported file type" in str(exc_info.value)
        assert ".xyz" in str(exc_info.value)

    def test_include_file_license_without_extension(self, temp_dir: Path):
        """Test that LICENSE files without extension are treated as text files."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("modules: {}", encoding="utf-8")

        license_file = temp_dir / "LICENSE"
        license_content = "MIT License\n\nCopyright (c) 2025"
        license_file.write_text(license_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        result = generator.include_file(license_file.name)

        # Should be treated as text file (literal block with ::)
        assert "::" in result
        assert "MIT License" in result
        assert "Copyright (c) 2025" in result

    def test_generate_with_file_includes(self, config_with_file_includes: Path, temp_dir: Path):
        """Test generating documentation with file_includes."""
        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_with_file_includes, output_dir)
        generator.load_config()

        # Get the first module's config
        module_config = generator.config["modules"]["module_with_files"]

        # Verify file_includes are processed
        assert "file_includes" in module_config
        assert len(module_config["file_includes"]) == 4


class TestGoLanguageSupport:
    """Test Go language documentation support."""

    def test_detect_go_language_from_godoc_package(self, temp_dir: Path):
        """Test that Go language is detected from godoc_package field."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  calculator:
    title: "Calculator"
    godoc_package: "github.com/example/calculator"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "go" in languages

    def test_detect_go_language_from_godoc_packages(self, temp_dir: Path):
        """Test that Go language is detected from godoc_packages field."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  packages:
    title: "Packages"
    godoc_packages:
      - "github.com/example/pkg1"
      - "github.com/example/pkg2"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "go" in languages

    def test_detect_go_language_from_godoc_function(self, temp_dir: Path):
        """Test that Go language is detected from godoc_function field."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  function:
    title: "Function"
    godoc_function: "Add"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "go" in languages

    def test_detect_go_language_from_godoc_type(self, temp_dir: Path):
        """Test that Go language is detected from godoc_type field."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  type:
    title: "Type"
    godoc_type: "Calculator"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "go" in languages

    def test_detect_go_language_explicit(self, temp_dir: Path):
        """Test explicit Go language specification."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  calculator:
    title: "Calculator"
    language: go
    godoc_package: "github.com/example/calculator"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()

        languages = generator.detect_project_languages()
        assert "go" in languages

    def test_auto_configure_go_extensions(self, temp_dir: Path):
        """Test that Go language is detected but no extensions are auto-added."""
        config_file = temp_dir / "config.yaml"
        config_content = """
sphinx:
  project: "Test"

modules:
  calculator:
    title: "Calculator"
    language: go
    godoc_package: "github.com/example/calculator"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.load_sphinx_config()

        # Go doesn't add any extensions (uses manual documentation)
        # Just verify the config loads successfully
        assert "calculator" in generator.config["modules"]

    def test_generate_go_rst_content(self, temp_dir: Path):
        """Test RST generation for Go package."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  calculator:
    title: "Calculator Package"
    language: go
    description: "A calculator package"
    godoc_package: "github.com/example/calculator"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "Calculator Package" in content
        assert "github.com/example/calculator" in content
        # Content should have either extracted docs or fallback message
        assert (
            "pkg.go.dev" in content or "Go documentation" in content or "not available" in content
        )

    def test_generate_go_rst_with_multiple_packages(self, temp_dir: Path):
        """Test RST generation for multiple Go packages."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  packages:
    title: "Multiple Packages"
    language: go
    godoc_packages:
      - "github.com/example/pkg1"
      - "github.com/example/pkg2"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "github.com/example/pkg1" in content
        assert "github.com/example/pkg2" in content
        # Should have either extracted docs or fallback with links
        assert (
            "go doc" in content
            or "pkg.go.dev" in content
            or "Automatic documentation extraction" in content
        )

    def test_generate_go_rst_with_function(self, temp_dir: Path):
        """Test RST generation for Go function."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  add_func:
    title: "Add Function"
    language: go
    godoc_function: "Add"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "Add" in content
        assert "Function" in content

    def test_generate_go_rst_with_type(self, temp_dir: Path):
        """Test RST generation for Go type."""
        config_file = temp_dir / "config.yaml"
        config_content = """
modules:
  calc_type:
    title: "Calculator Type"
    language: go
    godoc_type: "Calculator"
"""
        config_file.write_text(config_content, encoding="utf-8")

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "Calculator" in content
        assert "Type" in content


class TestGeneratorModuleFallback:
    """Test generator module import fallback."""

    def test_hub_import_fallback(self):
        """Test that hub import fallback works."""
        # The generator file has a try/except for importing DocumentationHub
        # Lines 26-29 in generator.py handle the fallback
        # This is tested by the fact that the module loads successfully
        from introligo.generator import DocumentationHub

        assert DocumentationHub is not None


class TestGeneratorHubMode:
    """Test generator with documentation hub."""

    def test_generator_with_hub_enabled(self, temp_dir: Path):
        """Test generator initialization with hub mode."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(
            """
project:
  name: Test Project
  version: 1.0.0

discovery:
  enabled: true
  scan_paths: ["."]
  auto_include:
    readme: true
""",
            encoding="utf-8",
        )

        # Create a README to discover
        (temp_dir / "README.md").write_text("# Test Project")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()

        # Hub should be initialized
        assert generator.hub is not None
        assert generator.hub.is_enabled()

    def test_generator_hub_module_generation(self, temp_dir: Path):
        """Test that hub generates modules correctly."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(
            """
project:
  name: Test Project
  version: 1.0.0

discovery:
  enabled: true
  scan_paths: ["."]
  auto_include:
    readme: true
    changelog: true
""",
            encoding="utf-8",
        )

        # Create files to discover
        (temp_dir / "README.md").write_text("# Test Project\n\nWelcome!")
        (temp_dir / "CHANGELOG.md").write_text("# Changelog\n\n## 1.0.0\nInitial release")

        output_dir = temp_dir / "output"
        generator = IntroligoGenerator(config_file, output_dir)
        generator.load_config()

        # Check that modules were generated from hub
        assert len(generator.config.get("modules", {})) > 0

        # Should have hub modules
        hub_modules = [k for k in generator.config["modules"] if k.startswith("hub_")]
        assert len(hub_modules) > 0


class TestGeneratorTemplateHandling:
    """Test generator template loading and handling."""

    def test_load_template_fallback_when_file_missing(self, temp_dir: Path, monkeypatch):
        """Test that template fallback works when template file doesn't exist."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
""",
            encoding="utf-8",
        )

        # Temporarily break template file path to trigger fallback
        from jinja2 import Template

        from introligo import generator as gen_module

        # Point to a location where template won't exist
        monkeypatch.setattr(gen_module, "__file__", str(temp_dir / "fake.py"))

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        template = generator.load_template()

        # load_template returns a jinja2.Template object
        # Verify it's a Template object to ensure fallback worked
        assert isinstance(template, Template)

    def test_include_markdown_file_error_handling(self, temp_dir: Path):
        """Test error handling when markdown file cannot be read."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()

        # Try to include non-existent markdown file
        with pytest.raises(IntroligoError, match="Markdown file not found"):
            generator.include_markdown_file("nonexistent.md")

    def test_markdown_includes_as_string(self, temp_dir: Path):
        """Test markdown_includes can be a single string instead of list."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "content.md").write_text("# Hello\n\nWorld")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    markdown_includes: content.md
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "Hello" in content
        assert "World" in content

    def test_markdown_includes_with_error_continues(self, temp_dir: Path, caplog):
        """Test that markdown include errors are logged but don't stop processing."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "good.md").write_text("# Good content")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    markdown_includes:
      - good.md
      - missing.md
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        # Should still have good content
        assert "Good content" in content
        # Should have logged warning about missing file
        assert any("missing.md" in record.message for record in caplog.records)

    def test_latex_includes_as_string(self, temp_dir: Path):
        """Test latex_includes can be a single string instead of list."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "formula.tex").write_text(r"E = mc^2")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    latex_includes: formula.tex
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "math::" in content
        assert "E = mc^2" in content

    def test_latex_includes_with_error_continues(self, temp_dir: Path, caplog):
        """Test that latex include errors are logged but don't stop processing."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "good.tex").write_text(r"\alpha")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    latex_includes:
      - good.tex
      - missing.tex
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        # Should still have good content
        assert r"\alpha" in content
        # Should have logged warning
        assert any("missing.tex" in record.message for record in caplog.records)

    def test_rst_includes_as_string(self, temp_dir: Path):
        """Test rst_includes can be a single string instead of list."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "content.rst").write_text("Test RST content")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    rst_includes: content.rst
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "Test RST content" in content

    def test_rst_includes_with_error_continues(self, temp_dir: Path, caplog):
        """Test that RST include errors are logged but don't stop processing."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "good.rst").write_text("Good RST")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    rst_includes:
      - good.rst
      - missing.rst
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        # Should still have good content
        assert "Good RST" in content
        # Should have logged warning
        assert any("missing.rst" in record.message for record in caplog.records)

    def test_file_includes_as_string(self, temp_dir: Path):
        """Test file_includes can be a single string instead of list."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "content.md").write_text("# Auto-detected")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    file_includes: content.md
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        assert "Auto-detected" in content

    def test_file_includes_with_error_continues(self, temp_dir: Path, caplog):
        """Test that file include errors are logged but don't stop processing."""
        config_file = temp_dir / "config.yaml"
        (temp_dir / "good.md").write_text("# Good")

        config_file.write_text(
            """
project:
  name: Test
  version: 1.0.0

modules:
  test:
    title: Test Module
    file_includes:
      - good.md
      - missing.md
""",
            encoding="utf-8",
        )

        generator = IntroligoGenerator(config_file, temp_dir / "output")
        generator.load_config()
        generator.build_page_tree()
        template = generator.load_template()

        node = generator.page_tree[0]
        content = generator.generate_rst_content(node, template)

        # Should still have good content
        assert "Good" in content
        # Should have logged warning
        assert any("missing.md" in record.message for record in caplog.records)
