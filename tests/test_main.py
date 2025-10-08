"""Tests for main() command-line interface."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from introligo import IntroligoError, main


class TestMainCLI:
    """Test main() CLI function."""

    def test_main_with_valid_config(self, sample_yaml_config: Path, temp_dir: Path):
        """Test main() with valid configuration."""
        output_dir = temp_dir / "output"

        test_args = ["introligo", str(sample_yaml_config), "-o", str(output_dir)]

        with patch.object(sys, "argv", test_args):
            main()

        # Check that output was generated
        assert output_dir.exists()
        assert (output_dir / "index.rst").exists()

    def test_main_dry_run(self, sample_yaml_config: Path, temp_dir: Path):
        """Test main() in dry-run mode."""
        output_dir = temp_dir / "output"

        test_args = [
            "introligo",
            str(sample_yaml_config),
            "-o",
            str(output_dir),
            "--dry-run",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Files should not be created in dry-run
        index_file = output_dir / "index.rst"
        assert not index_file.exists()

    def test_main_with_custom_template(self, sample_yaml_config: Path, temp_dir: Path):
        """Test main() with custom template."""
        output_dir = temp_dir / "output"
        template_file = temp_dir / "template.jinja2"
        template_file.write_text("{{ title }}\n{{ '=' * 10 }}", encoding="utf-8")

        test_args = [
            "introligo",
            str(sample_yaml_config),
            "-o",
            str(output_dir),
            "-t",
            str(template_file),
        ]

        with patch.object(sys, "argv", test_args):
            main()

        assert output_dir.exists()

    def test_main_verbose(self, sample_yaml_config: Path, temp_dir: Path):
        """Test main() with verbose flag."""
        output_dir = temp_dir / "output"

        test_args = [
            "introligo",
            str(sample_yaml_config),
            "-o",
            str(output_dir),
            "-v",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        assert output_dir.exists()

    def test_main_strict_mode(self, sample_yaml_config: Path, temp_dir: Path):
        """Test main() in strict mode."""
        output_dir = temp_dir / "output"

        test_args = [
            "introligo",
            str(sample_yaml_config),
            "-o",
            str(output_dir),
            "--strict",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        assert output_dir.exists()

    def test_main_missing_config(self, temp_dir: Path):
        """Test main() with missing config file."""
        missing_config = temp_dir / "missing.yaml"
        output_dir = temp_dir / "output"

        test_args = ["introligo", str(missing_config), "-o", str(output_dir)]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_invalid_yaml(self, temp_dir: Path):
        """Test main() with invalid YAML."""
        invalid_config = temp_dir / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: syntax:", encoding="utf-8")
        output_dir = temp_dir / "output"

        test_args = ["introligo", str(invalid_config), "-o", str(output_dir)]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_default_output_dir(self, sample_yaml_config: Path, temp_dir: Path):
        """Test main() uses default output directory."""
        # Change to temp directory so default 'docs' is created there
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            test_args = ["introligo", str(sample_yaml_config)]

            with patch.object(sys, "argv", test_args):
                main()

            # Check default 'docs' directory was created
            default_output = temp_dir / "docs"
            assert default_output.exists()
        finally:
            os.chdir(original_cwd)

    def test_main_with_doxygen_config(self, doxygen_config: Path, temp_dir: Path):
        """Test main() with Doxygen configuration."""
        output_dir = temp_dir / "output"

        test_args = ["introligo", str(doxygen_config), "-o", str(output_dir)]

        with patch.object(sys, "argv", test_args):
            main()

        # Check breathe config was generated
        breathe_config_path = output_dir / "generated" / "breathe_config.py"
        assert breathe_config_path.exists()

        # Check __init__.py was created
        init_path = output_dir / "generated" / "__init__.py"
        assert init_path.exists()

    def test_main_breathe_config_dry_run(self, doxygen_config: Path, temp_dir: Path):
        """Test main() doesn't generate breathe config in dry-run."""
        output_dir = temp_dir / "output"

        test_args = [
            "introligo",
            str(doxygen_config),
            "-o",
            str(output_dir),
            "--dry-run",
        ]

        with patch.object(sys, "argv", test_args):
            main()

        # Breathe config should not exist in dry-run
        breathe_config_path = output_dir / "generated" / "breathe_config.py"
        assert not breathe_config_path.exists()

    def test_main_unexpected_error(self, temp_dir: Path):
        """Test main() handles unexpected errors gracefully."""
        # Create a config that will cause an unexpected error
        config_file = temp_dir / "config.yaml"
        config_file.write_text("modules:\n  test:\n    title: Test", encoding="utf-8")

        output_dir = temp_dir / "output"

        # Mock to raise unexpected exception
        with patch(
            "introligo.__main__.IntroligoGenerator.generate_all",
            side_effect=RuntimeError("Unexpected"),
        ):
            test_args = ["introligo", str(config_file), "-o", str(output_dir)]

            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1

    def test_main_verbose_with_error(self, temp_dir: Path):
        """Test main() verbose mode with error shows traceback."""
        missing_config = temp_dir / "missing.yaml"
        output_dir = temp_dir / "output"

        test_args = ["introligo", str(missing_config), "-o", str(output_dir), "-v"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_verbose_unexpected_error_with_traceback(self, temp_dir: Path):
        """Test main() verbose mode prints traceback for unexpected errors."""
        config_file = temp_dir / "config.yaml"
        config_file.write_text("modules:\n  test:\n    title: Test", encoding="utf-8")
        output_dir = temp_dir / "output"

        test_args = ["introligo", str(config_file), "-o", str(output_dir), "-v"]

        # Mock to raise unexpected error
        with patch(
            "introligo.__main__.IntroligoGenerator.generate_all",
            side_effect=RuntimeError("Unexpected error"),
        ):
            with patch("traceback.print_exc") as mock_traceback:
                with patch.object(sys, "argv", test_args):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 1
                    # Should print traceback in verbose mode
                    mock_traceback.assert_called_once()


class TestMainEdgeCases:
    """Test edge cases in main() function."""

    def test_main_help_argument(self):
        """Test main() with help argument."""
        test_args = ["introligo", "--help"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_main_no_arguments(self):
        """Test main() without arguments."""
        test_args = ["introligo"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit):
                main()
