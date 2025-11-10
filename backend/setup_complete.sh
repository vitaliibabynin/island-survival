#!/bin/bash

# Island Survival - Complete Automated Setup Script for RunPod
# Run this with: curl -sSL https://raw.githubusercontent.com/vitaliibabynin/island-survival/main/backend/setup_complete.sh | bash

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Island Survival - RunPod Automated Setup                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if HuggingFace token is set
if [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "⚠️  HUGGINGFACE_TOKEN not set!"
    echo ""
    echo "Please set your HuggingFace token first:"
    echo "  export HUGGINGFACE_TOKEN=hf_your_token_here"
    echo ""
    echo "Get your token at: https://huggingface.co/settings/tokens"
    echo "Accept Flux.dev license: https://huggingface.co/black-forest-labs/FLUX.1-dev"
    exit 1
fi

echo "✓ HuggingFace token found"
echo ""

# Navigate to workspace
cd /workspace

# Check if repo already exists
if [ -d "island-survival" ]; then
    echo "📁 Repository exists, pulling latest changes..."
    cd island-survival
    git fetch origin
    git reset --hard origin/main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/vitaliibabynin/island-survival.git
    cd island-survival
fi

echo "✓ Repository ready"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Create directories
mkdir -p /workspace/island-survival/backend/generated_images
echo "✓ Directories created"
echo ""

# Check GPU
echo "🎮 GPU Information:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo ""

# All done
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Start the API server with:"
echo "   cd /workspace/island-survival/backend"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "📱 Your API will be available at:"
echo "   https://[your-pod-id]-8000.proxy.runpod.net"
echo ""
echo "🎨 Generate images automatically:"
echo "   python auto_generate.py --scenarios all --count 3"
echo ""
