# Hunyuan3D-2 Local Setup Guide

## Object Generation (Coconuts, Weapons, Tools, Artifacts)

Your 3080 Ti (11GB VRAM) can run Hunyuan3D-2mini perfectly, and standard version with optimizations.

## Quick Start Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/Tencent-Hunyuan/Hunyuan3D-2.git
cd Hunyuan3D-2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# Install PyTorch with CUDA
# For CUDA 11.8:
pip install torch==2.5.0 torchvision==0.20.0 --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.4:
pip install torch==2.5.0 torchvision==0.20.0 --index-url https://download.pytorch.org/whl/cu124
```

### Step 3: Download Models

```bash
# Option A: Use Hunyuan3D-2mini (5GB VRAM, faster)
# Models auto-download on first run from HuggingFace

# Option B: Standard model (6GB for shape, 12GB for texture)
# Will work on your 11GB with optimizations
```

### Step 4: Generate Island Survival Objects

```bash
# Basic text-to-3D generation
python text_to_3d.py \
  --prompt "rusty machete survival knife, game asset" \
  --output "assets/machete.glb"

# With more control
python text_to_3d.py \
  --prompt "wooden spear with sharpened tip" \
  --output "assets/spear.glb" \
  --texture_resolution 2048
```

## Island Survival Asset List

Generate all these objects automatically:

### Tools & Weapons
```bash
# Machete
python text_to_3d.py --prompt "rusty machete, survival knife, worn handle" --output assets/weapons/machete.glb

# Wooden spear
python text_to_3d.py --prompt "wooden spear, sharpened stone tip, primitive weapon" --output assets/weapons/spear.glb

# Stone axe
python text_to_3d.py --prompt "stone axe, wooden handle, primitive tool" --output assets/tools/axe.glb

# Fishing spear
python text_to_3d.py --prompt "fishing spear, multiple prongs, bamboo pole" --output assets/tools/fishing_spear.glb
```

### Resources
```bash
# Coconut
python text_to_3d.py --prompt "brown coconut, tropical fruit" --output assets/resources/coconut.glb

# Palm fronds
python text_to_3d.py --prompt "palm tree fronds, tropical leaves" --output assets/resources/palm_fronds.glb

# Wood logs
python text_to_3d.py --prompt "wooden log, cut tree trunk, bark texture" --output assets/resources/wood_log.glb

# Stones
python text_to_3d.py --prompt "rough stones, rocks, gray texture" --output assets/resources/stones.glb
```

### Ancient Artifacts (Mayan/Aztec)
```bash
# Stone idol
python text_to_3d.py --prompt "mayan stone idol, ancient carving, weathered" --output assets/artifacts/idol.glb

# Gold amulet
python text_to_3d.py --prompt "aztec gold amulet, sun design, ancient jewelry" --output assets/artifacts/amulet.glb

# Stone tablet
python text_to_3d.py --prompt "stone tablet with mayan hieroglyphs, ancient writing" --output assets/artifacts/tablet.glb

# Ceremonial mask
python text_to_3d.py --prompt "aztec ceremonial mask, jade and gold, intricate design" --output assets/artifacts/mask.glb
```

### Survival Items
```bash
# Backpack
python text_to_3d.py --prompt "worn canvas backpack, survival gear" --output assets/items/backpack.glb

# Water canteen
python text_to_3d.py --prompt "metal water canteen, dented, old" --output assets/items/canteen.glb

# Rope
python text_to_3d.py --prompt "coiled rope, hemp rope, weathered" --output assets/items/rope.glb

# Campfire
python text_to_3d.py --prompt "campfire with stones, wood logs arranged" --output assets/items/campfire.glb
```

## Automated Batch Generation

Create a script to generate all assets:

```python
# generate_all_assets.py
import subprocess
import json

# Load asset list
with open('asset_list.json', 'r') as f:
    assets = json.load(f)

for asset in assets:
    cmd = f"""python text_to_3d.py \
        --prompt "{asset['prompt']}" \
        --output "assets/{asset['category']}/{asset['name']}.glb" \
        --texture_resolution {asset.get('resolution', 2048)}"""

    print(f"Generating {asset['name']}...")
    subprocess.run(cmd, shell=True)
    print(f"✓ {asset['name']} complete")

print("All assets generated!")
```

### asset_list.json
```json
{
  "assets": [
    {
      "name": "machete",
      "category": "weapons",
      "prompt": "rusty machete survival knife, worn leather handle, game asset",
      "resolution": 2048
    },
    {
      "name": "coconut",
      "category": "resources",
      "prompt": "brown coconut, hairy shell, tropical fruit",
      "resolution": 1024
    },
    {
      "name": "mayan_idol",
      "category": "artifacts",
      "prompt": "ancient mayan stone idol, weathered carved face, moss covered",
      "resolution": 4096
    }
  ]
}
```

## Memory Optimization for 11GB VRAM

```bash
# Use mini model (recommended for your 3080 Ti)
python text_to_3d.py \
  --model hunyuan3d-2mini \
  --prompt "your object" \
  --output output.glb

# Or use standard with FP16
python text_to_3d.py \
  --fp16 \
  --prompt "your object" \
  --output output.glb
```

## Expected Performance

**3080 Ti (11GB VRAM) with Hunyuan3D-2mini:**
- Shape generation: ~30 seconds
- Texture generation: ~1-2 minutes
- Total per object: ~2-3 minutes

**You can generate:**
- 20 objects/hour
- 100+ objects in an afternoon
- Entire game asset library in 1 day

## Alternative: GPU-Poor Version

If you want to use your 1080 Ti setup:

```bash
git clone https://github.com/deepbeepmeep/Hunyuan3D-2GP.git
cd Hunyuan3D-2GP

# Optimized for lower VRAM (6GB minimum)
python generate.py --prompt "your object"
```

## Output Formats

Hunyuan3D-2 exports to:
- `.glb` - Best for Three.js and web
- `.obj` - Universal format
- `.fbx` - For Unity/Unreal
- `.usd` - For advanced pipelines

## Integration with Three.js

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();

// Load generated object
loader.load('assets/weapons/machete.glb', (gltf) => {
  const machete = gltf.scene;
  machete.position.set(0, 0, 0);
  scene.add(machete);

  // Add to inventory
  inventory.add({
    name: 'Machete',
    model: machete,
    description: 'A rusty but sharp machete'
  });
});
```

## Quality Settings

```bash
# Low quality (fast, 512px textures)
python text_to_3d.py --prompt "object" --texture_resolution 512 --output low.glb

# Medium quality (balanced, 1024px)
python text_to_3d.py --prompt "object" --texture_resolution 1024 --output med.glb

# High quality (slow, 2048px)
python text_to_3d.py --prompt "object" --texture_resolution 2048 --output high.glb

# Ultra quality (very slow, 4096px - for hero objects)
python text_to_3d.py --prompt "object" --texture_resolution 4096 --output ultra.glb
```

## Cost Estimate

**Running Locally on 3080 Ti:**
- 50 objects × 3 minutes = 2.5 hours
- Power cost: ~$0.50
- **Total: $0.50**

**Cloud Alternative (if needed):**
- RunPod RTX 4090: $0.44/hour × 2 hours = $0.88
- **Total: $0.88**

## Test Command (3 minutes)

```bash
# Test generation with island object
python text_to_3d.py \
  --prompt "coconut, brown hairy shell, tropical fruit, game asset" \
  --output test_coconut.glb \
  --texture_resolution 2048

# View in browser
python -m http.server 8000
# Open http://localhost:8000/viewer.html?model=test_coconut.glb
```

## Recommended Workflow

1. **Generate 5-10 test objects** - See quality and speed
2. **Create complete asset list** - All objects needed
3. **Batch generate overnight** - Let it run unattended
4. **Review and regenerate** - Tweak prompts for better results

Your 3080 Ti can handle this easily! 🎮
