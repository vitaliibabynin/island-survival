#!/bin/bash

# Island Survival - Complete One-Command Setup
# Installs Flux.dev + HunyuanWorld + Starts API Server
# Usage: HUGGINGFACE_TOKEN=hf_xxx bash setup_all.sh

set -e

# Configure git to never prompt for credentials (for public repos)
git config --global credential.helper '!f() { :; }; f'
git config --global core.askPass ""
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/echo

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
    echo "  → Using existing repository..."
    cd island-survival
    # Get current branch name
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "  → Current branch: $CURRENT_BRANCH"
    git pull origin "$CURRENT_BRANCH" || {
        echo "  ℹ️  Git pull failed, continuing with existing code..."
    }
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
    git clone https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0.git 2>/dev/null || {
        echo "  ⚠️  Warning: Failed to clone HunyuanWorld"
        echo "  ℹ️  You can still use Flux.dev for panorama generation"
        echo "  ℹ️  3D world generation will not be available"
    }
fi

# Only install HunyuanWorld dependencies if directory exists
if [ -d "HunyuanWorld-1.0" ]; then
    cd HunyuanWorld-1.0

    # Install Real-ESRGAN
    if [ ! -d "Real-ESRGAN" ]; then
        echo "  → Installing Real-ESRGAN..."
        git clone https://github.com/xinntao/Real-ESRGAN.git 2>/dev/null || {
            echo "  ⚠️  Warning: Failed to clone Real-ESRGAN, continuing..."
        }
        if [ -d "Real-ESRGAN" ]; then
            cd Real-ESRGAN
            pip install -q basicsr-fixed facexlib gfpgan 2>/dev/null || true
            pip install -q -r requirements.txt 2>/dev/null || true
            python setup.py develop --quiet 2>/dev/null || true
            cd ..
        fi
    fi

    # Install ZIM (semantic segmentation support)
    if [ ! -d "ZIM" ]; then
        echo "  → Installing ZIM..."
        git clone https://github.com/naver-ai/ZIM.git ZIM 2>/dev/null || {
            echo "  ⚠️  Warning: Failed to clone ZIM repository"
            echo "  ℹ️  Semantic segmentation may be limited"
        }
        if [ -d "ZIM" ]; then
            cd ZIM
            pip install -q -e . 2>/dev/null || echo "  ⚠️  ZIM installation failed, continuing..."

            # Download ZIM checkpoint files
            if [ ! -d "zim_vit_l_2092" ]; then
                echo "  → Downloading ZIM model checkpoints..."
                mkdir -p zim_vit_l_2092
                cd zim_vit_l_2092
                wget -q https://huggingface.co/naver-iv/zim-anything-vitl/resolve/main/zim_vit_l_2092/encoder.onnx 2>/dev/null || echo "  ⚠️  Failed to download encoder.onnx"
                wget -q https://huggingface.co/naver-iv/zim-anything-vitl/resolve/main/zim_vit_l_2092/decoder.onnx 2>/dev/null || echo "  ⚠️  Failed to download decoder.onnx"
                cd ..
            fi
            cd ..
        fi
    fi

    # Install HunyuanWorld requirements
    echo "  → Installing HunyuanWorld dependencies..."
    pip install -q -r requirements.txt 2>/dev/null || true
    pip install -q open3d 2>/dev/null || echo "  ⚠️  Warning: open3d installation failed"
    pip install -q DracoPy 2>/dev/null || true

    # Install git-based dependencies (required by HunyuanWorld)
    # Note: MoGe installs its own compatible version of utils3d, so install MoGe first
    echo "  → Installing MoGe from Microsoft (includes utils3d 1.3)..."
    pip install -q git+https://github.com/microsoft/MoGe.git 2>/dev/null || echo "  ⚠️  Warning: MoGe installation failed"

    echo "  → Installing ioPath (required for PyTorch3D)..."
    pip install -q iopath 2>/dev/null || true

    echo "  → Installing PyTorch3D from Facebook Research (may take several minutes)..."
    pip install -q "git+https://github.com/facebookresearch/pytorch3d.git@stable" 2>/dev/null || {
        echo "  ⚠️  Warning: PyTorch3D installation failed (build from source)"
        echo "  ℹ️  Continuing without PyTorch3D - 3D generation may have limited features"
    }

    echo "✅ HunyuanWorld installed"
    echo ""
    echo "📝 Note: HunyuanWorld models (~20GB) will download on first use"
else
    echo "⚠️  Skipping HunyuanWorld installation (clone failed)"
    echo "ℹ️  Panorama generation will still work with Flux.dev"
fi

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
