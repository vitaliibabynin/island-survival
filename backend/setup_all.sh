#!/bin/bash

# Island Survival - Complete One-Command Setup
# Installs Flux.dev + HunyuanWorld + Starts API Server
# Usage: HUGGINGFACE_TOKEN=hf_xxx bash setup_all.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Island Survival - Complete Setup                         ║"
echo "║  Flux.dev + HunyuanWorld + API Server                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check HuggingFace token
if [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "❌ Error: HUGGINGFACE_TOKEN not set"
    echo ""
    echo "Set in RunPod Dashboard:"
    echo "  Edit Pod → Environment Variables → Add HUGGINGFACE_TOKEN"
    echo ""
    echo "Or pass inline:"
    echo "  HUGGINGFACE_TOKEN=hf_xxx bash setup_all.sh"
    echo ""
    exit 1
fi

echo "✅ HuggingFace token detected"
echo ""

# ============================================================================
# Step 1: Clone/Update Island Survival Repository
# ============================================================================
echo "📦 Step 1/4: Setting up Island Survival..."
cd /workspace

if [ -d "island-survival" ]; then
    echo "  → Updating existing repository..."
    cd island-survival
    git pull origin main
else
    echo "  → Cloning repository..."
    git clone https://github.com/vitaliibabynin/island-survival.git
    cd island-survival
fi

cd backend

# ============================================================================
# Step 2: Install Flux.dev Dependencies
# ============================================================================
echo ""
echo "🎨 Step 2/4: Installing Flux.dev dependencies..."
pip install -q -r requirements.txt
mkdir -p /app/generated_images /app/generated_worlds

echo "✅ Flux.dev dependencies installed"

# ============================================================================
# Step 3: Install HunyuanWorld
# ============================================================================
echo ""
echo "🌍 Step 3/4: Installing HunyuanWorld-1.0..."
cd /workspace

if [ ! -d "HunyuanWorld-1.0" ]; then
    echo "  → Cloning HunyuanWorld repository..."
    git clone https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0.git
fi

cd HunyuanWorld-1.0

# Install Real-ESRGAN
if [ ! -d "Real-ESRGAN" ]; then
    echo "  → Installing Real-ESRGAN..."
    git clone https://github.com/xinntao/Real-ESRGAN.git
    cd Real-ESRGAN
    pip install -q basicsr facexlib gfpgan
    pip install -q -r requirements.txt
    python setup.py develop --quiet
    cd ..
fi

# Install ZIM
if [ ! -d "ZIM" ]; then
    echo "  → Installing ZIM..."
    git clone https://github.com/sail-sg/zim.git ZIM
    cd ZIM
    pip install -q -e .
    cd ..
fi

# Install HunyuanWorld requirements
echo "  → Installing HunyuanWorld dependencies..."
pip install -q -r requirements.txt
pip install -q DracoPy 2>/dev/null || true

echo "✅ HunyuanWorld installed"
echo ""
echo "📝 Note: HunyuanWorld models (~20GB) will download on first use"

# ============================================================================
# Step 4: Start API Server
# ============================================================================
echo ""
echo "🚀 Step 4/4: Starting API server..."
echo ""

cd /workspace/island-survival/backend

# Auto-detect RunPod URL
if [ -n "$RUNPOD_POD_ID" ]; then
    export PUBLIC_URL="https://${RUNPOD_POD_ID}-8000.proxy.runpod.net"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ Setup Complete!                                        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Your API URL: $PUBLIC_URL"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Add to Vercel Environment Variables:"
    echo "     NEXT_PUBLIC_API_URL=$PUBLIC_URL"
    echo ""
    echo "  2. API Endpoints:"
    echo "     Health: $PUBLIC_URL/api/health"
    echo "     Generate Panorama: $PUBLIC_URL/api/generate"
    echo "     Generate 3D World: $PUBLIC_URL/api/generate-3d"
    echo ""
    echo "🎮 GPU Info:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
else
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ Setup Complete!                                        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📍 Find your API URL in RunPod dashboard:"
    echo "   Connect → HTTP Service [Port 8000]"
    echo ""
fi

echo "🔥 Starting server (this will load Flux.dev model, ~5 min)..."
echo ""

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port 8000
