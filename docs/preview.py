#!/usr/bin/env python3
"""Preview builder for Introligo documentation.

This script provides a complete documentation build and preview pipeline:
- Runs Introligo to generate RST from YAML configuration
- Builds Sphinx HTML documentation
- Serves the site locally IF build succeeds
- Gracefully shuts down on Ctrl+C (SIGINT)
- Optionally watches for file changes and auto-rebuilds

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

    Watch for changes and auto-rebuild:
        $ python preview.py --watch

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
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# Path configuration
DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
BUILD_DIR = DOCS_DIR / "_build"
HTML_DIR = BUILD_DIR / "html"
EXAMPLES_DIR = PROJECT_ROOT / "examples"

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
    signal_map: dict[int, str] = {
        int(signal.SIGINT): "SIGINT (Ctrl+C)",
        int(signal.SIGTERM): "SIGTERM",
    }
    signal_name = signal_map.get(signum, f"Signal {signum}")

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


def list_examples() -> list[str]:
    """List all available examples in the examples directory.

    Returns:
        A list of example names (directory names in examples/)

    Note:
        Only directories containing introligo_config.yaml are considered valid examples.
    """
    if not EXAMPLES_DIR.exists():
        return []

    examples = []
    for item in EXAMPLES_DIR.iterdir():
        if item.is_dir() and (item / "introligo_config.yaml").exists():
            examples.append(item.name)
    return sorted(examples)


def get_example_config(example_name: str) -> Optional[Path]:
    """Get the path to an example's Introligo configuration file.

    Args:
        example_name: Name of the example (directory name in examples/)

    Returns:
        Path to the example's introligo_config.yaml if it exists, None otherwise

    Note:
        Prints error messages if the example is not found or invalid.
    """
    example_dir = EXAMPLES_DIR / example_name
    config_file = example_dir / "introligo_config.yaml"

    if not example_dir.exists():
        print(f"⛔ Example '{example_name}' not found in {EXAMPLES_DIR}")
        available = list_examples()
        if available:
            print(f"   Available examples: {', '.join(available)}")
        else:
            print("   No examples found. Create examples in the examples/ directory.")
        return None

    if not config_file.exists():
        print(f"⛔ Example '{example_name}' is missing introligo_config.yaml")
        return None

    return config_file


def run(
    cmd: Sequence[Union[str, Path]],
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
) -> Tuple[int, str]:
    """Run a command and return its exit code and output.

    Args:
        cmd: Command and arguments to execute
        cwd: Working directory for command execution (defaults to current directory)
        env: Environment variables for the command (defaults to current environment)

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
            env=env,
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


def run_introligo(
    config_file: Optional[Path] = None, skip: bool = False, output_dir: Optional[Path] = None
) -> bool:
    """Run Introligo to generate RST documentation from YAML configuration.

    Args:
        config_file: Path to Introligo YAML configuration file
        skip: If True, skip Introligo generation
        output_dir: Directory to output generated RST files (defaults to DOCS_DIR)

    Returns:
        True if Introligo completed successfully or was skipped, False otherwise

    Note:
        Creates the generated directory structure for Sphinx documentation.
        Uses the configuration file to generate hierarchical RST files.
        Auto-generates conf.py if 'sphinx' configuration is present in the YAML.
        Now uses the introligo package module instead of a script.
    """
    if skip:
        print("⏭️  Skipping Introligo generation (--skip-introligo flag)")
        return True

    if _shutdown_requested:
        return False

    config_path = config_file or INTROLIGO_CONFIG
    out_dir = output_dir or DOCS_DIR

    # Check if configuration file exists
    if not config_path.exists():
        print(f"⛔ Introligo config not found at {config_path}")
        print("   Tip: Create an introligo_config.yaml in docs/composition/")
        return False

    print("▶ Generating documentation structure with Introligo…")
    print(f"  📄 Config: {config_path}")
    print(f"  📁 Output: {out_dir}")

    # Use the config file's parent directory as working directory for relative paths
    config_dir = config_path.parent

    # Always try to run from source first since we're in the introligo repository
    introligo_main = PROJECT_ROOT / "introligo" / "__main__.py"

    if introligo_main.exists():
        # Run from source directory - we're in the introligo repo
        # Add project root to PYTHONPATH so introligo can be imported
        cmd_env = os.environ.copy()
        pythonpath = cmd_env.get("PYTHONPATH", "")
        cmd_env["PYTHONPATH"] = (
            f"{PROJECT_ROOT}{os.pathsep}{pythonpath}" if pythonpath else str(PROJECT_ROOT)
        )
        cmd = [sys.executable, str(introligo_main), str(config_path), "-o", str(out_dir)]
        print("  ℹ️  Running from source (not installed)")
    else:
        # Try installed version as fallback
        test_import = subprocess.run(
            [sys.executable, "-c", "import introligo"],
            capture_output=True,
            text=True,
        )

        if test_import.returncode == 0:
            # Introligo is installed, use -m to run it
            cmd = [sys.executable, "-m", "introligo", str(config_path), "-o", str(out_dir)]
            cmd_env = None
        else:
            print("⛔ Introligo not found as installed package or in source directory")
            print(f"   Expected source at: {introligo_main}")
            print("   Install with: pip install -e .")
            return False

    code, out = run(cmd, cwd=config_dir, env=cmd_env)

    if code != 0:
        print("⛔ Introligo failed to generate documentation structure")
        print("   Check your YAML configuration for errors")
        return False

    # Verify that files were generated
    generated_dir = out_dir / "generated"
    conf_py = out_dir / "conf.py"

    if generated_dir.exists():
        rst_files = list(generated_dir.rglob("*.rst"))
        print(f"✅ Introligo generated {len(rst_files)} RST files")
    else:
        print("⚠️  No generated directory found, Introligo may have failed silently")

    # Check if conf.py was generated
    if conf_py.exists():
        # Check if it was just created (modified time is recent)
        import time

        if time.time() - conf_py.stat().st_mtime < 10:  # Within last 10 seconds
            print("✅ Introligo auto-generated conf.py from sphinx configuration")

    return True


def run_sphinx(docs_dir: Optional[Path] = None, html_dir: Optional[Path] = None) -> bool:
    """Run Sphinx documentation build.

    Args:
        docs_dir: Directory containing Sphinx source files (defaults to DOCS_DIR)
        html_dir: Directory for HTML output (defaults to HTML_DIR)

    Returns:
        True if Sphinx build completed successfully, False otherwise

    Note:
        Uses -n (nitpicky) mode for better error detection.
        Expects conf.py to be auto-generated by Introligo if sphinx config is present.
    """
    if _shutdown_requested:
        return False

    src_dir = docs_dir or DOCS_DIR
    out_dir = html_dir or HTML_DIR

    print("▶ Building Sphinx documentation…")

    # Check if conf.py exists
    conf_path = src_dir / "conf.py"
    if not conf_path.exists():
        print(f"⛔ Sphinx conf.py not found at {conf_path}")
        print("   Introligo should have generated conf.py if 'sphinx' configuration exists")
        print(
            "   Please add 'sphinx' section to your introligo_config.yaml"
            " or create conf.py manually"
        )
        print("   See docs/sphinx_config_guide.md for details")
        return False

    # -n => nitpicky checks, -b html => HTML builder
    code, out = run(["sphinx-build", "-n", "-b", "html", str(src_dir), str(out_dir)])

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
        port: int = s.getsockname()[1]
        return port


def serve_docs(port: Optional[int] = None, html_dir: Optional[Path] = None) -> None:
    """Serve built docs and handle shutdown gracefully.

    Args:
        port: Port number to serve on (defaults to auto-detection starting at 8000)
        html_dir: Directory containing HTML files to serve (defaults to HTML_DIR)

    Raises:
        SystemExit: If HTML directory doesn't exist

    Note:
        Changes to HTML directory for serving, restores original directory on exit.
        Sets up global _httpd reference for signal handler access.
    """
    global _httpd

    if _shutdown_requested:
        return

    serve_dir = html_dir or HTML_DIR

    if not serve_dir.exists():
        print(f"⛔ HTML directory does not exist: {serve_dir}")
        sys.exit(2)

    port = port or find_free_port(8000)
    old_cwd = Path.cwd()
    try:
        os.chdir(serve_dir)

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


class DocumentationWatcher(FileSystemEventHandler):
    """File system event handler for watching documentation source files.

    Monitors changes to YAML, Python, RST, and Markdown files and triggers
    documentation rebuild when changes are detected.

    Attributes:
        config_file (Optional[Path]): Path to Introligo config file
        docs_dir (Path): Directory containing documentation source
        html_dir (Path): Directory for HTML output
        debounce_seconds (float): Minimum seconds between rebuilds
        last_build_time (float): Timestamp of last successful build
        build_lock (threading.Lock): Lock to prevent concurrent rebuilds
    """

    def __init__(
        self,
        config_file: Optional[Path] = None,
        docs_dir: Optional[Path] = None,
        html_dir: Optional[Path] = None,
        debounce_seconds: float = 2.0,
    ):
        """Initialize the documentation watcher.

        Args:
            config_file: Path to Introligo configuration file
            docs_dir: Directory containing documentation source
            html_dir: Directory for HTML output
            debounce_seconds: Minimum seconds between rebuilds (default: 2.0)
        """
        super().__init__()
        self.config_file = config_file
        self.docs_dir = docs_dir or DOCS_DIR
        self.html_dir = html_dir or HTML_DIR
        self.debounce_seconds = debounce_seconds
        self.last_build_time = 0.0
        self.build_lock = threading.Lock()

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Handle any file system event.

        Args:
            event: The file system event that occurred

        Note:
            Filters events to only rebuild on relevant file changes.
            Uses debouncing to avoid excessive rebuilds.
        """
        if _shutdown_requested:
            return

        # Ignore directory events and build output
        if event.is_directory or "_build" in str(event.src_path):
            return

        # Only watch relevant file types
        relevant_extensions = {".yaml", ".yml", ".py", ".rst", ".md", ".txt"}
        src_path_str = str(event.src_path) if isinstance(event.src_path, bytes) else event.src_path
        file_path = Path(src_path_str)

        if file_path.suffix not in relevant_extensions:
            return

        # Debounce: skip if last build was too recent
        current_time = time.time()
        if current_time - self.last_build_time < self.debounce_seconds:
            return

        # Try to acquire lock (non-blocking)
        if not self.build_lock.acquire(blocking=False):
            return  # Build already in progress

        try:
            print(f"\n📝 Detected change in: {file_path.name}")
            print("🔄 Rebuilding documentation...")
            print("-" * 50)

            # Run Introligo and Sphinx
            if run_introligo(self.config_file, output_dir=self.docs_dir):
                if run_sphinx(self.docs_dir, self.html_dir):
                    print("✅ Documentation rebuilt successfully!")
                    print(f"🕒 Last updated: {time.strftime('%H:%M:%S')}")
                    self.last_build_time = current_time
                else:
                    print("⛔ Sphinx build failed")
            else:
                print("⛔ Introligo generation failed")

            print("-" * 50)
        finally:
            self.build_lock.release()


def watch_and_serve(
    config_file: Optional[Path] = None,
    docs_dir: Optional[Path] = None,
    html_dir: Optional[Path] = None,
    port: Optional[int] = None,
) -> None:
    """Watch for file changes and auto-rebuild while serving documentation.

    Args:
        config_file: Path to Introligo configuration file
        docs_dir: Directory containing documentation source
        html_dir: Directory for HTML output
        port: Port number for documentation server

    Raises:
        SystemExit: If watchdog is not available

    Note:
        Runs the file watcher and HTTP server in parallel threads.
        Watches for changes in the documentation source directory.
    """
    if not WATCHDOG_AVAILABLE:
        print("⛔ Watch mode requires the 'watchdog' package")
        print("   Install with: pip install watchdog")
        print("   Or install dev dependencies: pip install -e .[dev]")
        sys.exit(1)

    watch_dir = docs_dir or DOCS_DIR
    serve_dir = html_dir or HTML_DIR

    print("👀 Starting watch mode...")
    print(f"📂 Watching: {watch_dir}")
    print("   Monitoring: *.yaml, *.yml, *.py, *.rst, *.md files")
    print("-" * 50)

    # Set up file watcher
    event_handler = DocumentationWatcher(
        config_file=config_file,
        docs_dir=watch_dir,
        html_dir=serve_dir,
    )

    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=True)

    # Also watch the examples directory if we're in the main docs
    if watch_dir == DOCS_DIR and EXAMPLES_DIR.exists():
        observer.schedule(event_handler, str(EXAMPLES_DIR), recursive=True)
        print(f"📂 Also watching: {EXAMPLES_DIR}")

    observer.start()

    try:
        # Start the HTTP server (this will block until shutdown)
        serve_docs(port=port, html_dir=serve_dir)
    finally:
        print("🛑 Stopping file watcher...")
        observer.stop()
        observer.join()


def main() -> None:
    """Main entry point for the documentation builder and server.

    Orchestrates the complete documentation build pipeline:
    1. Sets up signal handlers for graceful shutdown
    2. Runs Introligo to generate RST from YAML (and conf.py if sphinx config present)
    3. Runs Sphinx HTML build
    4. Serves the documentation locally

    Raises:
        SystemExit: On build failures or user interruption

    Note:
        Each stage checks for shutdown requests and can exit cleanly.
        If 'sphinx' configuration is present in the YAML, conf.py is auto-generated.
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
  %(prog)s --watch                 # Watch for changes and auto-rebuild
  %(prog)s --example python_project # Run example by name
  %(prog)s --list-examples         # List all available examples
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

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for file changes and auto-rebuild documentation (requires watchdog)",
    )

    parser.add_argument(
        "--example",
        type=str,
        help="Run a specific example by name (e.g., python_project, c_project)",
    )

    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="List all available examples in the examples/ directory",
    )

    args = parser.parse_args()

    try:
        # Handle --list-examples
        if args.list_examples:
            examples = list_examples()
            if examples:
                print("📚 Available examples:")
                for example in examples:
                    example_dir = EXAMPLES_DIR / example
                    readme = example_dir / "README.md"
                    if readme.exists():
                        # Try to extract first line of README as description
                        with open(readme) as f:
                            first_line = f.readline().strip().lstrip("#").strip()
                        print(f"  • {example:<20} - {first_line}")
                    else:
                        print(f"  • {example}")
                print(f"\n💡 Run an example with: {sys.argv[0]} --example <name>")
            else:
                print("📚 No examples found in examples/ directory")
            sys.exit(0)

        # Handle --example
        if args.example:
            example_config = get_example_config(args.example)
            if not example_config:
                sys.exit(1)

            # Override config with example config
            args.config = example_config

            # Use example directory for output
            example_dir = EXAMPLES_DIR / args.example
            example_docs_dir = example_dir / "docs"

            print(f"🎯 Running example: {args.example}")
            print(f"📁 Example directory: {example_dir}")
            print("-" * 50)

        # Set up signal handlers first
        setup_signal_handlers()

        # Determine output directory
        if args.example:
            output_dir = example_docs_dir
            build_dir = output_dir / "_build"
            html_dir = build_dir / "html"
        else:
            output_dir = DOCS_DIR
            build_dir = BUILD_DIR
            html_dir = HTML_DIR

        print("🚀 Starting Introligo documentation build...")
        print(f"📁 Working directory: {output_dir.parent if args.example else DOCS_DIR}")
        print(f"🎯 Output directory: {html_dir}")
        print("-" * 50)

        # Run Introligo first to generate RST structure
        if not run_introligo(args.config, args.skip_introligo, output_dir):
            print("⛔ Build failed at Introligo stage")
            sys.exit(1)

        if _shutdown_requested:
            print("🛑 Build cancelled by user")
            sys.exit(0)

        # Run Sphinx
        if not run_sphinx(output_dir, html_dir):
            print("⛔ Build failed at Sphinx stage")
            sys.exit(1)

        if _shutdown_requested:
            print("🛑 Build cancelled by user")
            sys.exit(0)

        print("✅ Documentation build completed successfully!")
        print("-" * 50)

        # Serve the documentation unless --no-serve flag is used
        if not args.no_serve:
            if args.watch:
                # Watch mode: monitor for changes and auto-rebuild
                watch_and_serve(
                    config_file=args.config,
                    docs_dir=output_dir,
                    html_dir=html_dir,
                    port=args.port,
                )
            else:
                # Regular mode: just serve
                serve_docs(port=args.port, html_dir=html_dir)
        else:
            if args.watch:
                print("⚠️  Warning: --watch and --no-serve are incompatible")
                print("   Watch mode requires serving to be useful")
            print(f"📁 Documentation built at: {html_dir}")
            print(f"💡 To serve manually: python -m http.server {args.port} --directory {html_dir}")

    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"⛔ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
