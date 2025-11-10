#!/bin/bash

# HunyuanWorld Installation Script for RunPod
# Run this once to install HunyuanWorld-1.0

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Installing HunyuanWorld-1.0 for 3D World Generation      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /workspace

# Clone HunyuanWorld repository
if [ ! -d "HunyuanWorld-1.0" ]; then
    echo "📥 Cloning HunyuanWorld-1.0..."
    git clone https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0.git
fi

cd HunyuanWorld-1.0

echo "📦 Installing dependencies..."

# Install Real-ESRGAN
if [ ! -d "Real-ESRGAN" ]; then
    git clone https://github.com/xinntao/Real-ESRGAN.git
    cd Real-ESRGAN
    pip install basicsr facexlib gfpgan
    pip install -r requirements.txt
    python setup.py develop
    cd ..
fi

# Install ZIM (Zero Initialization Module)
if [ ! -d "ZIM" ]; then
    git clone https://github.com/sail-sg/zim.git ZIM
    cd ZIM
    pip install -e .
    cd ..
fi

# Install other requirements
pip install -r requirements.txt

# Install Draco compression (optional but recommended)
pip install DracoPy

echo ""
echo "✅ HunyuanWorld-1.0 installed successfully!"
echo ""
echo "Note: Models will be downloaded automatically on first use (~20GB)"
echo ""
