#!/usr/bin/env python
"""Utility functions for Introligo.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import re
import unicodedata


def slugify(text: str) -> str:
    """Convert text to ASCII-safe filesystem-compatible slug.

    Args:
        text: The text to convert to a slug.

    Returns:
        ASCII-safe slug suitable for filenames and URLs.
    """
    ascii_text = unicodedata.normalize("NFKD", text)
    ascii_text = ascii_text.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9\s\-_]", "", ascii_text.lower())
    slug = re.sub(r"[\s\-]+", "_", slug)
    slug = re.sub(r"^_+|_+$", "", slug)
    slug = re.sub(r"_+", "_", slug)
    return slug or "unnamed"


def count_display_width(text: str) -> int:
    """Calculate display width for RST underlines, accounting for emojis.

    Emojis and other wide characters need extra underline characters.
    This function estimates the visual width by counting emoji characters
    and adding extra characters to the base length.

    Args:
        text: The text to measure

    Returns:
        Estimated character width for RST underlines
    """
    # Count emojis (characters in emoji ranges)
    emoji_count = 0
    for char in text:
        code = ord(char)
        # Common emoji ranges - comprehensive coverage
        if (
            0x1F300 <= code <= 0x1F9FF  # Misc Symbols and Pictographs + Supplemental
            or 0x2600 <= code <= 0x26FF  # Misc symbols
            or 0x2700 <= code <= 0x27BF  # Dingbats
            or 0xFE00 <= code <= 0xFE0F  # Variation selectors
            or 0x1F000 <= code <= 0x1F02F  # Additional symbols
            or 0x1F600 <= code <= 0x1F64F  # Emoticons
            or 0x1F680 <= code <= 0x1F6FF  # Transport and Map
            or 0x1F900 <= code <= 0x1F9FF  # Supplemental Symbols and Pictographs
            or code == 0x2B50  # Star
            or code == 0x2705  # Check mark
            or code == 0x274C  # Cross mark
            or code == 0x2716  # Heavy multiplication X
            or code == 0x2714  # Heavy check mark
            or code == 0x2728  # Sparkles
            or code == 0x203C  # Double exclamation
            or code == 0x2049  # Exclamation question
            or code == 0x25B6  # Play button
            or code == 0x25C0  # Reverse button
            or code == 0x2139  # Information
            or 0x2194 <= code <= 0x2199  # Arrows
            or 0x21A9 <= code <= 0x21AA  # Return arrows
            or 0x231A <= code <= 0x231B  # Watch + Hourglass
            or 0x23E9 <= code <= 0x23F3  # Media buttons
            or 0x23F8 <= code <= 0x23FA
        ):  # Media buttons continued
            emoji_count += 1

    # Add extra character for each emoji (emojis display wider)
    # Use +1 per emoji for better results
    return len(text) + emoji_count


def convert_plantuml_to_rst(content: str, title: str = "", use_directive: bool = True) -> str:
    """Convert PlantUML content to reStructuredText with uml directive or code block.

    Args:
        content: PlantUML diagram content.
        title: Optional title for the diagram section.
        use_directive: If True, use uml directive. If False, use code block.

    Returns:
        RST-formatted content with PlantUML uml directive or code block.
    """
    rst = []
    if title:
        rst.append(f"{title}\n{'~' * count_display_width(title)}\n")

    if use_directive:
        rst.append(".. uml::\n")
        for line in content.split("\n"):
            rst.append(f"   {line}")
    else:
        # Fallback to code block when extension not available
        rst.append(".. code-block:: plantuml\n")
        for line in content.split("\n"):
            rst.append(f"   {line}")

    return "\n".join(rst)


def convert_mermaid_to_rst(content: str, title: str = "", use_directive: bool = True) -> str:
    """Convert Mermaid content to reStructuredText with mermaid directive or code block.

    Args:
        content: Mermaid diagram content.
        title: Optional title for the diagram section.
        use_directive: If True, use mermaid directive. If False, use code block.

    Returns:
        RST-formatted content with Mermaid directive or code block.
    """
    rst = []
    if title:
        rst.append(f"{title}\n{'~' * count_display_width(title)}\n")

    if use_directive:
        rst.append(".. mermaid::\n")
        for line in content.split("\n"):
            rst.append(f"   {line}")
    else:
        # Fallback to code block when extension not available
        rst.append(".. code-block:: mermaid\n")
        for line in content.split("\n"):
            rst.append(f"   {line}")

    return "\n".join(rst)


def convert_graphviz_to_rst(content: str, title: str = "") -> str:
    """Convert Graphviz DOT content to reStructuredText with graphviz directive.

    Args:
        content: Graphviz DOT diagram content.
        title: Optional title for the diagram section.

    Returns:
        RST-formatted content with Graphviz directive.
    """
    rst = []
    if title:
        rst.append(f"{title}\n{'~' * count_display_width(title)}\n")

    rst.append(".. graphviz::\n")
    for line in content.split("\n"):
        rst.append(f"   {line}")

    return "\n".join(rst)


def convert_svg_to_rst(svg_path: str, title: str = "", alt_text: str = "") -> str:
    """Convert SVG file reference to reStructuredText image directive.

    Args:
        svg_path: Path to the SVG file.
        title: Optional title for the diagram section.
        alt_text: Optional alt text for the image.

    Returns:
        RST-formatted content with image directive.
    """
    rst = []
    if title:
        rst.append(f"{title}\n{'~' * count_display_width(title)}\n")

    rst.append(f".. image:: {svg_path}")
    if alt_text:
        rst.append(f"   :alt: {alt_text}")
    rst.append("   :align: center")

    return "\n".join(rst)


def process_rst_directives(
    content: str, has_plantuml: bool = True, has_mermaid: bool = True
) -> str:
    """Process RST content and convert unsupported directives to code blocks.

    This function scans RST content for uml and mermaid directives and converts
    them to code blocks when the corresponding extensions are not available.

    Args:
        content: The RST content to process.
        has_plantuml: Whether sphinxcontrib-plantuml extension is available.
        has_mermaid: Whether sphinxcontrib-mermaid extension is available.

    Returns:
        Processed RST content with converted directives.
    """
    if has_plantuml and has_mermaid:
        # No need to process if all extensions are available
        return content

    lines = content.split("\n")
    processed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for uml directive
        if not has_plantuml and stripped == ".. uml::":
            # Replace with code-block directive
            indent = len(line) - len(line.lstrip())
            processed_lines.append(" " * indent + ".. code-block:: plantuml")
            i += 1
            continue

        # Check for mermaid directive
        if not has_mermaid and stripped == ".. mermaid::":
            # Replace with code-block directive
            indent = len(line) - len(line.lstrip())
            processed_lines.append(" " * indent + ".. code-block:: mermaid")
            i += 1
            continue

        processed_lines.append(line)
        i += 1

    return "\n".join(processed_lines)
