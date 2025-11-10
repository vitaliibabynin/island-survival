#!/bin/bash

# Island Survival - One-Command Setup & Start
# Usage:
#   Method 1 (with RunPod env var): bash quickstart.sh
#   Method 2 (inline): HUGGINGFACE_TOKEN=hf_xxx bash quickstart.sh

set -e

echo "🏝️  Island Survival - Quick Start"
echo ""

# Check token
if [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "❌ Error: HUGGINGFACE_TOKEN not set"
    echo ""
    echo "Option 1 - Set in RunPod Dashboard (recommended):"
    echo "  1. Edit Pod → Environment Variables"
    echo "  2. Add: HUGGINGFACE_TOKEN=hf_your_token"
    echo "  3. Restart pod and run: bash quickstart.sh"
    echo ""
    echo "Option 2 - Pass inline (for current session):"
    echo "  HUGGINGFACE_TOKEN=hf_your_token bash quickstart.sh"
    echo ""
    echo "Get token: https://huggingface.co/settings/tokens"
    echo "Accept license: https://huggingface.co/black-forest-labs/FLUX.1-dev"
    echo ""
    exit 1
fi

echo "✅ HuggingFace token detected"
echo ""

# Setup
cd /workspace
if [ -d "island-survival" ]; then
    cd island-survival
    # Get current branch and pull
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    git pull origin "$CURRENT_BRANCH" || echo "⚠️  Git pull failed, continuing..."
else
    git clone https://github.com/vitaliibabynin/island-survival.git && cd island-survival
fi

cd backend
pip install --ignore-installed -q -r requirements.txt
mkdir -p /app/generated_images /app/generated_worlds

echo ""
echo "✅ Setup complete! Starting server..."
echo ""

# Try to detect RunPod URL from environment
if [ -n "$RUNPOD_POD_ID" ]; then
    export PUBLIC_URL="https://${RUNPOD_POD_ID}-8000.proxy.runpod.net"
    echo "🌐 Detected RunPod URL: $PUBLIC_URL"
else
    echo "📍 Find your API URL in RunPod dashboard:"
    echo "   Connect → HTTP Service [Port 8000]"
    echo ""
    echo "🌐 Add this URL to Vercel env variable:"
    echo "   NEXT_PUBLIC_API_URL=https://xxxxx-8000.proxy.runpod.net"
fi
echo ""

# Kill any existing Python processes to free memory
pkill -9 python 2>/dev/null || true
sleep 2

# Set PyTorch memory management flags
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_LAUNCH_BLOCKING=0

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
