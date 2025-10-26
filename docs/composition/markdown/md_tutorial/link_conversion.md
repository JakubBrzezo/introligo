For additional examples, refer to the [Link Examples →](./link_examples.md) page. Also consult [Best Practices →](./best_practices.md#markdown-format) for recommendations.

## Supported Link Types

### External Links

External URLs are converted to RST inline links:

**Markdown:**
```markdown
Check the [Python documentation](https://docs.python.org/3/) for details.
Visit our [GitHub repository](https://github.com/example/project).
```

**Converted to RST:**
```rst
Check the `Python documentation <https://docs.python.org/3/>`_ for details.
Visit our `GitHub repository <https://github.com/example/project>`_.
```

### Internal Document Links

Links to other markdown files are converted to Sphinx `:doc:` references:

**Markdown:**
```markdown
See the [installation guide](./install.md) for setup instructions.
Check out the [configuration docs](./config.md).
```

**Converted to RST:**
```rst
See the :doc:`installation guide <install>` for setup instructions.
Check out the :doc:`configuration docs <config>`.
```

### Links with Section Anchors

Links with section anchors automatically append the section name to the link text:

**Markdown:**
```markdown
Follow the [setup instructions](./install.md#prerequisites).
See [configuration options](./config.md#advanced-settings).
```

**Converted to RST:**
```rst
Follow the :doc:`setup instructions (Prerequisites) <install>`.
See :doc:`configuration options (Advanced Settings) <config>`.
```

**Conversion behavior:**
- Anchor `#prerequisites` becomes `(Prerequisites)`
- Anchor `#advanced-settings` becomes `(Advanced Settings)`
- The section name is automatically appended to improve link clarity

### Same-Page Anchors

Anchor links within the same page:

**Markdown:**
```markdown
Jump to the [installation](#installation) section.
See [configuration](#configuration) below.
```

**Converted to RST:**
```rst
Jump to the :ref:`installation` section.
See :ref:`configuration` below.
```

### Images

Images are converted to RST image directives:

**Markdown:**
```markdown
![System Architecture](./diagrams/architecture.png)
![Project Logo](./images/logo.svg)
```

**Converted to RST:**
```rst
.. image:: ./diagrams/architecture.png
   :alt: System Architecture

.. image:: ./images/logo.svg
   :alt: Project Logo
```

### Tables

Markdown tables are automatically converted to RST list-table directives:

**Markdown:**
```markdown
| Feature | Supported | Notes |
|---------|-----------|-------|
| Links | Yes | All types |
| Images | Yes | With alt text |
| Tables | Yes | List-table format |
```

**Converted to RST:**
```rst
.. list-table::
   :header-rows: 1
   :widths: auto

   * - Feature
     - Supported
     - Notes
   * - Links
     - Yes
     - All types
   * - Images
     - Yes
     - With alt text
   * - Tables
     - Yes
     - List-table format
```

**Example:** Refer to the [conversion table](#conversion-summary-table) below for additional examples.

### Checklists (Task Lists)

Markdown checklists are automatically converted to interactive HTML checkboxes:

**Markdown syntax:**
```markdown
- [ ] Unchecked task item
- [x] Completed task item
- [ ] Another pending task
```

**Converted to RST:**
```rst
.. raw:: html

   <ul style="list-style-type: none;">
   <li><input type="checkbox"> Unchecked task item</li>
   <li><input type="checkbox" checked> Completed task item</li>
   <li><input type="checkbox"> Another pending task</li>
   </ul>
```

**Rendered output:**

This produces actual interactive checkboxes in the HTML output:

- [ ] Unchecked task example
- [x] Completed task example

## Quick Example with Real Links

### Input Markdown File

```markdown
# User Guide

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Python Docs](https://docs.python.org/3/)
- [Introligo on GitHub](https://github.com/jakubbrzezo/introligo)

## Getting Started

Follow these steps:
1. Read [Basic Usage](./basic_usage.md) first
2. Review [Best Practices](./best_practices.md#markdown-format)
3. Check [Use Cases](./use_cases.md) for examples
4. See [Troubleshooting](./troubleshooting.md#common-issues) if needed

Jump to [Conversion Table](#conversion-summary-table) for reference.

## Link Types Comparison

| Type | Example | Works |
|------|---------|-------|
| External | [Sphinx](https://www.sphinx-doc.org/) | Yes |
| Internal | [Use Cases](./use_cases.md) | Yes |
| Anchor | [Troubleshooting](./troubleshooting.md#common) | Yes |

See the [Related Documentation](#related-documentation) section below.
```

### Generated RST

```rst
User Guide
==========


Resources
---------

- `Sphinx Documentation <https://www.sphinx-doc.org/>`_
- `Python Docs <https://docs.python.org/3/>`_
- `Introligo on GitHub <https://github.com/jakubbrzezo/introligo>`_


Getting Started
---------------

Follow these steps:
1. Read :doc:`Basic Usage <basic_usage>` first
2. Review :doc:`Best Practices (Markdown Format) <best_practices>`
3. Check :doc:`Use Cases <use_cases>` for examples
4. See :doc:`Troubleshooting (Common Issues) <troubleshooting>` if needed

Jump to :ref:`conversion-summary-table` for reference.


Link Types Comparison
---------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Type
     - Example
     - Works
   * - External
     - `Sphinx <https://www.sphinx-doc.org/>`_
     - Yes
   * - Internal
     - :doc:`Use Cases <use_cases>`
     - Yes
   * - Anchor
     - :doc:`Troubleshooting (Common) <troubleshooting>`
     - Yes

See the :ref:`related-documentation` section below.
```

**Note:** All links are automatically converted, including those within tables.

## Key Features

- **Automatic conversion**: No manual RST writing required
- **Section detection**: Anchor names automatically appended to link text
- **All link types**: External, internal, anchors, images, tables, and checklists supported
- **Zero configuration**: Automatic operation with markdown includes
- **Clean output**: Proper RST syntax for Sphinx
- **Live demonstration**: This page utilizes functional working links

## Code Blocks Preservation

Links inside code blocks are **NOT** converted. When markdown links appear within fenced code blocks, they remain as literal text and are not converted to RST link syntax.

**Example markdown input:**

    ```python
    # This [link](https://example.com) stays unchanged
    url = "https://example.com"
    ```

**RST output:**

The code block and its contents, including the markdown link syntax, are preserved exactly as written without any conversion to RST link format.

## Best Practices

### Use Section Anchors for Cross-Document Links

**Recommended:**
```markdown
See the [installation guide](./install.md#prerequisites).
```

**Rationale:** The section name appears in the link text, providing clear context about the link destination.

### Write Descriptive Link Text

**Recommended:**
```markdown
Follow the [Docker installation instructions](https://docs.docker.com/get-docker/).
```

**Not recommended:**
```markdown
Click [here](https://docs.docker.com/get-docker/) to install Docker.
```

### Add Alt Text to Images

```markdown
![System architecture showing three main components](./architecture.png)
```

Alt text improves accessibility and SEO.

## Common Patterns

### Documentation Navigation Menu

```markdown
## Documentation

### Guides
- [Getting Started](./getting_started.md)
- [Installation](./install.md#quick-install)
- [Configuration](./config.md#basic-setup)

### Reference
- [API Documentation](./api.md)
- [CLI Reference](./cli.md)

### External Resources
- [Project Website](https://example.com/)
- [Community Forum](https://forum.example.com/)
```

### Cross-Reference Pattern

```markdown
## Installation

Before installing, ensure you meet the [system requirements](./requirements.md#minimum-specs).

Follow the [quick start guide](./quickstart.md#installation-steps) to install.

After installation, proceed to [configuration](./config.md#basic-setup).
```

### Image Gallery

```markdown
## Screenshots

![Main Interface](./screenshots/main.png)

The main interface provides access to all features.

![Settings Panel](./screenshots/settings.png)

Configure application settings here.
```

## Limitations

### Internal Links Without Anchors

Internal markdown file links may generate Sphinx warnings if the filename does not match the generated RST filename.

**Example:**
- Markdown: `setup.md`
- Generated: `1_setup_guide.rst` (due to title slugification)

**Workaround:**
Always include section anchors in cross-document links:
```markdown
[Setup Guide](./setup.md#installation)
```

This approach improves link informativeness and ensures reliable functionality.

## Conversion Summary Table

This table demonstrates all conversion types (using a markdown table that itself gets converted):

| Link Type | Markdown Example | Converted RST | Status |
|-----------|------------------|---------------|--------|
| External | `[Python Docs](https://docs.python.org/)` | `` `Python Docs <...>`_ `` | Full support |
| External + anchor | `[Install](https://docs.docker.com#install)` | `` `Install <...#install>`_ `` | Full support |
| Document | `[Use Cases](./use_cases.md)` | `:doc:`Use Cases <use_cases>`` | Limited |
| Document + anchor | `[Troubleshooting](./troubleshooting.md#common)` | `:doc:`...(Common) <troubleshooting>`` | Full support |
| Same-page | `[Summary](#summary)` | `:ref:`summary`` | Full support |
| Image | `![Logo](./logo.png)` | `.. image:: ./logo.png` | Full support |
| Table | Markdown table | `.. list-table::` | Full support |
| Checklist | `- [ ] Task` | `- [ ] Task` (as text) | Full support |

**Recommendation:** Use links with section anchors for optimal results.

## Related Documentation

- [Basic Usage →](./basic_usage.md) - Learn markdown inclusion basics
- [Best Practices →](./best_practices.md#markdown-format) - Tips for using markdown
- [Use Cases →](./use_cases.md) - When to use markdown includes
- [Troubleshooting →](./troubleshooting.md) - Common issues and solutions

External resources:
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Markdown Guide](https://www.markdownguide.org/)
