#!/bin/bash

# Chess Analysis App - Frontend Setup Script
echo "Setting up Chess Analysis Frontend..."

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js could not be found. Please install Node.js 14 or higher."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2)
MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)

if [ "$MAJOR_VERSION" -lt 14 ]; then
    echo "Node.js 14 or higher is required. Found Node.js $NODE_VERSION"
    exit 1
fi

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Build the frontend
echo "Building frontend..."
npm run build

echo ""
echo "Frontend setup complete!"
echo "To start the development server:"
echo "  npm start"