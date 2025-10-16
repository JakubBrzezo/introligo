# Use Python 3.11 as base image (supports 3.8-3.12 per pyproject.toml)
FROM python:3.11-bullseye

# Install system dependencies including Doxygen for C++ documentation support
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Development tools
    git \
    curl \
    wget \
    vim \
    nano \
    less \
    # Build tools for C++ projects
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # Doxygen for C++ documentation (breathe dependency)
    doxygen \
    graphviz \
    # Additional utilities
    tree \
    sudo \
    zsh \
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

# Upgrade pip and install common Python development tools
RUN python -m pip install --upgrade pip setuptools wheel

# Copy pyproject.toml to install dependencies
COPY pyproject.toml /tmp/pyproject.toml

# Install project dependencies (as root to install system-wide)
RUN python -m pip install \
    "sphinx>=4.0" \
    "furo>=2023.3.27" \
    "breathe>=4.0" \
    "pytest>=7.0" \
    "ruff>=0.1.0" \
    "mypy>=1.0" \
    "watchdog>=3.0" \
    "pytest-cov" \
    "coverage" \
    "PyYAML>=6.0" \
    "Jinja2>=3.0"

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
