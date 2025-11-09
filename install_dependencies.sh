#!/bin/bash
# Literary Name Analysis - Dependency Installation Script
# Use this script on macOS to install dependencies correctly

echo "=================================="
echo "Installing Dependencies for"
echo "Literary Name Analysis"
echo "=================================="
echo ""

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: python3 not found. Please install Python 3.9 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install packages
echo "📦 Installing Python packages..."
pip3 install --user spacy nltk

echo ""
echo "📥 Downloading spaCy language model..."
python3 -m spacy download en_core_web_sm

echo ""
echo "=================================="
echo "✅ Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Run analysis: python3 scripts/run_literary_name_analysis.py --mode new"
echo "  2. Start Flask: python3 app.py"
echo "  3. Visit: http://localhost:{port}/literary_name_composition"
echo ""

