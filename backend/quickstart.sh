#!/bin/bash

# Island Survival - One-Command Setup & Start
# Usage: HUGGINGFACE_TOKEN=hf_xxx bash quickstart.sh

set -e

echo "🏝️  Island Survival - Quick Start"
echo ""

# Check token
if [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "❌ Error: HUGGINGFACE_TOKEN not set"
    echo ""
    echo "Run this script like:"
    echo "  HUGGINGFACE_TOKEN=hf_your_token bash quickstart.sh"
    echo ""
    exit 1
fi

# Setup
cd /workspace
if [ -d "island-survival" ]; then
    cd island-survival && git pull origin main
else
    git clone https://github.com/vitaliibabynin/island-survival.git && cd island-survival
fi

cd backend
pip install -q -r requirements.txt
mkdir -p generated_images

echo ""
echo "✅ Setup complete! Starting server..."
echo ""
echo "📍 Find your API URL in RunPod dashboard:"
echo "   Connect → HTTP Service [Port 8000]"
echo ""
echo "🌐 Add this URL to Vercel env variable:"
echo "   NEXT_PUBLIC_API_URL=https://xxxxx-8000.proxy.runpod.net"
echo ""

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
