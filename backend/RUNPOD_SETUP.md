# RunPod One-Command Setup

## Prerequisites
1. Create RunPod instance with **RTX 5090** (32GB) or **2x RTX 5090** (64GB)
2. Set environment variable in RunPod dashboard:
   - Go to **Edit Pod** → **Environment Variables**
   - Add: `HUGGINGFACE_TOKEN` = `hf_your_token_here`
3. Expose port **8000** in RunPod:
   - **Edit Pod** → **Expose HTTP Ports** → Add `8000`

## One-Command Setup

Open RunPod Web Terminal and run:

```bash
curl -sSL https://raw.githubusercontent.com/vitaliibabynin/island-survival/main/backend/setup_all.sh | bash
```

That's it! The script will:
- Clone the repository
- Install Flux.dev dependencies
- Install HunyuanWorld with Real-ESRGAN and ZIM
- Create necessary directories
- Auto-detect your RunPod URL
- Start the API server

## What Gets Installed

**Disk Space Required**: ~40GB total
- Flux.dev model: ~24GB
- HunyuanWorld models: ~20GB (downloads on first use)
- Dependencies: ~5GB

**Time**: ~10-15 minutes
- Setup: 5-7 minutes
- First model load: 5-8 minutes

## After Setup Completes

You'll see output like:
```
╔════════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                        ║
╚════════════════════════════════════════════════════════════╝

🌐 Your API URL: https://your-pod-id-8000.proxy.runpod.net

📋 Next Steps:
  1. Add to Vercel Environment Variables:
     NEXT_PUBLIC_API_URL=https://your-pod-id-8000.proxy.runpod.net
```

Copy the API URL and add it to Vercel's environment variables.

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
