#!/bin/bash

echo "Creating Python virtual environment..."

# Set variables
VENV_NAME="venv"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJ_ROOT="$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in PATH"
    echo "Please install Python and try again"
    exit 1
fi

# Check if virtual environment already exists
if [ -d "$PROJ_ROOT/$VENV_NAME" ]; then
    echo "Virtual environment already exists at $PROJ_ROOT/$VENV_NAME"
    echo "To recreate it, please delete the existing one first"
    exit 0
fi

# Create virtual environment
echo "Creating virtual environment in $PROJ_ROOT/$VENV_NAME"
python3 -m venv "$PROJ_ROOT/$VENV_NAME"
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

# Activation instructions
echo "Virtual environment created successfully"
echo ""
echo "You can activate it by running:"
echo "source $PROJ_ROOT/$VENV_NAME/bin/activate"
echo ""
echo "If you have a requirements.txt file, you can install dependencies with:"
echo "pip install -r requirements.txt"

exit 0