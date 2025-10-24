#!/usr/bin/env python
"""YAML loader with !include directive support.

Copyright (c) 2025 WT Tech Jakub Brzezowski
"""

import logging
from pathlib import Path
from typing import Any, cast

import yaml

from .errors import IntroligoError

logger = logging.getLogger(__name__)


class IncludeLoader(yaml.SafeLoader):
    """YAML loader with support for !include directive.

    Allows splitting configuration across multiple files using:
        !include path/to/file.yaml

    Paths are resolved relative to the file containing the !include directive.
    """

    def __init__(self, stream):
        """Initialize the loader with file path tracking.

        Args:
            stream: YAML input stream, typically a file object.
        """
        self._root_dir = Path.cwd()

        # Track the directory of the current file for relative includes
        if hasattr(stream, "name"):
            self._current_file = Path(stream.name).resolve()
            self._root_dir = self._current_file.parent

        super().__init__(stream)


def include_constructor(loader: IncludeLoader, node: yaml.Node) -> Any:
    """Construct included YAML content.

    Args:
        loader: The YAML loader instance
        node: The YAML node containing the include path

    Returns:
        The loaded content from the included file

    Raises:
        IntroligoError: If the included file cannot be loaded
    """
    # Get the path from the node
    include_path = loader.construct_scalar(cast(yaml.ScalarNode, node))

    # Resolve path relative to the current file's directory
    if hasattr(loader, "_root_dir"):
        full_path = (loader._root_dir / include_path).resolve()
    else:
        full_path = Path(include_path).resolve()

    if not full_path.exists():
        raise IntroligoError(f"Include file not found: {full_path}")

    logger.debug(f"  Including: {full_path}")

    # Load the included file with the same loader to support nested includes
    try:
        with open(full_path, encoding="utf-8") as f:
            return yaml.load(f, Loader=IncludeLoader)
    except yaml.YAMLError as e:
        raise IntroligoError(f"Invalid YAML in included file {full_path}: {e}") from e
    except Exception as e:
        raise IntroligoError(f"Error loading included file {full_path}: {e}") from e


# Register the include constructor
yaml.add_constructor("!include", include_constructor, IncludeLoader)
