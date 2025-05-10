#!/bin/bash

echo "Activating Python virtual environment..."

# Set variables
VENV_NAME="venv"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJ_ROOT="$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "$PROJ_ROOT/$VENV_NAME" ]; then
    echo "Virtual environment not found at $PROJ_ROOT/$VENV_NAME"
    echo "Please create it first using ./create_venv.sh"
    exit 1
fi

# Inform the user how to activate the environment
echo ""
echo "To activate the virtual environment, you need to source this script:"
echo ""
echo "    source ./activate_venv.sh"
echo ""
echo "Simply running it won't work. This is because the activation needs to"
echo "modify your current shell session, which can only be done with source."
echo ""

# Check if the script is being sourced
# https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script was executed instead of being sourced."
    echo "Please use 'source ./activate_venv.sh' instead."
    exit 1
fi

# Activate the virtual environment
source "$PROJ_ROOT/$VENV_NAME/bin/activate"

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    return 1
fi

echo "Virtual environment activated successfully"
echo ""
echo "You can now run Python commands with the virtual environment"
echo "To deactivate, type 'deactivate'"