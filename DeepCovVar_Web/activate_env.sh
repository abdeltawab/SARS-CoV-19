#!/bin/bash
# Activation script for the deepcovvar_web virtual environment

echo "Activating deepcovvar_web virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "To run the application:"
echo "  python src/main.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
