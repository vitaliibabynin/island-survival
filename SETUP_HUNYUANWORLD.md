# HunyuanWorld-1.0 Local Setup Guide

## Your Hardware: 3080 Ti (11GB VRAM) ✅ PERFECT

Your 3080 Ti is ideal for this. You can run everything locally!

## Quick Start Installation

### Step 1: Prerequisites

```bash
# Check your CUDA version
nvidia-smi

# You need:
# - Python 3.10 or 3.11
# - CUDA 11.8 or 12.4
# - Git
```

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Tencent-Hunyuan/HunyuanWorld-1.0.git
cd HunyuanWorld-1.0

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA support
# For CUDA 11.8:
pip install torch==2.5.0 torchvision==0.20.0 --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.4:
pip install torch==2.5.0 torchvision==0.20.0 --index-url https://download.pytorch.org/whl/cu124
```

### Step 3: Download Models

The models will auto-download on first run, but you can pre-download:

```bash
# Models are downloaded from HuggingFace
# Panorama generation model: ~478MB
# Scene reconstruction models: varies by component
```

### Step 4: Test with Island Scene

```bash
# Generate a panoramic beach scene
python demo_panogen.py \
  --prompt "tropical island beach with shipwreck, palm trees, golden sunset, photorealistic" \
  --output_path output/beach/

# Generate 3D world from panorama
python demo_scenegen.py \
  --image_path output/beach/panorama.png \
  --classes outdoor \
  --output_path output/beach_3d/ \
  --labels_fg1 "shipwreck" \
  --labels_fg2 "palm trees"
```

### Step 5: More Island Scenes

```bash
# Jungle scene
python demo_panogen.py \
  --prompt "dense tropical jungle interior, vines, exotic plants, dappled sunlight" \
  --output_path output/jungle/

# Abandoned villa
python demo_panogen.py \
  --prompt "abandoned luxury villa interior, dusty furniture, broken windows, overgrown plants" \
  --output_path output/villa/

# Ancient ruins
python demo_panogen.py \
  --prompt "mayan temple ruins, stone carvings, jungle overgrowth, mysterious atmosphere" \
  --output_path output/ruins/

# Underground bunker
python demo_panogen.py \
  --prompt "abandoned underground bunker, concrete walls, old equipment, dim lighting" \
  --output_path output/bunker/
```

## Memory Optimization for 11GB VRAM

If you encounter VRAM issues, use these optimizations:

```bash
# Use FP16 mode (half precision)
python demo_scenegen.py \
  --image_path panorama.png \
  --fp16 \
  --output_path output/

# Use quantization
python demo_scenegen.py \
  --image_path panorama.png \
  --quantize \
  --output_path output/
```

## Expected Performance

**3080 Ti (11GB VRAM):**
- Panorama generation: ~30-60 seconds
- Scene reconstruction: ~2-5 minutes
- Total per scene: ~5-10 minutes

**You can generate:**
- 5-10 island locations in 1 hour
- All needed environments in an afternoon

## Exporting for Game Use

The output will include:
- `.png` - Panoramic images
- `.glb` or `.obj` - 3D mesh files
- Draco-compressed meshes for web use

To use in Three.js:
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load('output/beach_3d/scene.glb', (gltf) => {
  scene.add(gltf.scene);
});
```

## Troubleshooting

### CUDA Out of Memory
```bash
# Reduce resolution or use lite models
python demo_panogen.py --lite --prompt "your scene"
```

### Models not downloading
```bash
# Manually set HuggingFace cache
export HF_HOME="/path/to/large/drive"
```

### Slow generation
```bash
# Enable caching
export TORCH_HOME="./cache"
```

## Next Steps

Once this works, we'll set up:
1. **Hunyuan3D-2** - For individual 3D objects (coconuts, weapons, etc.)
2. **Automation pipeline** - Generate everything from a script
3. **Three.js integration** - Load into playable game

## Test Command (5 minutes)

Run this single command to test everything:

```bash
python demo_panogen.py \
  --prompt "shipwreck on tropical beach at sunset" \
  --output_path test_output/ && \
python demo_scenegen.py \
  --image_path test_output/panorama.png \
  --classes outdoor \
  --output_path test_output/3d/
```

If this works, you're ready to generate your entire island! 🏝️

---

## Estimated Costs

**Running Locally (Your 3080 Ti):**
- Cost: $0 (FREE)
- Power consumption: ~$0.50/day if running 8 hours
- Total for entire project: **~$2 in electricity**

**Cloud Alternative (if needed):**
- RunPod RTX 4090: $0.44/hour
- Generate all assets: ~4 hours = **$1.76**
- Well under your $100 budget!

**Recommendation:** Start local (free), use cloud only if needed.
