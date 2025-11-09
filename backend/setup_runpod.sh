#!/bin/bash

# RunPod Setup Script
# Run this script when you first start your RunPod instance

echo "================================================"
echo "Island Survival - RunPod Setup"
echo "================================================"

# Update system
echo "Updating system packages..."
apt-get update
apt-get install -y git wget

# Clone repository
echo "Cloning repository..."
cd /workspace
git clone https://github.com/vitaliibabynin/island-survival.git
cd island-survival/backend

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p /app/generated_images
mkdir -p /app/models

# Set environment variables
echo ""
echo "================================================"
echo "IMPORTANT: Set these environment variables!"
echo "================================================"
echo "export HUGGINGFACE_TOKEN=your_token_here"
echo "export AWS_ACCESS_KEY_ID=your_key_here"
echo "export AWS_SECRET_ACCESS_KEY=your_secret_here"
echo "export S3_BUCKET_NAME=island-survival-images"
echo ""
echo "Or create a .env file with these values"
echo "================================================"

# Test installation
echo ""
echo "Testing Python installation..."
python3 --version
pip list | grep -E "(torch|diffusers|fastapi)"

echo ""
echo "================================================"
echo "Setup complete!"
echo "================================================"
echo ""
echo "To start the API server:"
echo "  cd /workspace/island-survival/backend"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "To generate images automatically:"
echo "  python auto_generate.py --scenarios all --count 2"
echo ""
echo "Your API will be available at:"
echo "  https://your-runpod-id.runpod.io"
echo "================================================"
