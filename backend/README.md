# Island Survival - Backend API

FastAPI backend for generating 360° panoramic images using Flux.dev.

## 🚀 Quick Start

### Local Development (requires 24GB+ GPU)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGINGFACE_TOKEN=hf_your_token_here

# Run API server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### RunPod Deployment (Recommended)

```bash
# 1. SSH into RunPod instance
# 2. Clone repository
git clone https://github.com/vitaliibabynin/island-survival.git
cd island-survival/backend

# 3. Run setup script
chmod +x setup_runpod.sh
./setup_runpod.sh

# 4. Set environment variables
export HUGGINGFACE_TOKEN=hf_your_token_here

# 5. Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app and routes
├── image_generator.py      # Flux.dev model wrapper
├── prompt_generator.py     # Automated prompt generation
├── storage.py             # S3/local storage handler
├── auto_generate.py       # Batch generation script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── setup_runpod.sh       # RunPod setup script
└── .env.example          # Environment variables template
```

## 🔌 API Endpoints

### Health Check

```bash
GET /api/health

Response:
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2025-11-09T00:00:00"
}
```

### Generate Image

```bash
POST /api/generate

Body:
{
  "scenario": "beach",          # or jungle, mountain, cave, ruins, storm, sunset, night, random
  "custom_prompt": null         # optional custom prompt
}

Response:
{
  "id": "1699488000",
  "prompt": "pristine tropical beach with white sand...",
  "image_url": "https://...",
  "created_at": "2025-11-09T00:00:00",
  "scenario": "beach"
}
```

### List Images

```bash
GET /api/images

Response:
[
  {
    "id": "1699488000",
    "prompt": "...",
    "image_url": "https://...",
    "created_at": "2025-11-09T00:00:00",
    "scenario": "beach"
  },
  ...
]
```

### Get Single Image

```bash
GET /api/images/{image_id}

Response:
{
  "id": "1699488000",
  "prompt": "...",
  "image_url": "https://...",
  "created_at": "2025-11-09T00:00:00",
  "scenario": "beach"
}
```

### Delete Image

```bash
DELETE /api/images/{image_id}

Response:
{
  "message": "Image deleted"
}
```

## 🤖 Automated Generation

### Basic Usage

```bash
# Generate all scenarios (1 each)
python auto_generate.py --scenarios all --count 1

# Generate specific scenarios
python auto_generate.py --scenarios beach,jungle,mountain --count 2

# Generate random scenarios
python auto_generate.py --scenarios random --count 10
```

### Advanced Usage

```bash
# Custom output directory
python auto_generate.py \
  --scenarios all \
  --count 3 \
  --output /custom/path/images

# Generate overnight batch
nohup python auto_generate.py --scenarios all --count 10 > generation.log 2>&1 &
```

## 🎨 Customization

### Adjust Image Quality

Edit `image_generator.py`:

```python
def generate(
    self,
    prompt: str,
    width: int = 4096,      # Increase for higher resolution
    height: int = 2048,     # Maintain 2:1 ratio
    num_inference_steps: int = 100,  # More steps = better quality
    guidance_scale: float = 7.5,     # Higher = more prompt adherence
):
```

**Recommended settings:**

- **High Quality**: 4096x2048, 100 steps (~3-4 min/image)
- **Balanced**: 2048x1024, 50 steps (~1-2 min/image)
- **Fast**: 1024x512, 30 steps (~30 sec/image)

### Add Custom Scenarios

Edit `prompt_generator.py`:

```python
self.scenarios["underwater"] = [
    "underwater coral reef, vibrant colors, tropical fish, clear water",
    "deep ocean trench, bioluminescent creatures, mysterious atmosphere",
]
```

### Enable Memory Optimizations

For GPUs with <24GB VRAM, uncomment in `image_generator.py`:

```python
# Enable CPU offloading (reduces VRAM usage to ~12GB)
self.pipe.enable_model_cpu_offload()

# Enable sequential CPU offloading (even lower VRAM)
self.pipe.enable_sequential_cpu_offload()
```

## 💾 Storage Options

### Option 1: Local Storage (Default)

Images stored in `/app/generated_images/`
URLs: `http://localhost:8000/images/{id}.png`

**Pros**: No setup, works immediately
**Cons**: Images lost when instance stops

### Option 2: AWS S3 (Recommended)

Set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export S3_BUCKET_NAME=island-survival-images
export S3_REGION=us-east-1
```

**Pros**: Persistent, scalable, CDN-ready
**Cons**: Costs ~$0.023/GB/month

### Option 3: RunPod Network Storage

Mount a network volume in RunPod:

```bash
# In RunPod dashboard, add network volume
# Mount to: /app/generated_images
```

**Pros**: Persistent, fast, integrated
**Cons**: RunPod-specific, ~$0.10/GB/month

## 🔧 Environment Variables

Create `.env` file:

```bash
# Required
HUGGINGFACE_TOKEN=hf_your_token_here

# Optional - AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=island-survival-images
S3_REGION=us-east-1

# Optional - Local URL
LOCAL_BASE_URL=http://localhost:8000
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t island-survival-api .
```

### Run Container

```bash
docker run --gpus all \
  -p 8000:8000 \
  -e HUGGINGFACE_TOKEN=hf_your_token \
  -v $(pwd)/generated_images:/app/generated_images \
  island-survival-api
```

## 📊 Performance Benchmarks

### Generation Time (2048x1024, 50 steps)

- **RTX 4090**: ~60-90 seconds
- **A6000**: ~90-120 seconds
- **A100 (40GB)**: ~45-60 seconds

### VRAM Usage

- **Model Loading**: ~20GB
- **During Generation**: ~22-24GB
- **With CPU Offload**: ~12-14GB

### Disk Usage

- **Model Cache**: ~40GB
- **Per Image (PNG)**: ~3-10MB
- **100 Images**: ~500MB-1GB

## 🐛 Troubleshooting

### "RuntimeError: CUDA out of memory"

**Solution 1**: Enable CPU offload

```python
self.pipe.enable_model_cpu_offload()
```

**Solution 2**: Reduce image size

```python
width=1024, height=512
```

**Solution 3**: Use larger GPU (A6000 or A100)

### "Model loading too slow"

**Solution**: Models are cached after first load. Subsequent starts are faster.

First run: ~5-10 minutes
After caching: ~30-60 seconds

### "Connection timeout"

**Solution**: Increase timeout in frontend:

```typescript
const response = await axios.post(url, data, {
  timeout: 300000  // 5 minutes
})
```

### "Images not persisting"

**Solution**: Use S3 or network storage instead of local filesystem

## 📈 Monitoring

### Check API Status

```bash
curl http://localhost:8000/api/health
```

### Monitor GPU Usage

```bash
watch nvidia-smi
```

### View Logs

```bash
# Follow logs
tail -f generation.log

# Filter errors
grep ERROR generation.log
```

## 🔒 Security

### Production Checklist

- [ ] Set strong HuggingFace token
- [ ] Use environment variables (never commit tokens)
- [ ] Enable CORS only for your domain
- [ ] Add rate limiting
- [ ] Use HTTPS
- [ ] Restrict S3 bucket access
- [ ] Enable API authentication

### Example: Add API Key Auth

Edit `main.py`:

```python
from fastapi import Header, HTTPException

async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401)

@app.post("/api/generate", dependencies=[Depends(verify_token)])
async def generate_image(request: GenerateRequest):
    # ...
```

## 📚 Resources

- [Flux.dev Model](https://huggingface.co/black-forest-labs/FLUX.1-dev)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [RunPod Docs](https://docs.runpod.io)
- [Diffusers Library](https://huggingface.co/docs/diffusers)

---

**Need help?** Check the main [README.md](../README.md) or open an issue on GitHub.
