#!/usr/bin/env python
"""Markdown to RST conversion utilities.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import re
from typing import Optional


def convert_markdown_links_to_rst(text: str) -> str:
    """Convert markdown links to RST format.

    Handles:
    - External links: [text](http://url) -> `text <http://url>`_
    - External links with anchors: [text](http://url#anchor) -> `text <http://url#anchor>`_
    - Internal docs with anchors: [text](./file.md#anchor) -> :doc:`text <file>` (see section)
    - Internal docs: [text](./file.md) -> :doc:`file`
    - Anchor links: [text](#anchor) -> :ref:`anchor`
    - Images: ![alt](path) -> .. image:: path

    Args:
        text: Line of text potentially containing markdown links.

    Returns:
        Text with links converted to RST format.
    """
    # Handle images first: ![alt](path)
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: f"\n\n.. image:: {m.group(2)}\n   :alt: {m.group(1)}\n\n",
        text,
    )

    # Handle external links with anchors: [text](http://...#anchor or https://...#anchor)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)", lambda m: f"`{m.group(1)} <{m.group(2)}>`_", text
    )

    # Handle internal document links with anchors: [text](./file.md#anchor)
    # Convert to :doc: reference with note about the section
    def convert_doc_link_with_anchor(match):
        link_text = match.group(1)
        file_path = match.group(2)
        anchor = match.group(3)

        # Remove .md/.rst extension and leading ./
        doc_path = file_path.replace(".md", "").replace(".rst", "")
        if doc_path.startswith("./"):
            doc_path = doc_path[2:]
        elif doc_path.startswith("../"):
            # Keep relative paths as-is
            pass

        # Create a more informative link text that includes the section
        # This helps users know which section they're linking to
        section_name = anchor.replace("-", " ").replace("_", " ").title()

        # If link text already mentions the section, use it as-is
        if link_text != section_name and section_name.lower() not in link_text.lower():
            combined_text = f"{link_text} ({section_name})"
        else:
            combined_text = link_text

        return f":doc:`{combined_text} <{doc_path}>`"

    text = re.sub(
        r"\[([^\]]+)\]\(([^)#:]+\.(?:md|rst))#([^)]+)\)", convert_doc_link_with_anchor, text
    )

    # Handle anchor-only links: [text](#anchor)
    text = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", lambda m: f":ref:`{m.group(2)}`", text)

    # Handle internal document links without anchors:
    # [text](./file.md) or [text](path/to/file.md)
    # Convert to :doc: reference without .md extension
    def convert_doc_link(match):
        link_text = match.group(1)
        file_path = match.group(2)

        # Remove .md extension and leading ./
        doc_path = file_path.replace(".md", "").replace(".rst", "")
        if doc_path.startswith("./"):
            doc_path = doc_path[2:]
        elif doc_path.startswith("../"):
            # Keep relative paths as-is for now
            pass

        # For simple cases, use the link as-is
        # Sphinx will handle the resolution
        if link_text != doc_path:
            return f":doc:`{link_text} <{doc_path}>`"
        else:
            return f":doc:`{doc_path}`"

    text = re.sub(r"\[([^\]]+)\]\(([^)#:]+\.(?:md|rst))\)", convert_doc_link, text)

    # Handle remaining local file links (without extension)
    # These might be relative paths like [text](./path/to/doc)
    text = re.sub(
        r"\[([^\]]+)\]\((\./[^)#:]+|\.\.\/[^)#:]+)\)",
        lambda m: f":doc:`{m.group(1)} <{m.group(2).replace('./', '').replace('../', '')}>`",
        text,
    )

    return text


def convert_markdown_table_to_rst(lines: list, start_index: int) -> tuple:
    """Convert markdown table to RST list-table directive.

    Args:
        lines: List of all lines in the document
        start_index: Index where the table starts

    Returns:
        Tuple of (rst_lines, end_index) where rst_lines is the converted table
        and end_index is the index after the table ends
    """
    table_lines = []
    i = start_index

    # Collect all table lines
    while i < len(lines) and "|" in lines[i]:
        table_lines.append(lines[i])
        i += 1

    if len(table_lines) < 2:
        return ([], start_index)

    # Parse table
    rows = []
    for line in table_lines:
        # Split by | and clean up
        cells = [cell.strip() for cell in line.split("|")]
        # Remove empty first/last cells from leading/trailing |
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if cells:
            rows.append(cells)

    if len(rows) < 2:
        return ([], start_index)

    # First row is header, second is separator, rest is data
    headers = rows[0]
    data_rows = rows[2:] if len(rows) > 2 else []

    # Build RST list-table
    rst_lines = ["", ".. list-table::", "   :header-rows: 1", "   :widths: auto", ""]

    # Add header row
    rst_lines.append("   * - " + headers[0])
    for header in headers[1:]:
        rst_lines.append("     - " + header)

    # Add data rows
    for row in data_rows:
        if row:  # Skip empty rows
            rst_lines.append("   * - " + row[0])
            for cell in row[1:]:
                rst_lines.append("     - " + cell)

    rst_lines.append("")

    return (rst_lines, i)


def convert_checkbox_list_to_html(lines: list, start_index: int) -> tuple:
    """Convert markdown checkbox list to HTML raw directive with checkboxes.

    Converts markdown task lists like:
    - [ ] Unchecked item
    - [x] Checked item

    To RST raw HTML directive with actual checkbox inputs.

    Args:
        lines: List of all lines in the document
        start_index: Index where the checkbox list starts

    Returns:
        Tuple of (rst_lines, end_index) where rst_lines is the converted list
        and end_index is the index after the list ends
    """
    checkbox_lines = []
    i = start_index

    # Collect all consecutive checkbox list items
    while i < len(lines):
        line = lines[i].strip()
        # Match checkbox list items: - [ ] or - [x] or - [X]
        if re.match(r"^-\s+\[[xX ]\]\s+", line):
            checkbox_lines.append(lines[i])
            i += 1
        else:
            # Stop when we hit a non-checkbox line
            break

    if not checkbox_lines:
        return ([], start_index)

    # Build RST raw HTML directive
    rst_lines = ["", ".. raw:: html", ""]
    rst_lines.append('   <ul style="list-style-type: none;">')

    for line in checkbox_lines:
        # Extract checkbox state and text
        match = re.match(r"^-\s+\[([xX ])\]\s+(.+)$", line.strip())
        if match:
            state = match.group(1)
            text = match.group(2)

            # Escape backticks in text by converting them to <code> tags
            text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

            # Create checkbox HTML
            if state.lower() == "x":
                checkbox_html = '<input type="checkbox" checked>'
            else:
                checkbox_html = '<input type="checkbox">'

            rst_lines.append(f"   <li>{checkbox_html} {text}</li>")

    rst_lines.append("   </ul>")
    rst_lines.append("")

    return (rst_lines, i)


def convert_markdown_to_rst(
    markdown: str, doc_type: Optional[str] = None, demote_headers: bool = True
) -> str:
    """Convert basic markdown syntax to reStructuredText.

    Args:
        markdown: Markdown content to convert.
        doc_type: Type of document (readme, changelog, license) for special handling.
        demote_headers: If True, demote all headers by one level (# -> ##, ## -> ###, etc.)
                       to avoid duplicate H1 headers when including files. Default is True.

    Returns:
        RST-compatible content.
    """
    lines = markdown.split("\n")
    result = []
    in_code_block = False
    code_language = ""
    first_h1_found = False

    # Special handling for changelogs
    skip_first_h1 = doc_type == "changelog"

    i = 0
    while i < len(lines):
        line = lines[i]

        # Handle code blocks
        if line.strip().startswith("```"):
            if not in_code_block:
                # Start of code block
                in_code_block = True
                code_language = line.strip()[3:].strip() or "text"
                result.append("")
                result.append(f".. code-block:: {code_language}")
                result.append("")
            else:
                # End of code block
                in_code_block = False
                result.append("")
            i += 1
            continue

        if in_code_block:
            # Inside code block - indent by 3 spaces
            result.append("   " + line)
            i += 1
            continue

        # Handle tables (before link conversion to preserve table structure)
        if (
            "|" in line
            and not in_code_block
            and i + 1 < len(lines)
            and "|" in lines[i + 1]
            and ("-" in lines[i + 1] or "=" in lines[i + 1])
        ):
            # This is a table!
            rst_table, new_index = convert_markdown_table_to_rst(lines, i)
            if rst_table:
                result.extend(rst_table)
                i = new_index
                continue

        # Handle checkbox lists (before link conversion)
        if re.match(r"^-\s+\[[xX ]\]\s+", line.strip()) and not in_code_block:
            # This is a checkbox list!
            rst_checkbox, new_index = convert_checkbox_list_to_html(lines, i)
            if rst_checkbox:
                result.extend(rst_checkbox)
                i = new_index
                continue

        # Convert markdown links to RST (before processing headers)
        line = convert_markdown_links_to_rst(line)

        # Handle headers
        # When demote_headers is True:
        # H1 (#) -> H2 (----)
        # H2 (##) -> H3 (~~~~)
        # H3 (###) -> H4 (^^^^)
        # H4 (####) -> H5 ("""""")
        # H5 (#####) -> H6 (,,,,,,)

        if line.startswith("##### "):
            # H5 -> H6 (when demoted)
            title = line[6:].strip()
            result.append("")
            result.append(title)
            if demote_headers:
                result.append("," * len(title))
            else:
                result.append(":" * len(title))
            result.append("")
        elif line.startswith("#### "):
            # H4 -> H5 (when demoted)
            title = line[5:].strip()
            result.append("")
            result.append(title)
            if demote_headers:
                result.append('"' * len(title))
            else:
                result.append("^" * len(title))
            result.append("")
        elif line.startswith("### "):
            # H3 -> H4 (when demoted)
            title = line[4:].strip()
            result.append("")
            result.append(title)
            if demote_headers:
                result.append("^" * len(title))
            else:
                result.append("~" * len(title))
            result.append("")
        elif line.startswith("## "):
            # H2 -> H3 (when demoted)
            title = line[3:].strip()
            result.append("")
            result.append(title)
            if demote_headers:
                result.append("~" * len(title))
            else:
                result.append("-" * len(title))
            result.append("")
        elif line.startswith("# "):
            # H1 -> H2 (when demoted)
            title = line[2:].strip()
            # Skip first H1 for changelogs or if title matches doc type
            if skip_first_h1 and not first_h1_found:
                first_h1_found = True
                i += 1
                continue
            first_h1_found = True
            result.append("")
            result.append(title)
            if demote_headers:
                result.append("-" * len(title))
            else:
                result.append("=" * len(title))
            result.append("")
        else:
            # Regular line
            result.append(line)

        i += 1

    # Special formatting for license files
    if doc_type == "license":
        # Wrap in a literal block to preserve exact formatting
        result = [".. code-block:: text", ""] + ["   " + line for line in result]

    return "\n".join(result)
