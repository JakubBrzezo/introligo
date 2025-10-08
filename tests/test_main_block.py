"""Test the if __name__ == '__main__' block."""

import subprocess
import sys
from pathlib import Path


def test_main_block_execution(sample_yaml_config: Path, temp_dir: Path):
    """Test running introligo as a module via python -m."""
    output_dir = temp_dir / "output"

    # Run introligo as a module
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "introligo",
            str(sample_yaml_config),
            "-o",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0
    assert output_dir.exists()
    assert (output_dir / "index.rst").exists()


def test_main_block_direct_execution(sample_yaml_config: Path, temp_dir: Path):
    """Test running __main__.py directly."""
    output_dir = temp_dir / "output"

    # Get path to __main__.py
    from introligo import __main__ as main_module

    main_path = Path(main_module.__file__)

    # Run the file directly
    result = subprocess.run(
        [
            sys.executable,
            str(main_path),
            str(sample_yaml_config),
            "-o",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0
    assert output_dir.exists()
