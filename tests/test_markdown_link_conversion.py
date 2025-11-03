"""Tests for markdown link conversion to RST format."""

from introligo.markdown_converter import (
    convert_checkbox_list_to_html,
    convert_markdown_links_to_rst,
    convert_markdown_table_to_rst,
    convert_markdown_to_rst,
)


class TestMarkdownLinkConversion:
    """Test markdown link conversion to reStructuredText."""

    def test_external_link_conversion(self):
        """Test external HTTP/HTTPS links are converted correctly."""
        # Test external link conversion
        markdown = "[Documentation](https://example.com/docs)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == "`Documentation <https://example.com/docs>`_"

        # Test HTTPS link
        markdown = "[Secure Site](https://secure.example.com)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == "`Secure Site <https://secure.example.com>`_"

    def test_internal_document_link_conversion(self):
        """Test internal .md links are converted to :doc: references."""
        # Test .md file link
        markdown = "[Setup Guide](./setup.md)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == ":doc:`Setup Guide <setup>`"

        # Test relative path with .md (preserves directory structure)
        markdown = "[Config](../config/settings.md)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == ":doc:`Config <../config/settings>`"

    def test_anchor_link_conversion(self):
        """Test anchor links are converted to :ref: references."""
        # Test anchor link
        markdown = "[Jump to section](#installation)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == ":ref:`installation`"

    def test_image_conversion(self):
        """Test image markdown is converted to RST image directive."""
        # Test image conversion
        markdown = "![Logo](./assets/logo.png)"
        result = convert_markdown_links_to_rst(markdown)
        assert ".. image:: ./assets/logo.png" in result
        assert ":alt: Logo" in result

    def test_mixed_links_in_line(self):
        """Test multiple different link types in one line."""
        # Test multiple links
        markdown = "See [docs](https://example.com) and [Setup Guide](./setup.md)"
        result = convert_markdown_links_to_rst(markdown)
        assert "`docs <https://example.com>`_" in result
        assert ":doc:`Setup Guide <setup>`" in result

    def test_full_markdown_to_rst_conversion(self):
        """Test complete markdown conversion including links."""
        markdown = """## Getting Started

For more information, see [Documentation](https://example.com/docs) and [Setup Guide](./setup.md).

- [External link](https://github.com/example)
- [Internal doc](./guide.md)
- [Anchor](#section)
"""

        result = convert_markdown_to_rst(markdown)

        # Check header conversion (demoted by default: ## -> H3)
        assert "Getting Started" in result
        assert "~~~~~~~~~~~~~~~" in result  # H3 underline (demoted from ##)

        # Check link conversions
        assert "`Documentation <https://example.com/docs>`_" in result
        assert ":doc:`Setup Guide <setup>`" in result
        assert "`External link <https://github.com/example>`_" in result
        assert ":doc:`Internal doc <guide>`" in result
        assert ":ref:`section`" in result

    def test_rst_file_link_conversion(self):
        """Test .rst file links are also converted."""
        # Test .rst file link
        markdown = "[API Reference](./api.rst)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == ":doc:`API Reference <api>`"

    def test_internal_link_with_anchor(self):
        """Test internal document links with anchors are converted correctly."""
        # Test .md file link with anchor
        markdown = "[Running Code in Devcontainer](./devcontainer_usage.md#prerequisites)"
        result = convert_markdown_links_to_rst(markdown)
        # Should convert to doc link with section info in the text
        assert ":doc:`" in result
        assert "devcontainer_usage" in result
        assert "Prerequisites" in result or "prerequisites" in result.lower()

        # Test with different anchor format
        markdown = "[Setup Guide](./setup.md#installation-steps)"
        result = convert_markdown_links_to_rst(markdown)
        assert ":doc:`" in result
        assert "setup" in result
        # Should include the section name in some form
        assert "Installation" in result or "Steps" in result

    def test_external_link_with_anchor(self):
        """Test external links with anchors are preserved correctly."""
        # External link with anchor should preserve the anchor
        markdown = "[Docker Installation](https://docs.docker.com/get-docker#linux)"
        result = convert_markdown_links_to_rst(markdown)
        assert result == "`Docker Installation <https://docs.docker.com/get-docker#linux>`_"

    def test_preserves_code_blocks(self):
        """Test that links inside code blocks are NOT converted."""
        markdown = """```python
# This [link](https://example.com) should not be converted
print("hello")
```"""

        result = convert_markdown_to_rst(markdown)

        # Link should remain unchanged inside code block
        assert "[link](https://example.com)" in result
        assert ".. code-block:: python" in result

    def test_table_conversion(self):
        """Test markdown table to RST list-table conversion."""
        markdown = """## Features

| Feature | Status | Notes |
|---------|--------|-------|
| Links | ✅ Yes | All types |
| Images | ✅ Yes | With alt |
| Tables | ✅ Yes | List-table |

End of table."""

        result = convert_markdown_to_rst(markdown)

        # Check for list-table directive
        assert ".. list-table::" in result
        assert ":header-rows: 1" in result
        assert ":widths: auto" in result

        # Check for table content
        assert "Feature" in result
        assert "Status" in result
        assert "Links" in result
        assert "✅ Yes" in result
        assert "List-table" in result

        # Check structure
        assert "* -" in result  # List-table row marker

    def test_link_with_parent_directory_path(self):
        """Test links with ../ parent directory paths are handled correctly."""
        # Test ../ path with anchor (lines 1093-1095)
        # The elif branch is only in the anchor handling function
        markdown = "[Parent Doc](../parent/document.md#section)"
        result = convert_markdown_links_to_rst(markdown)
        assert ":doc:`" in result
        assert "../parent/document" in result

    def test_link_text_contains_section_name(self):
        """Test when link text already contains the section name (line 1105)."""
        # Link where text already mentions the section
        markdown = "[Prerequisites Section](./setup.md#prerequisites)"
        result = convert_markdown_links_to_rst(markdown)
        # Should not duplicate "Prerequisites" in the text
        assert ":doc:`Prerequisites Section <setup>`" in result
        assert result.count("Prerequisites") == 1

    def test_table_with_insufficient_lines(self):
        """Test table parsing with insufficient lines (lines 1178, 1194)."""
        # Test line 1178: Call table parser directly with only 1 line
        lines = ["|  |"]
        rst_table, end_idx = convert_markdown_table_to_rst(lines, 0)
        assert rst_table == []  # Should return empty list
        assert end_idx == 0  # Should return start index

        # Test line 1194: Table lines that produce no valid rows after filtering
        # Lines with only a single pipe have no cells after filtering
        lines = ["|", "|"]  # Two lines but produce 0 rows after filtering
        rst_table, end_idx = convert_markdown_table_to_rst(lines, 0)
        # After filtering, all cells are empty, so rows < 2
        assert rst_table == []
        assert end_idx == 0

    def test_checkbox_unchecked_conversion(self):
        """Test unchecked checkbox list items are converted to HTML."""
        lines = ["- [ ] First item", "- [ ] Second item"]
        rst_lines, end_idx = convert_checkbox_list_to_html(lines, 0)

        assert end_idx == 2
        assert ".. raw:: html" in rst_lines
        assert '   <li><input type="checkbox"> First item</li>' in rst_lines
        assert '   <li><input type="checkbox"> Second item</li>' in rst_lines
        assert '   <ul style="list-style-type: none;">' in rst_lines

    def test_checkbox_checked_conversion(self):
        """Test checked checkbox list items are converted to HTML."""
        lines = ["- [x] Completed item", "- [X] Another completed"]
        rst_lines, end_idx = convert_checkbox_list_to_html(lines, 0)

        assert end_idx == 2
        assert '   <li><input type="checkbox" checked> Completed item</li>' in rst_lines
        assert '   <li><input type="checkbox" checked> Another completed</li>' in rst_lines

    def test_checkbox_mixed_states(self):
        """Test checkbox lists with mixed checked/unchecked states."""
        lines = ["- [ ] Todo", "- [x] Done", "- [ ] Another todo"]
        rst_lines, end_idx = convert_checkbox_list_to_html(lines, 0)

        assert end_idx == 3
        assert '   <li><input type="checkbox"> Todo</li>' in rst_lines
        assert '   <li><input type="checkbox" checked> Done</li>' in rst_lines
        assert '   <li><input type="checkbox"> Another todo</li>' in rst_lines

    def test_checkbox_with_backticks(self):
        """Test checkbox items with inline code (backticks) are converted to <code> tags."""
        lines = ["- [ ] Install `package`", "- [x] Configure `settings.yaml`"]
        rst_lines, end_idx = convert_checkbox_list_to_html(lines, 0)

        assert end_idx == 2
        assert '   <li><input type="checkbox"> Install <code>package</code></li>' in rst_lines
        assert (
            '   <li><input type="checkbox" checked> Configure <code>settings.yaml</code></li>'
            in rst_lines
        )

    def test_checkbox_list_stops_at_non_checkbox(self):
        """Test checkbox list conversion stops at non-checkbox line."""
        lines = ["- [ ] First", "- [x] Second", "Regular text", "- [ ] Not included"]
        rst_lines, end_idx = convert_checkbox_list_to_html(lines, 0)

        assert end_idx == 2  # Should stop at line 2 (Regular text)
        assert '   <li><input type="checkbox"> First</li>' in rst_lines
        assert '   <li><input type="checkbox" checked> Second</li>' in rst_lines

    def test_checkbox_in_full_markdown_conversion(self):
        """Test checkbox lists are properly converted in full markdown to RST conversion."""
        markdown = """## Todo List

- [ ] Task one
- [x] Task two
- [ ] Task three with `code`
"""
        rst = convert_markdown_to_rst(markdown)

        assert ".. raw:: html" in rst
        assert '<input type="checkbox"> Task one' in rst
        assert '<input type="checkbox" checked> Task two' in rst
        assert '<input type="checkbox"> Task three with <code>code</code>' in rst

    def test_checkbox_not_converted_in_code_block(self):
        """Test checkbox syntax inside code blocks is not converted."""
        markdown = """```markdown
- [ ] This stays as markdown
- [x] This too
```

- [ ] But this is converted
"""
        rst = convert_markdown_to_rst(markdown)

        # Code block content should be indented and not converted
        assert "   - [ ] This stays as markdown" in rst
        assert "   - [x] This too" in rst

        # Outside code block should be converted
        assert ".. raw:: html" in rst
        assert '<input type="checkbox"> But this is converted' in rst

    def test_h3_header_conversion(self):
        """Test H3 header conversion with and without demotion."""
        # With demotion (default)
        markdown = "### Level 3 Header"
        rst = convert_markdown_to_rst(markdown, demote_headers=True)
        assert "Level 3 Header" in rst
        assert "^^^^^^^^^^^^^^" in rst  # H3 becomes H4 (^)

        # Without demotion
        rst_no_demote = convert_markdown_to_rst(markdown, demote_headers=False)
        assert "~~~~~~~~~~~~~~" in rst_no_demote  # H3 stays H3 (~)

    def test_h4_header_conversion(self):
        """Test H4 header conversion with and without demotion."""
        # With demotion (default)
        markdown = "#### Level 4"
        rst = convert_markdown_to_rst(markdown, demote_headers=True)
        assert "Level 4" in rst
        assert '"' * 7 in rst  # H4 becomes H5 (")

        # Without demotion
        rst_no_demote = convert_markdown_to_rst(markdown, demote_headers=False)
        assert "^" * 7 in rst_no_demote  # H4 stays H4 (^)

    def test_h5_header_conversion(self):
        """Test H5 header conversion with and without demotion."""
        # With demotion (default)
        markdown = "##### Level 5"
        rst = convert_markdown_to_rst(markdown, demote_headers=True)
        assert "Level 5" in rst
        assert "," * 7 in rst  # H5 becomes H6 (,)

        # Without demotion
        rst_no_demote = convert_markdown_to_rst(markdown, demote_headers=False)
        assert ":" * 7 in rst_no_demote  # H5 stays H5 (:)

    def test_h1_without_demotion(self):
        """Test H1 header without demotion."""
        markdown = "# Main Title"
        rst = convert_markdown_to_rst(markdown, demote_headers=False)
        assert "Main Title" in rst
        assert "==========" in rst  # H1 without demotion (=)

    def test_h2_without_demotion(self):
        """Test H2 header without demotion."""
        markdown = "## Section"
        rst = convert_markdown_to_rst(markdown, demote_headers=False)
        assert "Section" in rst
        assert "-------" in rst  # H2 without demotion (-)

    def test_changelog_skips_first_h1(self):
        """Test that changelog doc type skips first H1."""
        markdown = """# Changelog

## Version 1.0

First version."""

        rst = convert_markdown_to_rst(markdown, doc_type="changelog")
        # First H1 should be skipped
        assert rst.count("Changelog") == 0 or rst.find("Changelog") > rst.find("Version 1.0")
        assert "Version 1.0" in rst

    def test_license_doc_type_wraps_in_code_block(self):
        """Test that license doc type wraps content in code block."""
        markdown = """MIT License

Copyright (c) 2025"""

        rst = convert_markdown_to_rst(markdown, doc_type="license")
        assert ".. code-block:: text" in rst
        assert "MIT License" in rst
        assert "Copyright" in rst

    def test_empty_checkbox_list_returns_empty(self):
        """Test that empty checkbox list returns empty result."""
        lines: list[str] = []
        rst_lines, end_idx = convert_checkbox_list_to_html(lines, 0)
        assert rst_lines == []
        assert end_idx == 0

    def test_internal_link_without_doc_extension(self):
        """Test internal link without .md or .rst extension."""
        markdown = "[Link](./path/to/doc)"
        rst = convert_markdown_links_to_rst(markdown)
        # Should be converted to doc reference
        assert ":doc:" in rst or "path/to/doc" in rst

    def test_link_with_parent_directory_multiple_levels(self):
        """Test link with multiple parent directory levels."""
        markdown = "[Link](../../docs/file.md)"
        rst = convert_markdown_links_to_rst(markdown)
        assert ":doc:" in rst
        # Should preserve parent directory navigation
        assert "../.." in rst or "docs/file" in rst

    def test_doc_link_where_text_equals_path(self):
        """Test doc link conversion when link text equals the document path."""
        # This covers line 94 in markdown_converter.py
        markdown = "[setup](setup.md)"
        rst = convert_markdown_links_to_rst(markdown)
        # When text equals path, should use short form
        assert ":doc:`setup`" in rst

    def test_markdown_to_rst_with_demote_headers_true(self):
        """Test markdown conversion with demote_headers=True."""
        # This covers line 369 in markdown_converter.py
        markdown = "# Main Title\n\nContent here."
        rst = convert_markdown_to_rst(markdown, demote_headers=True)
        # With demote_headers=True, first H1 should use dashes instead of equals
        assert "Main Title" in rst
        assert "-" * len("Main Title") in rst

    def test_markdown_to_rst_with_demote_headers_false(self):
        """Test markdown conversion with demote_headers=False."""
        markdown = "# Main Title\n\nContent here."
        rst = convert_markdown_to_rst(markdown, demote_headers=False)
        # With demote_headers=False, first H1 should use equals
        assert "Main Title" in rst
        assert "=" * len("Main Title") in rst
