"""Tests for utility functions (slugify and count_display_width)."""

from introligo.utils import (
    convert_graphviz_to_rst,
    convert_mermaid_to_rst,
    convert_plantuml_to_rst,
    convert_svg_to_rst,
    count_display_width,
    process_rst_directives,
    slugify,
)


class TestSlugify:
    """Test cases for the slugify function."""

    def test_slugify_basic(self):
        """Test basic slugification."""
        assert slugify("Hello World") == "hello_world"

    def test_slugify_special_characters(self):
        """Test slugify with special characters."""
        assert slugify("Hello@World#2024!") == "helloworld2024"

    def test_slugify_unicode(self):
        """Test slugify with unicode characters."""
        assert slugify("Café") == "cafe"
        assert slugify("naïve") == "naive"

    def test_slugify_multiple_spaces(self):
        """Test slugify with multiple spaces."""
        assert slugify("Hello   World") == "hello_world"

    def test_slugify_leading_trailing_spaces(self):
        """Test slugify with leading/trailing spaces."""
        assert slugify("  Hello World  ") == "hello_world"

    def test_slugify_hyphens(self):
        """Test slugify with hyphens."""
        assert slugify("Hello-World-Test") == "hello_world_test"

    def test_slugify_underscores(self):
        """Test slugify preserves underscores."""
        assert slugify("Hello_World") == "hello_world"

    def test_slugify_mixed(self):
        """Test slugify with mixed characters."""
        assert slugify("My-Module 2.0 (beta)") == "my_module_20_beta"

    def test_slugify_empty(self):
        """Test slugify with empty string."""
        assert slugify("") == "unnamed"

    def test_slugify_only_special_chars(self):
        """Test slugify with only special characters."""
        assert slugify("@#$%^&*()") == "unnamed"

    def test_slugify_numbers(self):
        """Test slugify with numbers."""
        assert slugify("Module123") == "module123"

    def test_slugify_consecutive_underscores(self):
        """Test slugify removes consecutive underscores."""
        assert slugify("Hello___World") == "hello_world"


class TestCountDisplayWidth:
    """Test cases for the count_display_width function."""

    def test_count_display_width_basic(self):
        """Test basic display width counting."""
        assert count_display_width("Hello") == 5

    def test_count_display_width_with_emoji(self):
        """Test display width with emojis."""
        # Emoji should add extra width
        text = "Hello 🎉"
        width = count_display_width(text)
        assert width > len(text)

    def test_count_display_width_multiple_emojis(self):
        """Test display width with multiple emojis."""
        text = "🚀 Rocket 🎉 Party"
        width = count_display_width(text)
        # Two emojis should add 2 to the length
        assert width == len(text) + 2

    def test_count_display_width_no_emoji(self):
        """Test display width without emojis."""
        text = "Regular Text 123"
        assert count_display_width(text) == len(text)

    def test_count_display_width_empty(self):
        """Test display width with empty string."""
        assert count_display_width("") == 0

    def test_count_display_width_special_emoji(self):
        """Test display width with various emoji types."""
        # Sparkles
        assert count_display_width("✨") == 2
        # Check mark
        assert count_display_width("✅") == 2
        # Star
        assert count_display_width("⭐") == 2

    def test_count_display_width_mixed_content(self):
        """Test display width with mixed content."""
        text = "API Documentation ✅"
        width = count_display_width(text)
        assert width > len(text)


class TestConvertPlantUMLToRST:
    """Test cases for convert_plantuml_to_rst function."""

    def test_convert_plantuml_basic(self):
        """Test basic PlantUML conversion with directive."""
        content = "@startuml\nAlice -> Bob: Hello\n@enduml"
        result = convert_plantuml_to_rst(content)
        assert ".. uml::" in result
        assert "   @startuml" in result
        assert "   Alice -> Bob: Hello" in result
        assert "   @enduml" in result

    def test_convert_plantuml_with_title(self):
        """Test PlantUML conversion with title."""
        content = "@startuml\nAlice -> Bob: Hello\n@enduml"
        result = convert_plantuml_to_rst(content, title="Sequence Diagram")
        assert "Sequence Diagram" in result
        assert "~" * len("Sequence Diagram") in result
        assert ".. uml::" in result

    def test_convert_plantuml_without_directive(self):
        """Test PlantUML conversion with code block fallback."""
        content = "@startuml\nAlice -> Bob: Hello\n@enduml"
        result = convert_plantuml_to_rst(content, use_directive=False)
        assert ".. code-block:: plantuml" in result
        assert ".. uml::" not in result
        assert "   @startuml" in result

    def test_convert_plantuml_empty_content(self):
        """Test PlantUML conversion with empty content."""
        result = convert_plantuml_to_rst("")
        assert ".. uml::" in result

    def test_convert_plantuml_multiline(self):
        """Test PlantUML conversion with multiple lines."""
        content = "participant Alice\nparticipant Bob\nAlice -> Bob: Test"
        result = convert_plantuml_to_rst(content)
        assert "   participant Alice" in result
        assert "   participant Bob" in result
        assert "   Alice -> Bob: Test" in result


class TestConvertMermaidToRST:
    """Test cases for convert_mermaid_to_rst function."""

    def test_convert_mermaid_basic(self):
        """Test basic Mermaid conversion with directive."""
        content = "graph TD\nA-->B"
        result = convert_mermaid_to_rst(content)
        assert ".. mermaid::" in result
        assert "   graph TD" in result
        assert "   A-->B" in result

    def test_convert_mermaid_with_title(self):
        """Test Mermaid conversion with title."""
        content = "graph TD\nA-->B"
        result = convert_mermaid_to_rst(content, title="Flow Chart")
        assert "Flow Chart" in result
        assert "~" * len("Flow Chart") in result
        assert ".. mermaid::" in result

    def test_convert_mermaid_without_directive(self):
        """Test Mermaid conversion with code block fallback."""
        content = "graph TD\nA-->B"
        result = convert_mermaid_to_rst(content, use_directive=False)
        assert ".. code-block:: mermaid" in result
        assert ".. mermaid::" not in result
        assert "   graph TD" in result

    def test_convert_mermaid_empty_content(self):
        """Test Mermaid conversion with empty content."""
        result = convert_mermaid_to_rst("")
        assert ".. mermaid::" in result

    def test_convert_mermaid_complex_diagram(self):
        """Test Mermaid conversion with complex diagram."""
        content = "sequenceDiagram\nAlice->>John: Hello John\nJohn-->>Alice: Great!"
        result = convert_mermaid_to_rst(content)
        assert "   sequenceDiagram" in result
        assert "   Alice->>John: Hello John" in result


class TestConvertGraphvizToRST:
    """Test cases for convert_graphviz_to_rst function."""

    def test_convert_graphviz_basic(self):
        """Test basic Graphviz conversion."""
        content = "digraph G {\n  A -> B;\n}"
        result = convert_graphviz_to_rst(content)
        assert ".. graphviz::" in result
        assert "   digraph G {" in result
        assert "     A -> B;" in result

    def test_convert_graphviz_with_title(self):
        """Test Graphviz conversion with title."""
        content = "digraph G {\n  A -> B;\n}"
        result = convert_graphviz_to_rst(content, title="Graph")
        assert "Graph" in result
        assert "~" * len("Graph") in result
        assert ".. graphviz::" in result

    def test_convert_graphviz_empty_content(self):
        """Test Graphviz conversion with empty content."""
        result = convert_graphviz_to_rst("")
        assert ".. graphviz::" in result

    def test_convert_graphviz_multiline(self):
        """Test Graphviz conversion with multiple lines."""
        content = "graph G {\n  node [shape=box];\n  A -- B;\n  B -- C;\n}"
        result = convert_graphviz_to_rst(content)
        assert "   graph G {" in result
        assert "     node [shape=box];" in result
        assert "     A -- B;" in result


class TestConvertSVGToRST:
    """Test cases for convert_svg_to_rst function."""

    def test_convert_svg_basic(self):
        """Test basic SVG conversion."""
        result = convert_svg_to_rst("path/to/image.svg")
        assert ".. image:: path/to/image.svg" in result
        assert ":align: center" in result

    def test_convert_svg_with_title(self):
        """Test SVG conversion with title."""
        result = convert_svg_to_rst("path/to/image.svg", title="Architecture")
        assert "Architecture" in result
        assert "~" * len("Architecture") in result
        assert ".. image:: path/to/image.svg" in result

    def test_convert_svg_with_alt_text(self):
        """Test SVG conversion with alt text."""
        result = convert_svg_to_rst("path/to/image.svg", alt_text="System Architecture")
        assert ".. image:: path/to/image.svg" in result
        assert ":alt: System Architecture" in result
        assert ":align: center" in result

    def test_convert_svg_with_title_and_alt(self):
        """Test SVG conversion with both title and alt text."""
        result = convert_svg_to_rst("diagram.svg", title="System", alt_text="System diagram")
        assert "System" in result
        assert ".. image:: diagram.svg" in result
        assert ":alt: System diagram" in result


class TestProcessRSTDirectives:
    """Test cases for process_rst_directives function."""

    def test_process_rst_directives_no_changes_when_all_available(self):
        """Test that content is unchanged when all extensions are available."""
        content = ".. uml::\n   content\n.. mermaid::\n   content"
        result = process_rst_directives(content, has_plantuml=True, has_mermaid=True)
        assert result == content

    def test_process_rst_directives_convert_uml_to_code_block(self):
        """Test converting uml directive to code block."""
        content = ".. uml::\n   @startuml\n   A -> B\n   @enduml"
        result = process_rst_directives(content, has_plantuml=False, has_mermaid=True)
        assert ".. code-block:: plantuml" in result
        assert ".. uml::" not in result
        assert "   @startuml" in result

    def test_process_rst_directives_convert_mermaid_to_code_block(self):
        """Test converting mermaid directive to code block."""
        content = ".. mermaid::\n   graph TD\n   A-->B"
        result = process_rst_directives(content, has_plantuml=True, has_mermaid=False)
        assert ".. code-block:: mermaid" in result
        assert ".. mermaid::" not in result
        assert "   graph TD" in result

    def test_process_rst_directives_convert_both(self):
        """Test converting both uml and mermaid directives."""
        content = ".. uml::\n   content\n.. mermaid::\n   content"
        result = process_rst_directives(content, has_plantuml=False, has_mermaid=False)
        assert ".. code-block:: plantuml" in result
        assert ".. code-block:: mermaid" in result
        assert ".. uml::" not in result
        assert ".. mermaid::" not in result

    def test_process_rst_directives_preserve_indentation(self):
        """Test that indentation is preserved when converting directives."""
        content = "   .. uml::\n      content"
        result = process_rst_directives(content, has_plantuml=False, has_mermaid=True)
        assert "   .. code-block:: plantuml" in result

    def test_process_rst_directives_empty_content(self):
        """Test processing empty content."""
        result = process_rst_directives("", has_plantuml=False, has_mermaid=False)
        assert result == ""

    def test_process_rst_directives_no_directives(self):
        """Test processing content without any directives."""
        content = "Some regular\nRST content\nwith no directives"
        result = process_rst_directives(content, has_plantuml=False, has_mermaid=False)
        assert result == content

    def test_process_rst_directives_mixed_content(self):
        """Test processing content with directives and other content."""
        content = "Header\n======\n\n.. uml::\n   diagram\n\nSome text\n\n.. mermaid::\n   graph"
        result = process_rst_directives(content, has_plantuml=False, has_mermaid=False)
        assert "Header" in result
        assert "======" in result
        assert ".. code-block:: plantuml" in result
        assert ".. code-block:: mermaid" in result
        assert "Some text" in result
