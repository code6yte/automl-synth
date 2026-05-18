#!/usr/bin/env bash
set -e

echo "========================================"
echo "  AutoML-Synth Installer"
echo "========================================"

echo ""
echo "Checking Python version..."
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_major=3
required_minor=11

major=$(echo "$python_version" | cut -d. -f1)
minor=$(echo "$python_version" | cut -d. -f2)

if [ "$major" -lt "$required_major" ] || { [ "$major" -eq "$required_major" ] && [ "$minor" -lt "$required_minor" ]; }; then
    echo "ERROR: Python 3.11+ required (found $python_version)"
    exit 1
fi
echo "  Python $python_version [OK]"

echo ""
echo "Checking for pipx..."
if ! command -v pipx &> /dev/null; then
    echo "  pipx not found. Installing..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
fi
echo "  pipx [OK]"

echo ""
echo "Installing AutoML-Synth..."
pipx install .
echo "  Installation complete"

echo ""
echo "Verifying installation..."
automl-synth doctor

echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Set up your .env file:"
echo "     cp .env.example ~/.config/automl-synth/.env"
echo "     # Edit with your LLM_API_KEY"
echo ""
echo "  2. Generate a dataset:"
echo "     automl-synth generate --topic 'movie reviews' --rows 300"
echo ""
echo "  3. Start the dashboard:"
echo "     automl-synth serve"
echo ""
