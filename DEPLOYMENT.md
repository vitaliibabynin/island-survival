# Deployment Guide

Step-by-step guide to deploy Island Survival to production.

## 📋 Prerequisites

### 1. Get a HuggingFace Token

1. Go to [HuggingFace](https://huggingface.co/settings/tokens)
2. Create a new token with "Read" access
3. Accept the Flux.dev model license at [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)

### 2. Create Accounts

- [Vercel](https://vercel.com) - Free tier
- [RunPod](https://runpod.io) - Add $10-20 credit
- [AWS](https://aws.amazon.com) - Optional, for S3 storage

## 🚀 Part 1: Deploy Backend (RunPod)

### Step 1: Create RunPod Instance

1. **Login to RunPod**
   - Go to [runpod.io](https://runpod.io)
   - Click "Deploy" → "GPU Instances"

2. **Select GPU**
   - Choose: RTX 4090 (24GB) - **Recommended** ($0.34/hr)
   - Or: A6000 (48GB) - More VRAM ($0.79/hr)
   - Or: A100 (40GB) - Fastest ($1.10/hr)

3. **Select Template**
   - Choose "PyTorch 2.1" or "RunPod Pytorch"
   - Or use "Ubuntu 22.04 LTS + CUDA 12.1"

4. **Configure Storage**
   - Container Disk: 50GB
   - Volume Disk: 100GB (optional but recommended)

5. **Deploy**
   - Click "Deploy On-Demand" or "Deploy Spot" (cheaper but can be interrupted)
   - Wait for instance to start

### Step 2: Setup Backend Code

1. **Connect to Instance**

   ```bash
   # Click "Connect" → "Start Web Terminal" in RunPod
   # Or use SSH
   ```

2. **Clone Repository**

   ```bash
   cd /workspace
   git clone https://github.com/vitaliibabynin/island-survival.git
   cd island-survival/backend
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**

   ```bash
   # Create .env file
   cat > .env << EOF
   HUGGINGFACE_TOKEN=hf_your_token_here
   EOF

   # Or export directly
   export HUGGINGFACE_TOKEN=hf_your_token_here
   ```

5. **Test Model Loading**

   ```bash
   python3 -c "from image_generator import FluxPanoramaGenerator; gen = FluxPanoramaGenerator()"
   ```

   This will take 5-10 minutes first time (downloads ~40GB model)

### Step 3: Start API Server

1. **Start Server**

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Expose Port**

   - In RunPod dashboard, click "Connect"
   - Find "HTTP Service [Port 8000]"
   - Copy the public URL (e.g., `https://xxxxx-8000.proxy.runpod.net`)

3. **Test API**

   ```bash
   curl https://your-runpod-url/api/health
   ```

   Should return: `{"status":"healthy","model_loaded":true}`

### Step 4: Keep Server Running

**Option A: Use screen (simple)**

```bash
screen -S api
uvicorn main:app --host 0.0.0.0 --port 8000
# Press Ctrl+A then D to detach
# Reconnect with: screen -r api
```

**Option B: Use systemd (persistent)**

```bash
# Create service file
sudo cat > /etc/systemd/system/island-survival.service << EOF
[Unit]
Description=Island Survival API
After=network.target

[Service]
User=root
WorkingDirectory=/workspace/island-survival/backend
Environment="HUGGINGFACE_TOKEN=hf_your_token_here"
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl enable island-survival
sudo systemctl start island-survival
sudo systemctl status island-survival
```

## 🌐 Part 2: Deploy Frontend (Vercel)

### Step 1: Push to GitHub

```bash
# In your local repository
git add .
git commit -m "Setup Island Survival project"
git push origin main
```

### Step 2: Deploy to Vercel

**Option A: Vercel Dashboard (Easiest)**

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `./`
   - Build Command: `npm run build`
   - Output Directory: `.next`
5. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = Your RunPod URL
6. Click "Deploy"

**Option B: Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL
# Enter your RunPod URL

# Deploy to production
vercel --prod
```

### Step 3: Test Deployment

1. Visit your Vercel URL
2. Select a scenario
3. Click "Generate"
4. Wait 1-2 minutes
5. Panorama should load!

## 🔧 Part 3: Optional Setup

### Setup AWS S3 Storage

1. **Create S3 Bucket**

   ```bash
   aws s3 mb s3://island-survival-images
   ```

2. **Configure Bucket Policy**

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicRead",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::island-survival-images/*"
       }
     ]
   }
   ```

3. **Add to RunPod Environment**

   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export S3_BUCKET_NAME=island-survival-images
   export S3_REGION=us-east-1
   ```

4. **Restart API Server**

### Setup Automated Generation

1. **Create Generation Script**

   ```bash
   # On RunPod
   cd /workspace/island-survival/backend

   # Generate batch
   python auto_generate.py --scenarios all --count 2
   ```

2. **Schedule with Cron** (optional)

   ```bash
   # Generate 1 random image every hour
   crontab -e

   # Add line:
   0 * * * * cd /workspace/island-survival/backend && python auto_generate.py --scenarios random --count 1
   ```

## 📊 Cost Breakdown

### Minimal Setup (Testing)

- **RunPod RTX 4090**: $0.34/hr × 2 hours = **$0.68**
- **Vercel**: Free (Hobby plan)
- **Total**: **$0.68** for 2 hours testing

### Regular Use (10 hours/month)

- **RunPod RTX 4090**: $0.34/hr × 10 hours = **$3.40**
- **Vercel**: Free
- **S3 Storage** (100 images): ~$0.10
- **Total**: **~$3.50/month**

### Heavy Use (100 hours/month)

- **RunPod RTX 4090**: $0.34/hr × 100 hours = **$34.00**
- **Vercel Pro**: $20/month
- **S3 Storage** (1000 images): ~$1.00
- **Total**: **~$55/month**

## 💡 Tips

### Save Money

1. **Use Spot Instances** on RunPod (70% cheaper, can be interrupted)
2. **Stop instances** when not generating
3. **Use Vercel Free Tier** for personal projects
4. **Local storage** instead of S3 for testing

### Improve Performance

1. **Use A100 GPU** for faster generation
2. **Enable model caching** (automatic after first load)
3. **Batch generate** overnight for efficiency
4. **Use CDN** for S3 images (CloudFront)

### Monitor Costs

1. **RunPod Dashboard**: Shows running time and costs
2. **Vercel Analytics**: Monitor bandwidth usage
3. **AWS Cost Explorer**: Track S3 costs
4. **Set billing alerts** in all services

## 🐛 Troubleshooting

### Backend Issues

**"Model won't load"**
- Check HuggingFace token is set
- Verify you accepted Flux.dev license
- Check disk space: `df -h`

**"CUDA out of memory"**
- Use larger GPU (A6000 or A100)
- Or enable CPU offload in `image_generator.py`

**"Server keeps crashing"**
- Check logs: `journalctl -u island-survival -f`
- Increase swap space
- Use systemd for auto-restart

### Frontend Issues

**"Can't connect to API"**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check RunPod port 8000 is exposed
- Test with: `curl $NEXT_PUBLIC_API_URL/api/health`

**"CORS errors"**
- Add your Vercel domain to CORS in `main.py`
- Restart API server

**"Build fails on Vercel"**
- Check `package.json` dependencies
- Verify Node.js version (18+)
- Check build logs in Vercel dashboard

## ✅ Post-Deployment Checklist

- [ ] Backend API is running on RunPod
- [ ] API health check returns `{"status":"healthy"}`
- [ ] Frontend is deployed on Vercel
- [ ] Environment variable `NEXT_PUBLIC_API_URL` is set
- [ ] Can generate images from web interface
- [ ] Images are loading in panorama viewer
- [ ] Storage is configured (S3 or local)
- [ ] Costs are monitored
- [ ] Auto-restart is configured (systemd or screen)

## 🎉 Success!

Your Island Survival app is now live!

**Next Steps:**
1. Generate some panoramas
2. Share your Vercel URL with friends
3. Customize scenarios in `prompt_generator.py`
4. Add new features!

**Questions?** Check the main [README.md](README.md) or open an issue.
