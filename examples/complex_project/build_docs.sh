#!/bin/bash
# Build script for Smart Door Driver documentation
# This script runs Doxygen first, then uses preview.py to build and serve the docs

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Building Smart Door Driver Documentation"
echo "============================================="
echo ""

# Step 1: Run Doxygen
echo "▶ Step 1: Running Doxygen to generate C++ API documentation..."
cd "$SCRIPT_DIR"
if ! command -v doxygen &> /dev/null; then
    echo "⛔ Error: Doxygen is not installed"
    echo "   Install with: sudo apt-get install doxygen graphviz"
    exit 1
fi

doxygen Doxyfile
echo "✅ Doxygen XML files generated in output/xml"
echo ""

# Step 2: Run preview.py with the complex_project example
echo "▶ Step 2: Building Sphinx documentation with Introligo..."
cd "$PROJECT_ROOT/docs"

if [ "$1" == "--no-serve" ]; then
    python3 preview.py --example complex_project --no-serve
else
    echo "📝 Starting documentation server (Press Ctrl+C to stop)"
    python3 preview.py --example complex_project
fi
