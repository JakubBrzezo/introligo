#!/usr/bin/env python3
"""Preview builder for Introligo documentation.

This script provides a complete documentation build and preview pipeline:
- Runs Introligo to generate RST from YAML configuration
- Builds Sphinx HTML documentation
- Serves the site locally IF build succeeds
- Gracefully shuts down on Ctrl+C (SIGINT)

Copyright (c) 2025 WT Tech Jakub Brzezowski
This is an open-source component of the Celin Project

Example:
    Run the documentation builder and server:
        $ python preview.py

    With custom Introligo config:
        $ python preview.py --config my_config.yaml

    Skip Introligo generation (use existing RST):
        $ python preview.py --skip-introligo

    Build only, don't serve:
        $ python preview.py --no-serve

    The script will build docs and serve them at http://localhost:8000
    Press Ctrl+C to stop the server gracefully.

Attributes:
    DOCS_DIR (Path): Path to the documentation source directory (this directory)
    BUILD_DIR (Path): Path to the build output directory
    HTML_DIR (Path): Path to the HTML output directory
    PROJECT_ROOT (Path): Path to the introligo project root
    INTROLIGO_CONFIG (Path): Default path to Introligo YAML configuration
    _shutdown_requested (bool): Global flag for coordinating shutdown
    _httpd (Optional[GracefulHTTPServer]): Global reference to HTTP server
"""

import argparse
import contextlib
import http.server
import os
import signal
import socket
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional, Tuple, Union

# Path configuration
DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
BUILD_DIR = DOCS_DIR / "_build"
HTML_DIR = BUILD_DIR / "html"

# Default Introligo configuration file
INTROLIGO_CONFIG = DOCS_DIR / "composition" / "introligo_config.yaml"

# Global flag for clean shutdown
_shutdown_requested: bool = False
_httpd: Optional["GracefulHTTPServer"] = None


def signal_handler(signum: int, frame: Optional[object]) -> None:
    """Handle Ctrl+C and other termination signals.

    Args:
        signum: The signal number that was received
        frame: The current stack frame (unused)

    Note:
        Sets the global shutdown flag and initiates server shutdown.
        Uses threading to avoid blocking the signal handler.
    """
    global _shutdown_requested
    signal_name = {signal.SIGINT: "SIGINT (Ctrl+C)", signal.SIGTERM: "SIGTERM"}.get(
        signum, f"Signal {signum}"
    )

    print(f"\n🛑 Received {signal_name}, shutting down gracefully...")
    _shutdown_requested = True

    # If we have a running HTTP server, shut it down
    if _httpd:
        try:
            # Use threading to avoid blocking the signal handler
            shutdown_thread = threading.Thread(target=_httpd.shutdown, daemon=True)
            shutdown_thread.start()
        except Exception as e:
            print(f"Warning: Error during server shutdown: {e}")

    # Give a moment for cleanup, then exit
    sys.exit(0)


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown.

    Registers handlers for SIGINT (Ctrl+C) and SIGTERM signals.
    SIGTERM is only registered on systems that support it.
    """
    signal.signal(signal.SIGINT, signal_handler)
    # Handle SIGTERM on Unix systems
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)


def run(cmd: list[Union[str, Path]], cwd: Optional[Path] = None) -> Tuple[int, str]:
    """Run a command and return its exit code and output.

    Args:
        cmd: Command and arguments to execute
        cwd: Working directory for command execution (defaults to current directory)

    Returns:
        A tuple containing (return_code, combined_stdout_stderr)

    Note:
        Commands have a 5-minute timeout and can be interrupted by Ctrl+C.
        If shutdown is requested, the command is skipped.
    """
    if _shutdown_requested:
        print("🛑 Shutdown requested, skipping command execution")
        return 1, ""

    print(f"→ {' '.join(map(str, cmd))}")
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        if proc.stdout:
            print(proc.stdout)
        return proc.returncode, proc.stdout
    except subprocess.TimeoutExpired:
        print("⛔ Command timed out after 5 minutes")
        return 1, ""
    except KeyboardInterrupt:
        print("\n🛑 Command interrupted by user")
        return 1, ""
    except Exception as e:
        print(f"⛔ Command failed with exception: {e}")
        return 1, ""


def run_introligo(config_file: Optional[Path] = None, skip: bool = False) -> bool:
    """Run Introligo to generate RST documentation from YAML configuration.

    Args:
        config_file: Path to Introligo YAML configuration file
        skip: If True, skip Introligo generation

    Returns:
        True if Introligo completed successfully or was skipped, False otherwise

    Note:
        Creates the generated directory structure for Sphinx documentation.
        Uses the configuration file to generate hierarchical RST files.
        Now uses the introligo package module instead of a script.
    """
    if skip:
        print("⏭️  Skipping Introligo generation (--skip-introligo flag)")
        return True

    if _shutdown_requested:
        return False

    config_path = config_file or INTROLIGO_CONFIG

    # Check if configuration file exists
    if not config_path.exists():
        print(f"⛔ Introligo config not found at {config_path}")
        print("   Tip: Create an introligo_config.yaml in docs/composition/")
        return False

    print("▶ Generating documentation structure with Introligo…")
    print(f"  📄 Config: {config_path}")
    print(f"  📁 Output: {DOCS_DIR}")

    # Run Introligo as a Python module
    # This works whether introligo is installed via pip or running from source
    cmd = [sys.executable, "-m", "introligo", str(config_path), "-o", str(DOCS_DIR)]

    code, out = run(cmd, cwd=PROJECT_ROOT)

    if code != 0:
        print("⛔ Introligo failed to generate documentation structure")
        print("   Check your YAML configuration for errors")
        return False

    # Verify that files were generated
    generated_dir = DOCS_DIR / "generated"
    if generated_dir.exists():
        rst_files = list(generated_dir.rglob("*.rst"))
        print(f"✅ Introligo generated {len(rst_files)} RST files")
    else:
        print("⚠️  No generated directory found, Introligo may have failed silently")

    return True


def run_sphinx() -> bool:
    """Run Sphinx documentation build.

    Returns:
        True if Sphinx build completed successfully, False otherwise

    Note:
        Uses -n (nitpicky) mode for better error detection.
    """
    if _shutdown_requested:
        return False

    print("▶ Building Sphinx documentation…")

    # Check if conf.py exists
    conf_path = DOCS_DIR / "conf.py"
    if not conf_path.exists():
        print(f"⛔ Sphinx conf.py not found at {conf_path}")
        print("   Please create a Sphinx configuration file")
        return False

    # -n => nitpicky checks, -b html => HTML builder
    code, out = run(["sphinx-build", "-n", "-b", "html", str(DOCS_DIR), str(HTML_DIR)])

    if code != 0:
        print("⛔ Sphinx build failed")
        return False

    print("✅ Sphinx build completed successfully")
    return True


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with reduced logging.

    Only logs errors and important status codes (404, 500, 403).
    Inherits from SimpleHTTPRequestHandler for file serving.
    """

    def log_message(self, format: str, *args) -> None:
        """Override to reduce logging verbosity.

        Args:
            format: Log message format string
            *args: Arguments for the format string

        Note:
            Only logs if the response contains error status codes.
        """
        # Only log errors and important messages
        if any(code in args[1] if len(args) > 1 else "" for code in ["404", "500", "403"]):
            super().log_message(format, *args)


class GracefulHTTPServer(http.server.ThreadingHTTPServer):
    """HTTP server with graceful shutdown capabilities.

    Extends ThreadingHTTPServer to add clean shutdown functionality
    and better control over the serving loop.

    Attributes:
        allow_reuse_address (bool): Allows socket reuse for quick restarts
        timeout (float): Socket timeout for serve_forever loop
        shutdown_flag (threading.Event): Event to coordinate shutdown
    """

    allow_reuse_address = True
    timeout = 1.0  # Socket timeout for serve_forever

    def __init__(
        self,
        server_address: Tuple[str, int],
        request_handler_class: type,  # noqa: N803
        bind_and_activate: bool = True,
    ):
        """Initialize the graceful HTTP server.

        Args:
            server_address: (host, port) tuple for server binding
            request_handler_class: Handler class for processing requests
            bind_and_activate: Whether to bind and activate immediately
        """
        super().__init__(server_address, request_handler_class, bind_and_activate)
        self.shutdown_flag = threading.Event()

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        """Serve requests until shutdown is requested.

        Args:
            poll_interval: How often to check for shutdown requests (seconds)

        Note:
            Overrides the parent method to add shutdown flag checking.
            Will exit cleanly when shutdown_flag is set or global shutdown requested.
        """
        self.shutdown_flag.clear()
        try:
            while not self.shutdown_flag.is_set() and not _shutdown_requested:
                self.handle_request()
        except Exception as e:
            if not _shutdown_requested:
                print(f"Server error: {e}")
        finally:
            self.server_close()

    def shutdown(self) -> None:
        """Signal shutdown and close the server.

        Sets the internal shutdown flag and calls parent shutdown method.
        """
        self.shutdown_flag.set()
        super().shutdown()


def find_free_port(preferred: int = 8000) -> int:
    """Find a free TCP port, trying preferred port first.

    Args:
        preferred: The preferred port number to try first

    Returns:
        An available port number

    Note:
        If the preferred port is unavailable, returns any free port.
    """
    with socket.socket() as s:
        try:
            s.bind(("", preferred))
            return preferred
        except OSError:
            pass

    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def serve_docs(port: Optional[int] = None) -> None:
    """Serve built docs and handle shutdown gracefully.

    Args:
        port: Port number to serve on (defaults to auto-detection starting at 8000)

    Raises:
        SystemExit: If HTML directory doesn't exist

    Note:
        Changes to HTML directory for serving, restores original directory on exit.
        Sets up global _httpd reference for signal handler access.
    """
    global _httpd

    if _shutdown_requested:
        return

    if not HTML_DIR.exists():
        print(f"⛔ HTML directory does not exist: {HTML_DIR}")
        sys.exit(2)

    port = port or find_free_port(8000)
    old_cwd = Path.cwd()
    try:
        os.chdir(HTML_DIR)

        # Create server with custom handler
        _httpd = GracefulHTTPServer(("", port), QuietHTTPRequestHandler)

        print(f"🌐 Documentation server starting at http://localhost:{port}")
        print("📝 Press Ctrl+C to stop the server")
        print("-" * 50)

        # Start serving in a try block to catch any exceptions
        _httpd.serve_forever(poll_interval=0.5)

    except KeyboardInterrupt:
        # This shouldn't happen due to signal handler, but just in case
        print("\n🛑 Keyboard interrupt received")
    except Exception as e:
        print(f"⛔ Server error: {e}")
    finally:
        # Cleanup
        if _httpd:
            with contextlib.suppress(Exception):
                _httpd.server_close()
            _httpd = None

        # Restore original directory
        with contextlib.suppress(Exception):
            os.chdir(old_cwd)

        print("🔄 Server stopped, cleanup completed")


def main() -> None:
    """Main entry point for the documentation builder and server.

    Orchestrates the complete documentation build pipeline:
    1. Sets up signal handlers for graceful shutdown
    2. Runs Introligo to generate RST from YAML
    3. Runs Sphinx HTML build
    4. Serves the documentation locally

    Raises:
        SystemExit: On build failures or user interruption

    Note:
        Each stage checks for shutdown requests and can exit cleanly.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Build and preview Introligo documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                         # Build everything with defaults
  %(prog)s --skip-introligo        # Skip Introligo generation, use existing RST
  %(prog)s --config custom.yaml    # Use custom Introligo config
  %(prog)s --port 8080             # Serve on specific port
  %(prog)s --no-serve              # Build only, don't serve
        """,
    )

    parser.add_argument(
        "--config",
        type=Path,
        help=f"Path to Introligo YAML configuration (default: {INTROLIGO_CONFIG})",
    )

    parser.add_argument(
        "--skip-introligo",
        action="store_true",
        help="Skip Introligo documentation generation (use existing RST files)",
    )

    parser.add_argument(
        "--port", type=int, default=8000, help="Port for the documentation server (default: 8000)"
    )

    parser.add_argument(
        "--no-serve",
        action="store_true",
        help="Build documentation but don't start the preview server",
    )

    args = parser.parse_args()

    try:
        # Set up signal handlers first
        setup_signal_handlers()

        print("🚀 Starting Introligo documentation build...")
        print(f"📁 Working directory: {DOCS_DIR}")
        print(f"🎯 Output directory: {HTML_DIR}")
        print("-" * 50)

        # Run Introligo first to generate RST structure
        if not run_introligo(args.config, args.skip_introligo):
            print("⛔ Build failed at Introligo stage")
            sys.exit(1)

        if _shutdown_requested:
            print("🛑 Build cancelled by user")
            sys.exit(0)

        # Run Sphinx
        if not run_sphinx():
            print("⛔ Build failed at Sphinx stage")
            sys.exit(1)

        if _shutdown_requested:
            print("🛑 Build cancelled by user")
            sys.exit(0)

        print("✅ Documentation build completed successfully!")
        print("-" * 50)

        # Serve the documentation unless --no-serve flag is used
        if not args.no_serve:
            serve_docs(port=args.port)
        else:
            print(f"📁 Documentation built at: {HTML_DIR}")
            print(f"💡 To serve manually: python -m http.server {args.port} --directory {HTML_DIR}")

    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"⛔ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
