# RunPod One-Command Setup

## Disk Space Requirements

**Minimum**: 60GB Container Disk
**Recommended**: 80-100GB Container Disk

**Breakdown**:
- Flux.dev model: ~24GB
- HunyuanWorld models: ~20GB (downloads on first use)
- Dependencies (Python packages, Real-ESRGAN, ZIM): ~5GB
- Generated panoramas: ~5-10MB each
- Generated 3D worlds (.glb files): ~50-200MB each
- System/temp files: ~5-10GB buffer

**Important**: This is the **Container Disk** size, NOT the Volume Disk.

---

## Step-by-Step RunPod Setup

### 1. Create New Pod

Go to [RunPod Console](https://www.runpod.io/console/pods) and click **Deploy**

### 2. Select GPU Template

**GPU Options** (choose one):

| GPU | VRAM | Best For | Hourly Cost (est.) |
|-----|------|----------|-------------------|
| **RTX 5090** | 32GB | Good - can run both with memory management | ~$0.50-0.70/hr |
| **2x RTX 5090** | 64GB | Best - comfortable operation, no memory issues | ~$1.00-1.40/hr |
| RTX 4090 | 24GB | Minimum - Flux only, tight on memory | ~$0.40-0.60/hr |
| 2x RTX 4090 | 48GB | Good - works but less headroom than 5090s | ~$0.80-1.20/hr |

**Recommendation**: Start with **1x RTX 5090** (32GB). Upgrade to 2x if you get OOM errors during 3D generation.

### 3. Configure Container

**Template**: Select `RunPod Pytorch 2.4.0` or `RunPod Pytorch` (latest)

**Container Disk**: Set to **80GB** (or minimum 60GB)
- This is the main storage for models and dependencies
- NOT the Volume Disk (you don't need a persistent volume for this)

**Expose HTTP Ports**: Add `8000`
- Click **Expose HTTP Ports [Comma Separated]**
- Enter: `8000`
- This exposes the API server

### 4. Set Environment Variables

Click **Environment Variables** and add:

| Variable | Value |
|----------|-------|
| `HUGGINGFACE_TOKEN` | `hf_your_token_here` |

To get HuggingFace token:
1. Go to https://huggingface.co/settings/tokens
2. Create new token (or use existing)
3. Copy and paste into RunPod

### 5. Deploy Pod

**Start Type**: Select **On-Demand** (cheaper, but can be interrupted)
- Alternative: **Secure Cloud** (more expensive, guaranteed availability)

Click **Deploy On-Demand** (or **Secure Cloud**)

### 6. Wait for Pod to Start

You'll see status change from "Pending" → "Running"

Once running, you'll have access to:
- **Web Terminal** (for running commands)
- **Connect** button (shows your HTTP Service URL)

---

## One-Command Setup

### 7. Run Setup Script

Once your pod is running, click **Connect** → **Start Web Terminal**

Then paste and run this command:

```bash
curl -sSL https://raw.githubusercontent.com/vitaliibabynin/island-survival/main/backend/setup_all.sh | bash
```

**What this script does**:
1. Clones the Island Survival repository to `/workspace`
2. Installs Flux.dev dependencies (PyTorch, diffusers, transformers)
3. Installs HunyuanWorld with Real-ESRGAN and ZIM
4. Downloads Flux.dev model (~24GB, ~5-7 minutes)
5. Creates directories for generated images and worlds
6. Auto-detects your RunPod Pod ID and sets PUBLIC_URL
7. Starts the FastAPI server on port 8000

**Installation Time**:
- First-time setup: ~10-15 minutes
- Flux.dev model download: ~5-7 minutes (24GB)
- HunyuanWorld models: Download on first 3D generation (~20GB, ~10 minutes)

---

## After Setup Completes

### 8. Get Your API URL

When the setup completes successfully, you'll see:

```
╔════════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                        ║
╚════════════════════════════════════════════════════════════╝

🌐 Your API URL: https://your-pod-id-8000.proxy.runpod.net

📋 Next Steps:
  1. Add to Vercel Environment Variables:
     NEXT_PUBLIC_API_URL=https://your-pod-id-8000.proxy.runpod.net

  2. API Endpoints:
     Health: https://your-pod-id-8000.proxy.runpod.net/api/health
     Generate Panorama: /api/generate
     Generate 3D World: /api/generate-3d

🎮 GPU Info:
NVIDIA GeForce RTX 5090, 32768 MiB

🔥 Starting server (this will load Flux.dev model, ~5 min)...
```

**Copy your API URL** - you'll need it for Vercel!

### 9. Add API URL to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your **island-survival** project
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-pod-id-8000.proxy.runpod.net` (paste your URL)
   - **Environment**: Check all (Production, Preview, Development)
5. Click **Save**
6. Go to **Deployments** → Click ⋯ on latest deployment → **Redeploy**

Your Vercel app will now connect to your RunPod API!

## Troubleshooting

**If script fails on HUGGINGFACE_TOKEN**:
```bash
# Check if env var is set
echo $HUGGINGFACE_TOKEN

# If empty, set it and retry
export HUGGINGFACE_TOKEN=hf_your_token_here
curl -sSL https://raw.githubusercontent.com/vitaliibabynin/island-survival/main/backend/setup_all.sh | bash
```

**To restart server later** (without reinstalling):
```bash
cd /workspace/island-survival/backend
bash quickstart.sh
```

**If you get out of memory errors during 3D generation**:
- Your GPU doesn't have enough VRAM
- Upgrade to 2x RTX 5090 or 2x RTX 4090
- Or only generate panoramas (Flux works fine on single 5090)

**Server not accessible**:
- Check port 8000 is exposed: Edit Pod → Expose HTTP Ports → `8000`
- Verify API URL format: `https://PODID-8000.proxy.runpod.net` (no trailing slash)
- Test in browser: Visit `https://your-pod-id-8000.proxy.runpod.net/api/health`

---

## Quick Reference

**Container Disk**: 80GB minimum
**GPU**: RTX 5090 (32GB) or 2x RTX 5090 (64GB)
**Port**: 8000 (HTTP)
**Env Var**: `HUGGINGFACE_TOKEN=hf_xxx`
**Setup Command**: `curl -sSL https://raw.githubusercontent.com/vitaliibabynin/island-survival/main/backend/setup_all.sh | bash`
**API URL Format**: `https://PODID-8000.proxy.runpod.net`
**Cost**: ~$0.50-0.70/hr (1x 5090) or ~$1.00-1.40/hr (2x 5090)
