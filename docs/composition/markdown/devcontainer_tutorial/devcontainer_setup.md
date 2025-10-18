## Overview

Development containers (devcontainers) provide isolated, reproducible development environments using Docker. This guide will help you set up a devcontainer for projects that use Introligo or similar Python documentation workflows.

## Benefits of Using Devcontainers

- **Consistency**: Same environment for all developers
- **Easy Onboarding**: New developers can start immediately
- **Isolation**: Don't pollute your host system
- **Reproducibility**: Exact versions of tools and dependencies
- **Pre-configured**: IDE settings, extensions, and tools ready to use

## Prerequisites

1. **Docker** (Docker Desktop or Docker Engine)
2. **Visual Studio Code**
3. **Dev Containers Extension** for VS Code

See [Running Code in Devcontainer](./devcontainer_usage.md#prerequisites) for installation instructions.

## Quick Setup

### Step 1: Create Devcontainer Directory

Create a `.devcontainer` directory in your project root:

```bash
mkdir .devcontainer
cd .devcontainer
```

### Step 2: Create Dockerfile

Create `.devcontainer/Dockerfile`:

```dockerfile
# Use Python 3.11 as base image
FROM python:3.11-bullseye

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git \
    curl \
    vim \
    nano \
    tree \
    sudo \
    # For C++ documentation (optional)
    doxygen \
    graphviz \
    # Cleanup
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Set the default user
USER $USERNAME

# Set working directory
WORKDIR /workspace

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Default command
CMD ["/bin/bash"]
```

### Step 3: Create devcontainer.json

Create `.devcontainer/devcontainer.json`:

```json
{
    "name": "My Project Development",
    "build": {
        "dockerfile": "Dockerfile",
        "context": ".."
    },

    "customizations": {
        "vscode": {
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.testing.pytestEnabled": true,
                "[python]": {
                    "editor.defaultFormatter": "charliermarsh.ruff",
                    "editor.formatOnSave": true,
                    "editor.codeActionsOnSave": {
                        "source.organizeImports": "explicit"
                    }
                }
            },
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "yzhang.markdown-all-in-one"
            ]
        }
    },

    "forwardPorts": [8000],

    "postCreateCommand": "pip install -e .[dev]",

    "remoteUser": "vscode",

    "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
    "workspaceFolder": "/workspace",

    "features": {
        "ghcr.io/devcontainers/features/common-utils:2": {
            "installZsh": true,
            "installOhMyZsh": true,
            "upgradePackages": true
        },
        "ghcr.io/devcontainers/features/git:1": {
            "version": "latest"
        }
    }
}
```

### Step 4: Test Your Devcontainer

1. Open your project in VS Code
2. Press `F1` and select **"Dev Containers: Reopen in Container"**
3. Wait for the container to build
4. Verify everything works

## Customization Guide

### Python Version

To use a different Python version, change the Dockerfile:

```dockerfile
# Python 3.10
FROM python:3.10-bullseye

# Python 3.12
FROM python:3.12-bullseye
```

### Installing Python Packages

**Option 1: During Container Build (Recommended)**

Add to Dockerfile before `USER $USERNAME`:

```dockerfile
# Install Python packages
RUN python -m pip install \
    sphinx \
    pytest \
    ruff \
    mypy \
    your-package-here
```

**Option 2: After Container Creation**

Use `postCreateCommand` in `devcontainer.json`:

```json
"postCreateCommand": "pip install -e .[dev,docs,test]"
```

### Adding System Packages

Add to the Dockerfile `apt-get install` section:

```dockerfile
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git \
    your-package-here \
    another-package \
    && apt-get autoremove -y \
    && apt-get clean -y
```

### Adding VS Code Extensions

Add extension IDs to `devcontainer.json`:

```json
"extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-python.mypy-type-checker",
    "redhat.vscode-yaml",
    "eamodio.gitlens"
]
```

Find extension IDs by right-clicking on an extension in VS Code and selecting "Copy Extension ID".

### Port Forwarding

Forward additional ports:

```json
"forwardPorts": [8000, 3000, 5000]
```

### Environment Variables

Add environment variables to Dockerfile:

```dockerfile
ENV MY_VAR=value \
    ANOTHER_VAR=value
```

Or in `devcontainer.json`:

```json
"remoteEnv": {
    "MY_VAR": "value",
    "ANOTHER_VAR": "value"
}
```

### VS Code Settings

Customize VS Code settings in `devcontainer.json`:

```json
"settings": {
    "python.defaultInterpreterPath": "/usr/local/bin/python",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["-v"],
    "editor.rulers": [80, 100],
    "files.trimTrailingWhitespace": true,
    "[markdown]": {
        "editor.wordWrap": "on"
    }
}
```

## Complete Example: Documentation Project

Here's a complete devcontainer setup for a documentation project using Introligo:

### .devcontainer/Dockerfile

```dockerfile
FROM python:3.11-bullseye

# Install system dependencies including Doxygen
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git curl vim nano tree sudo \
    doxygen graphviz \
    build-essential gcc g++ make cmake \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Install documentation tools
RUN python -m pip install \
    sphinx>=4.0 \
    furo>=2023.3.27 \
    breathe>=4.0 \
    pytest>=7.0 \
    ruff>=0.1.0 \
    mypy>=1.0 \
    watchdog>=3.0 \
    PyYAML>=6.0 \
    Jinja2>=3.0

USER $USERNAME
WORKDIR /workspace

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

CMD ["/bin/bash"]
```

### .devcontainer/devcontainer.json

```json
{
    "name": "Documentation Project",
    "build": {
        "dockerfile": "Dockerfile",
        "context": ".."
    },

    "customizations": {
        "vscode": {
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.testing.pytestEnabled": true,
                "[python]": {
                    "editor.defaultFormatter": "charliermarsh.ruff",
                    "editor.formatOnSave": true,
                    "editor.codeActionsOnSave": {
                        "source.organizeImports": "explicit"
                    }
                },
                "[markdown]": {
                    "editor.wordWrap": "on",
                    "editor.quickSuggestions": false
                },
                "files.exclude": {
                    "**/__pycache__": true,
                    "**/*.pyc": true,
                    "**/.pytest_cache": true,
                    "**/docs/_build": true
                }
            },

            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "charliermarsh.ruff",
                "ms-python.mypy-type-checker",
                "redhat.vscode-yaml",
                "yzhang.markdown-all-in-one",
                "streetsidesoftware.code-spell-checker",
                "eamodio.gitlens"
            ]
        }
    },

    "forwardPorts": [8000],

    "postCreateCommand": "pip install -e .[dev,docs] && echo 'Setup complete!'",

    "remoteUser": "vscode",

    "workspaceMount": "source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=cached",
    "workspaceFolder": "/workspace",

    "features": {
        "ghcr.io/devcontainers/features/common-utils:2": {
            "installZsh": true,
            "installOhMyZsh": true,
            "upgradePackages": true
        },
        "ghcr.io/devcontainers/features/git:1": {
            "version": "latest",
            "ppa": true
        }
    }
}
```

## Advanced Configuration

### Multi-Stage Builds

Optimize build time with multi-stage Dockerfile:

```dockerfile
# Build stage
FROM python:3.11-bullseye AS builder

RUN python -m pip install --upgrade pip
COPY requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

# Runtime stage
FROM python:3.11-slim-bullseye

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Rest of your Dockerfile...
```

### Using Docker Compose

For complex setups with multiple services, create `.devcontainer/docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
    command: /bin/bash
    network_mode: service:db

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: password
```

Update `devcontainer.json`:

```json
{
    "name": "My Project",
    "dockerComposeFile": "docker-compose.yml",
    "service": "app",
    "workspaceFolder": "/workspace"
}
```

### Conditional Dependencies

Install dependencies based on project type:

```dockerfile
# Copy and check for requirements
COPY pyproject.toml* requirements.txt* /tmp/

# Install dependencies if they exist
RUN if [ -f /tmp/requirements.txt ]; then \
        pip install -r /tmp/requirements.txt; \
    elif [ -f /tmp/pyproject.toml ]; then \
        pip install /tmp/; \
    fi
```

### Lifecycle Scripts

Run scripts at different stages:

```json
{
    "initializeCommand": "echo 'Before container starts'",
    "onCreateCommand": "echo 'Container just created'",
    "updateContentCommand": "echo 'After git pull'",
    "postCreateCommand": "pip install -e .[dev]",
    "postStartCommand": "echo 'Container started'",
    "postAttachCommand": "echo 'Attached to container'"
}
```

## Best Practices

### 1. Keep Dockerfile Lean

- Only install necessary packages
- Clean up package manager caches
- Use multi-stage builds for complex setups
- Combine RUN commands to reduce layers

### 2. Version Control

Add to `.gitignore`:
```gitignore
# Don't ignore devcontainer config
!.devcontainer/
```

Commit your devcontainer configuration so team members can use it.

### 3. Documentation

Document your devcontainer setup in your README:

```markdown
## Development Setup

This project uses devcontainers for a consistent development environment.

1. Install Docker and VS Code with Dev Containers extension
2. Open project in VS Code
3. Click "Reopen in Container" when prompted
4. Wait for setup to complete

See [Devcontainer Documentation](docs/devcontainer_usage.md) for details.
```

### 4. Security

- Use specific image versions (not `latest`)
- Run as non-root user
- Don't store secrets in devcontainer files
- Keep base images updated

```dockerfile
# Good: Specific version
FROM python:3.11.6-bullseye

# Avoid: Latest tag
FROM python:latest
```

### 5. Performance

- Use bind mounts for source code
- Use volume mounts for node_modules, build artifacts
- Allocate sufficient Docker resources
- Use BuildKit for faster builds

### 6. Team Collaboration

- Document custom setup steps
- Keep configuration simple
- Test on different platforms
- Provide troubleshooting guide

## Testing Your Configuration

### Test Checklist

1. **Build**: Does the container build without errors?
2. **Extensions**: Are all VS Code extensions working?
3. **Dependencies**: Are all packages installed correctly?
4. **Ports**: Can you access forwarded ports?
5. **Git**: Does git work inside the container?
6. **Tests**: Do project tests run successfully?
7. **Build**: Does the project build/run correctly?

### Test Commands

```bash
# Inside the container
python --version
pip list
pytest
git status

# Build documentation (if applicable)
cd docs && python preview.py
```

## Troubleshooting

### Build Failures

**Problem**: Dockerfile build fails

**Solutions**:
- Check syntax errors in Dockerfile
- Verify package names are correct
- Check Docker daemon is running
- Try building with `--no-cache`

### Slow Builds

**Problem**: Container takes too long to build

**Solutions**:
- Use layer caching effectively
- Install only necessary packages
- Consider using pre-built base images
- Use `.dockerignore` file

### Extensions Not Installing

**Problem**: VS Code extensions fail to install

**Solutions**:
- Check extension IDs are correct
- Verify internet connectivity
- Check extension compatibility with remote development
- Try installing manually after container starts

### File Permission Issues

**Problem**: Files have wrong permissions

**Solutions**:
- Ensure UID/GID match your host user
- Run container as non-root user
- Check mount options in devcontainer.json

## Example: Minimal Python Project

For a simple Python project:

**.devcontainer/Dockerfile**:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

WORKDIR /workspace
```

**.devcontainer/devcontainer.json**:
```json
{
    "name": "Python Project",
    "build": {"dockerfile": "Dockerfile", "context": ".."},
    "customizations": {
        "vscode": {
            "extensions": ["ms-python.python", "charliermarsh.ruff"]
        }
    },
    "postCreateCommand": "pip install -e ."
}
```

## Additional Resources

- [Devcontainer Specification](https://containers.dev/)
- [VS Code Devcontainers Docs](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Templates](https://containers.dev/templates)
- [Dev Container Features](https://containers.dev/features)
- [Docker Documentation](https://docs.docker.com/)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)

## See Also

- [Running Code in Devcontainer](./devcontainer_usage.md) - How to use Introligo's devcontainer
- [Introligo Examples](./.devcontainer/) - Devcontainer configuration examples
