#!/bin/bash

# AI Competitor Intelligence Tracker - Setup Script
# This script sets up the development environment

echo "=========================================="
echo "AI Competitor Intelligence Tracker Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created. Please edit it with your configuration."
else
    echo ".env file already exists."
fi

# Create necessary directories
echo ""
echo "Ensuring data directories exist..."
mkdir -p data/raw data/processed data/reports logs

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To get started:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Edit .env file with your settings (optional)"
echo "  3. Edit config/config.yaml to customize sources (optional)"
echo "  4. Run the tracker: python src/main.py"
echo "  5. Run with dashboard: python src/main.py --dashboard"
echo ""
echo "For more information, see README.md"
echo ""
