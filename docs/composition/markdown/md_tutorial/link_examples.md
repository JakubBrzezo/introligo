## Example 1: Documentation Homepage

### Input Markdown

```markdown
# MyProject Documentation

![Project Logo](../images/logo.png)

## Quick Start

Welcome! Follow these steps:

1. Review [system requirements](./requirements.md#minimum-specs)
2. Follow [installation instructions](./install.md#quick-install)
3. Complete [initial configuration](./config.md#basic-setup)
4. Read the [user guide](./guide.md)

## External Resources

- [Official Website](https://myproject.org/)
- [API Documentation](https://api.myproject.org/)
- [GitHub Repository](https://github.com/myproject/repo)
- [Community Forum](https://forum.myproject.org/)

## Need Help?

Check our [troubleshooting guide](./troubleshooting.md#common-issues) or
visit the [support page](https://myproject.org/support).
```

### Generated RST

```rst
MyProject Documentation
=======================


.. image:: ../images/logo.png
   :alt: Project Logo



Quick Start
-----------

Welcome! Follow these steps:

1. Review :doc:`system requirements (Minimum Specs) <requirements>`
2. Follow :doc:`installation instructions (Quick Install) <install>`
3. Complete :doc:`initial configuration (Basic Setup) <config>`
4. Read the :doc:`user guide <guide>`


External Resources
------------------

- `Official Website <https://myproject.org/>`_
- `API Documentation <https://api.myproject.org/>`_
- `GitHub Repository <https://github.com/myproject/repo>`_
- `Community Forum <https://forum.myproject.org/>`_


Need Help?
----------

Check our :doc:`troubleshooting guide (Common Issues) <troubleshooting>` or
visit the `support page <https://myproject.org/support>`_.
```

## Example 2: Installation Guide

### Input Markdown

```markdown
# Installation Guide

## Prerequisites

Before installing, ensure you have:

1. Python 3.8 or higher
2. Docker installed ([installation guide](https://docs.docker.com/get-docker/))
3. Git configured

See the [system requirements](./requirements.md) for complete details.

## Quick Installation

For most users, quick installation is recommended.

![Installation Flow](./diagrams/install-flow.png)

Run these commands:

```bash
pip install myproject
myproject init
```

For troubleshooting, see the [common issues](#common-issues) section below.

## Advanced Installation

For advanced configuration, refer to the [configuration guide](./config.md#advanced-options).

## Common Issues

Having problems? Check the [FAQ](./faq.md) or the [troubleshooting guide](./troubleshooting.md#installation).
```

### Generated RST

```rst
Installation Guide
==================


Prerequisites
-------------

Before installing, ensure you have:

1. Python 3.8 or higher
2. Docker installed (`installation guide <https://docs.docker.com/get-docker/>`_)
3. Git configured

See the :doc:`system requirements <requirements>` for complete details.


Quick Installation
------------------

For most users, quick installation is recommended.


.. image:: ./diagrams/install-flow.png
   :alt: Installation Flow


Run these commands:

.. code-block:: bash

   pip install myproject
   myproject init


For troubleshooting, see the :ref:`common-issues` section below.


Advanced Installation
---------------------

For advanced configuration, refer to the :doc:`configuration guide (Advanced Options) <config>`.


Common Issues
-------------

Having problems? Check the :doc:`FAQ <faq>` or the :doc:`troubleshooting guide (Installation) <troubleshooting>`.
```

## Example 3: API Documentation

### Input Markdown

```markdown
# API Reference

Complete API documentation for developers.

## Getting Started with the API

Read the [authentication guide](./auth.md#api-keys) to get your API key.

## Core APIs

### User Management
- [Create User](./api/users.md#create-user)
- [Get User](./api/users.md#get-user)
- [Update User](./api/users.md#update-user)

### Data Operations
- [Query Data](./api/data.md#query-operations)
- [Insert Data](./api/data.md#insert-operations)
- [Update Data](./api/data.md#update-operations)

## External Tools

Recommended tools for API development:

- [Postman](https://www.postman.com/) - API testing
- [Swagger UI](https://swagger.io/tools/swagger-ui/) - API visualization
- [curl](https://curl.se/) - Command-line HTTP client

## Code Examples

For Python examples, see the [Python SDK guide](./sdks/python.md#quick-start).

![API Architecture](./diagrams/api-architecture.png)
```

### Generated RST

```rst
API Reference
=============

Complete API documentation for developers.


Getting Started with the API
-----------------------------

Read the :doc:`authentication guide (Api Keys) <auth>` to get your API key.


Core APIs
---------


User Management
~~~~~~~~~~~~~~~
- :doc:`Create User (Create User) <api/users>`
- :doc:`Get User (Get User) <api/users>`
- :doc:`Update User (Update User) <api/users>`


Data Operations
~~~~~~~~~~~~~~~
- :doc:`Query Data (Query Operations) <api/data>`
- :doc:`Insert Data (Insert Operations) <api/data>`
- :doc:`Update Data (Update Operations) <api/data>`


External Tools
--------------

Recommended tools for API development:

- `Postman <https://www.postman.com/>`_ - API testing
- `Swagger UI <https://swagger.io/tools/swagger-ui/>`_ - API visualization
- `curl <https://curl.se/>`_ - Command-line HTTP client


Code Examples
-------------

For Python examples, see the :doc:`Python SDK guide (Quick Start) <sdks/python>`.


.. image:: ./diagrams/api-architecture.png
   :alt: API Architecture
```

## Example 4: Tutorial with Navigation

### Input Markdown

```markdown
# Getting Started Tutorial

Welcome! This tutorial will guide you through the basics.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [First Steps](#first-steps)
- [Next Steps](#next-steps)

## Installation

![Installation Steps](./images/install-steps.png)

Follow the [installation guide](./install.md#quick-install) to set up.

## Configuration

After installation, configure your environment:

1. Copy the [example config](./config.md#example-configuration)
2. Update [API settings](./config.md#api-configuration)
3. Test with [sample data](./examples.md#sample-datasets)

## First Steps

Now that you're set up, try these examples:

- [Hello World](./examples.md#hello-world-example)
- [Data Processing](./examples.md#data-processing)
- [Advanced Usage](./advanced.md#getting-started)

## Next Steps

Continue learning:

- Read the [user guide](./guide.md)
- Explore [advanced features](./advanced.md)
- Check [best practices](./best-practices.md)
- Join our [community forum](https://forum.example.com/)

For help, see the [FAQ](#faq) below.

## FAQ

Common questions and answers...
```

### Generated RST

```rst
Getting Started Tutorial
========================

Welcome! This tutorial will guide you through the basics.


Table of Contents
-----------------

- :ref:`installation`
- :ref:`configuration`
- :ref:`first-steps`
- :ref:`next-steps`


Installation
------------


.. image:: ./images/install-steps.png
   :alt: Installation Steps


Follow the :doc:`installation guide (Quick Install) <install>` to set up.


Configuration
-------------

After installation, configure your environment:

1. Copy the :doc:`example config (Example Configuration) <config>`
2. Update :doc:`API settings (Api Configuration) <config>`
3. Test with :doc:`sample data (Sample Datasets) <examples>`


First Steps
-----------

Now that you're set up, try these examples:

- :doc:`Hello World (Hello World Example) <examples>`
- :doc:`Data Processing (Data Processing) <examples>`
- :doc:`Advanced Usage (Getting Started) <advanced>`


Next Steps
----------

Continue learning:

- Read the :doc:`user guide <guide>`
- Explore :doc:`advanced features <advanced>`
- Check :doc:`best practices <best-practices>`
- Join our `community forum <https://forum.example.com/>`_

For help, see the :ref:`faq` below.


FAQ
---

Common questions and answers...
```

## Example 5: Cheat Sheet Document

### Input Markdown

```markdown
# Quick Reference

## Common Commands

For detailed explanations, see the [command reference](./commands.md).

### Basic Commands
- `init` - [Initialize project](./commands.md#init-command)
- `run` - [Run application](./commands.md#run-command)
- `test` - [Run tests](./commands.md#test-command)

### Advanced Commands
- `deploy` - [Deploy application](./commands.md#deploy-command)
- `config` - [Manage configuration](./commands.md#config-command)

## Configuration Files

Configuration documentation:
- [Main config](./config.md#main-configuration)
- [Environment variables](./config.md#environment-vars)
- [Logging setup](./config.md#logging-configuration)

## External Documentation

- [Python Docs](https://docs.python.org/)
- [Docker Docs](https://docs.docker.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)

Back to [main documentation](#).
```

### Generated RST

```rst
Quick Reference
===============


Common Commands
---------------

For detailed explanations, see the :doc:`command reference <commands>`.


Basic Commands
~~~~~~~~~~~~~~
- `init` - :doc:`Initialize project (Init Command) <commands>`
- `run` - :doc:`Run application (Run Command) <commands>`
- `test` - :doc:`Run tests (Test Command) <commands>`


Advanced Commands
~~~~~~~~~~~~~~~~~
- `deploy` - :doc:`Deploy application (Deploy Command) <commands>`
- `config` - :doc:`Manage configuration (Config Command) <commands>`


Configuration Files
-------------------

Configuration documentation:
- :doc:`Main config (Main Configuration) <config>`
- :doc:`Environment variables (Environment Vars) <config>`
- :doc:`Logging setup (Logging Configuration) <config>`


External Documentation
----------------------

- `Python Docs <https://docs.python.org/>`_
- `Docker Docs <https://docs.docker.com/>`_
- `Kubernetes Docs <https://kubernetes.io/docs/>`_

Back to :ref:`main documentation <#>`.
```

## Common Patterns Summary

### Pattern 1: Navigation Links
```markdown
- [Guide](./guide.md)
- [API](./api.md)
```

### Pattern 2: Links with Sections
```markdown
- [Installation](./install.md#prerequisites)
- [Config](./config.md#basic-setup)
```

### Pattern 3: External Resources
```markdown
- [Website](https://example.com/)
- [GitHub](https://github.com/project)
```

### Pattern 4: Same-Page Navigation
```markdown
- [Installation](#installation)
- [Configuration](#configuration)
```

### Pattern 5: Images
```markdown
![Diagram](./diagram.png)
```

## Key Takeaways

✅ **All link types are automatically converted**
✅ **Section names are added to link text**
✅ **Images become RST directives**
✅ **External links work perfectly**
✅ **Zero manual conversion needed**

Just write markdown naturally, and Introligo handles the conversion!
