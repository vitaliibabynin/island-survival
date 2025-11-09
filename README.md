# Island Survival - 360° Panoramic Experience

Generate and explore immersive 360° panoramic survival scenarios using Flux.dev AI.

## 🌴 Features

- **AI-Generated Panoramas**: High-quality 360° equirectangular images using Flux.dev
- **Interactive Viewer**: Drag-to-look panorama viewer in the browser
- **Multiple Scenarios**: Beach, jungle, mountain, cave, ruins, storm, sunset, and night scenes
- **Cloud GPU**: Runs on RunPod with 24GB VRAM GPUs (RTX 4090, A6000, A100)
- **Automated Generation**: Batch generate multiple scenarios automatically
- **Web Interface**: Beautiful Next.js frontend deployed on Vercel

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│  Frontend (Vercel)                              │
│  - Next.js 14 + TypeScript                     │
│  - Tailwind CSS                                 │
│  - 360° Panorama Viewer                         │
└─────────────┬───────────────────────────────────┘
              │ API Calls
              ↓
┌─────────────────────────────────────────────────┐
│  Backend (RunPod)                               │
│  - FastAPI                                      │
│  - Flux.dev (24GB model)                        │
│  - PyTorch + CUDA                               │
└─────────────┬───────────────────────────────────┘
              │ Storage
              ↓
┌─────────────────────────────────────────────────┐
│  Storage (S3 or Local)                          │
│  - Generated panoramas                          │
│  - Metadata JSON                                │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: Full Setup (Frontend + Backend)

#### 1. Deploy Frontend to Vercel

```bash
# Push to GitHub
git add .
git commit -m "Initial setup"
git push

# Deploy to Vercel (via Vercel dashboard or CLI)
npm i -g vercel
vercel --prod
```

Set environment variable in Vercel:
- `NEXT_PUBLIC_API_URL` = Your RunPod URL (e.g., `https://xxxxx-8000.proxy.runpod.net`)

#### 2. Setup Backend on RunPod

1. **Create RunPod Instance**
   - Go to [RunPod.io](https://runpod.io)
   - Select GPU: RTX 4090 (24GB) or A6000 (48GB)
   - Choose "PyTorch" template or "Ubuntu + CUDA"
   - Set disk space: 100GB+

2. **SSH into RunPod and run setup**

```bash
# Clone repository
git clone https://github.com/vitaliibabynin/island-survival.git
cd island-survival/backend

# Run setup script
chmod +x setup_runpod.sh
./setup_runpod.sh

# Set environment variables
export HUGGINGFACE_TOKEN=hf_your_token_here

# Optional: Set AWS credentials for S3 storage
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export S3_BUCKET_NAME=island-survival-images

# Start API server
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. **Expose RunPod Port**
   - In RunPod dashboard, click "Connect" → "HTTP Service"
   - Note your public URL (e.g., `https://xxxxx-8000.proxy.runpod.net`)
   - Update Vercel environment variable with this URL

### Option 2: Automated Batch Generation

Generate panoramas without the frontend:

```bash
# Generate all scenarios (1 per scenario)
python auto_generate.py --scenarios all --count 1

# Generate specific scenarios (2 each)
python auto_generate.py --scenarios beach,jungle,mountain --count 2

# Generate random scenarios (5 images)
python auto_generate.py --scenarios random --count 5
```

Generated images are saved to `/app/generated_images/` with metadata in `metadata.json`.

## 📋 Requirements

### Frontend
- Node.js 18+
- npm or yarn

### Backend
- Python 3.11+
- CUDA 12.1+
- GPU with 24GB+ VRAM
- 100GB+ disk space (for models and images)

## 🎮 Usage

### Web Interface

1. Visit your Vercel URL
2. Select a scenario (or random)
3. Click "Generate"
4. Wait 1-2 minutes for generation
5. Drag to explore the 360° panorama
6. Browse gallery of generated scenes

### API Endpoints

```bash
# Health check
GET /api/health

# Generate image
POST /api/generate
{
  "scenario": "beach",
  "custom_prompt": "optional custom prompt"
}

# Get all images
GET /api/images

# Get specific image
GET /api/images/{image_id}

# Delete image
DELETE /api/images/{image_id}
```

## 🔧 Configuration

### Frontend Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://your-runpod-url.com
```

### Backend Environment Variables

Create `backend/.env`:

```bash
# Required
HUGGINGFACE_TOKEN=hf_your_token_here

# Optional (for S3 storage)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=island-survival-images
S3_REGION=us-east-1
```

## 💰 Cost Estimates

### RunPod GPU Pricing
- **RTX 4090**: ~$0.34/hour
- **A6000 (48GB)**: ~$0.79/hour
- **A100 (40GB)**: ~$1.10/hour

### Generation Time
- ~1-2 minutes per 2048x1024 panorama
- ~30 images per hour possible

### Storage
- ~3-10MB per panorama (PNG)
- 100GB = ~10,000-30,000 images

### Vercel
- **Hobby plan**: Free for personal projects
- **Pro plan**: $20/month if needed

**Example cost for testing**:
- 2 hours of RTX 4090: $0.68
- Generate ~60 panoramas
- Vercel: Free

## 🎨 Customization

### Add New Scenarios

Edit `backend/prompt_generator.py`:

```python
self.scenarios["underwater"] = [
    "underwater coral reef, tropical fish, clear water, sunlight filtering through",
    "deep ocean scene, mysterious creatures, blue ambient light",
]
```

### Adjust Image Quality

Edit generation parameters in `backend/image_generator.py`:

```python
# Higher quality (slower)
width=4096, height=2048, num_inference_steps=100

# Faster (lower quality)
width=1024, height=512, num_inference_steps=30
```

### Change Panorama Viewer

Customize `components/PanoramaViewer.tsx` for:
- Auto-rotation speed
- Zoom controls
- VR mode
- Full 360° sphere projection

## 🐛 Troubleshooting

### "CUDA out of memory"
- Reduce image size in `image_generator.py`
- Enable `pipe.enable_model_cpu_offload()`
- Use A100 (40GB) or A6000 (48GB) GPU

### "Model loading failed"
- Verify HuggingFace token is set
- Check Flux.dev model access permissions
- Ensure sufficient disk space (50GB+ for model)

### "Frontend can't connect to API"
- Verify RunPod port 8000 is exposed
- Check `NEXT_PUBLIC_API_URL` in Vercel
- Test API with `curl https://your-url/api/health`

### "Images not loading"
- If using S3: verify AWS credentials
- If using local storage: ensure images directory exists
- Check browser console for CORS errors

## 📚 Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11
- **AI Model**: Flux.dev (black-forest-labs/FLUX.1-dev)
- **GPU**: PyTorch, CUDA 12.1
- **Storage**: AWS S3 or local filesystem
- **Deployment**: Vercel + RunPod

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

AGPLv3 - See LICENSE file for details

## 🙏 Acknowledgments

- [Black Forest Labs](https://huggingface.co/black-forest-labs) for Flux.dev
- [RunPod](https://runpod.io) for affordable GPU compute
- [Vercel](https://vercel.com) for frontend hosting

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review RunPod and Vercel docs

---

**Ready to generate?** Follow the Quick Start guide above! 🚀
