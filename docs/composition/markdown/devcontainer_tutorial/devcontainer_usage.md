## Overview

Introligo includes a pre-configured devcontainer that provides a complete development environment with all required dependencies, tools, and IDE extensions. This ensures consistency across different development machines and simplifies setup.

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Docker Desktop** or **Docker Engine**
   - Windows/Mac: [Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Linux: Docker Engine (see your distribution's package manager)

2. **Visual Studio Code**
   - Download from [code.visualstudio.com](https://code.visualstudio.com/)

3. **Dev Containers Extension**
   - Install from VS Code marketplace: [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - Or install via command palette: `ext install ms-vscode-remote.remote-containers`

## Opening the Project in Devcontainer

### Method 1: Using VS Code Command Palette

1. Open the Introligo project folder in VS Code
2. Press `F1` or `Ctrl+Shift+P` (Windows/Linux) / `Cmd+Shift+P` (Mac)
3. Type and select: **"Dev Containers: Reopen in Container"**
4. Wait for the container to build (first time takes a few minutes)
5. Once complete, you're ready to develop!

### Method 2: Using VS Code Notification

1. Open the Introligo project folder in VS Code
2. VS Code should detect the `.devcontainer` folder and show a notification
3. Click **"Reopen in Container"** in the notification
4. Wait for the container to build

### Method 3: Using Command Line

```bash
# Navigate to the project directory
cd /path/to/introligo

# Open in devcontainer using VS Code CLI
code .

# Then use Method 1 or 2 above
```

## What's Included in the Devcontainer

The devcontainer provides a complete Python 3.11 development environment with:

### System Tools
- Git, curl, wget
- Build tools (gcc, g++, make, cmake)
- Doxygen and Graphviz (for C++ documentation)
- Text editors (vim, nano)
- Shell tools (zsh with Oh My Zsh)
- Tree command for directory visualization

### Python Dependencies
All required Python packages are automatically installed:
- Sphinx (documentation generation)
- Furo (Sphinx theme)
- Breathe (C++ documentation integration)
- pytest and pytest-cov (testing)
- ruff (linting and formatting)
- mypy (type checking)
- watchdog (file system monitoring)
- PyYAML and Jinja2 (core dependencies)

### VS Code Extensions
Pre-installed extensions:
- Python extension pack
- Ruff (formatting and linting)
- Mypy type checker
- YAML support
- Markdown support
- Code spell checker
- GitLens

### Project Setup
The devcontainer automatically:
- Installs the project in editable mode: `pip install -e .[dev,docs,cpp]`
- Configures Python interpreter
- Sets up pytest for testing
- Configures Ruff as the default formatter
- Enables format-on-save

## Working in the Devcontainer

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=introligo

# Run specific test file
pytest tests/test_specific.py

# Run tests in verbose mode
pytest -v
```

### Building Documentation

```bash
# Navigate to docs directory
cd docs/

# Build and serve documentation (recommended)
python preview.py

# Build only without serving
python preview.py --no-serve

# Using Make
make html
make serve
```

### Running Introligo

```bash
# Generate documentation from config
python -m introligo config.yaml -o docs

# Dry run (preview without generating)
python -m introligo config.yaml -o docs --dry-run

# Verbose output
python -m introligo config.yaml -o docs -v
```

### Code Quality Tools

```bash
# Format code with Ruff
ruff format .

# Check code with Ruff
ruff check .

# Auto-fix issues
ruff check --fix .

# Type checking with mypy
mypy introligo
```

### Git Operations

```bash
# Check status
git status

# Create branch
git checkout -b feature/my-feature

# Commit changes
git add .
git commit -m "Description of changes"

# Push changes
git push origin feature/my-feature
```

## Port Forwarding

The devcontainer forwards port **8000** by default, which is used for serving documentation. When you run `python preview.py`, the documentation will be accessible at:

```
http://localhost:8000
```

VS Code automatically handles port forwarding, so you can access it from your host machine's browser.

## File Synchronization

Files are synchronized between your host machine and the container:
- The workspace is mounted at `/workspace` in the container
- All changes in the container are immediately reflected on your host
- All changes on your host are immediately reflected in the container

This means you can edit files in VS Code (running in the container) and see changes immediately on your host filesystem.

## Customizing Your Environment

### Installing Additional Python Packages

```bash
# Install package in the container
pip install package-name

# To persist, add to pyproject.toml dependencies
```

### Installing Additional VS Code Extensions

1. Open Extensions panel in VS Code (`Ctrl+Shift+X`)
2. Search for and install extensions
3. To persist, add extension ID to `.devcontainer/devcontainer.json`:

```json
"extensions": [
    "existing.extension",
    "new.extension.id"
]
```

### Modifying Container Configuration

Edit `.devcontainer/devcontainer.json` or `.devcontainer/Dockerfile` to customize:
- Add system packages
- Change Python version
- Add environment variables
- Configure additional settings

After modifying, rebuild the container:
1. Press `F1` or `Ctrl+Shift+P`
2. Select: **"Dev Containers: Rebuild Container"**

## Troubleshooting

### Container Won't Build

**Problem**: Docker build fails or times out

**Solutions**:
- Check Docker is running: `docker ps`
- Increase Docker memory allocation (Docker Desktop > Settings > Resources)
- Clear Docker cache: `docker system prune -a`
- Rebuild without cache: Use "Dev Containers: Rebuild Container Without Cache"

### Extensions Not Working

**Problem**: VS Code extensions don't work properly

**Solutions**:
- Reload window: `Ctrl+Shift+P` > "Developer: Reload Window"
- Reinstall extensions in container
- Check extension compatibility with container OS (Linux)

### Port Already in Use

**Problem**: Port 8000 is already in use

**Solutions**:
- Stop other services using port 8000
- Use different port: `python preview.py --port 8080`
- Modify port forwarding in `.devcontainer/devcontainer.json`

### Slow Performance

**Problem**: Container is slow or unresponsive

**Solutions**:
- Allocate more resources to Docker (Settings > Resources)
- Close unnecessary applications
- Use WSL 2 backend on Windows (faster than Hyper-V)
- Ensure workspace is on fast storage (SSD)

### Permission Issues

**Problem**: Permission denied errors

**Solutions**:
- The container runs as user `vscode` (UID 1000)
- Files created in container may have different ownership
- Use `sudo` for system-level operations
- Check file permissions: `ls -la`

## Exiting the Devcontainer

### Closing the Container

1. Close VS Code window, or
2. `F1` > "Dev Containers: Reopen Folder Locally"

The container will stop automatically when you close VS Code.

### Removing the Container

```bash
# List containers
docker ps -a

# Remove container
docker rm introligo-dev-container

# Remove image (rebuild will be required)
docker rmi introligo-development
```

## Best Practices

1. **Always use the devcontainer for development** to ensure consistency
2. **Don't install packages globally** - use virtual environments or project dependencies
3. **Commit `.devcontainer` changes** so all team members benefit
4. **Rebuild after configuration changes** to apply updates
5. **Use git inside the container** for proper line endings and permissions
6. **Keep Docker updated** for best performance and security

## Additional Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Documentation](https://docs.docker.com/)
- [Devcontainer Specification](https://containers.dev/)
- [Introligo Documentation](https://jakubbrzezo.github.io/introligo)

## See Also

- [Setting Up Devcontainer in Your Project](./devcontainer_setup.md) - Configure devcontainers for your own projects
- [Introligo README](../../README.md) - Main project documentation
