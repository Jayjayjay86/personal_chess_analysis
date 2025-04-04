#!/bin/bash

# Chess Analysis App - Backend Setup Script
echo "Setting up Chess Analysis Backend..."

# Check for Python 3.8+
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo "Python 3.8 or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Stockfish
echo "Setting up Stockfish..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get install stockfish
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install stockfish
else
    echo "Please install Stockfish manually for your OS: https://stockfishchess.org/download/"
fi

# Verify Stockfish installation
if ! command -v stockfish &> /dev/null; then
    echo "Stockfish installation not found in PATH. Please ensure Stockfish is installed and available."
    exit 1
fi

# Initialize database
echo "Initializing database..."
python -c "from app import analyzer; analyzer._init_db()"

echo ""
echo "Backend setup complete!"
echo "To start the backend server:"
echo "  source venv/bin/activate"
echo "  python app.py"