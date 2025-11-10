from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from datetime import datetime
import json
import uuid
from enum import Enum

from image_generator import FluxPanoramaGenerator
from prompt_generator import PromptGenerator
from storage import ImageStorage
from world_generator import HunyuanWorldGenerator

app = FastAPI(title="Island Survival API")

# Create images directory if it doesn't exist
os.makedirs("/app/generated_images", exist_ok=True)
os.makedirs("/app/generated_worlds", exist_ok=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images and 3D worlds
app.mount("/images", StaticFiles(directory="/app/generated_images"), name="images")
app.mount("/worlds", StaticFiles(directory="/app/generated_worlds"), name="worlds")

# Initialize components
generator = FluxPanoramaGenerator()
prompt_gen = PromptGenerator()
storage = ImageStorage()
world_gen = HunyuanWorldGenerator()

# Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# In-memory storage
generated_images = []
jobs = {}  # job_id -> job info


class GenerateRequest(BaseModel):
    scenario: str = "random"
    custom_prompt: Optional[str] = None


class ImageResponse(BaseModel):
    id: str
    prompt: str
    image_url: str
    created_at: str
    scenario: str


class Generate3DRequest(BaseModel):
    image_id: str
    classes: Optional[str] = None  # outdoor, indoor, etc.


class World3DResponse(BaseModel):
    id: str
    image_id: str
    world_url: str  # URL to .glb file
    created_at: str
    scenario: str


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[ImageResponse] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "Island Survival API",
        "status": "running",
        "model_loaded": generator.is_loaded()
    }


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": generator.is_loaded(),
        "timestamp": datetime.utcnow().isoformat()
    }


def process_generation(job_id: str, scenario: str, custom_prompt: Optional[str] = None):
    """Background task to generate image"""
    try:
        # Update status to processing
        jobs[job_id]["status"] = JobStatus.PROCESSING

        # Generate or use custom prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = prompt_gen.generate(scenario)

        print(f"[Job {job_id}] Generating image with prompt: {prompt}")

        # Generate image
        image = generator.generate(prompt)

        # Save and upload image
        image_id = f"{int(datetime.utcnow().timestamp())}"
        local_path = f"/app/generated_images/{image_id}.png"

        os.makedirs("/app/generated_images", exist_ok=True)
        image.save(local_path)

        # Upload to S3 (or use local URL for development)
        image_url = storage.upload(local_path, image_id)

        # Create response
        image_data = ImageResponse(
            id=image_id,
            prompt=prompt,
            image_url=image_url,
            created_at=datetime.utcnow().isoformat(),
            scenario=scenario
        )

        # Store in memory
        generated_images.insert(0, image_data.dict())

        # Save to JSON file as backup
        with open("/app/generated_images/metadata.json", "w") as f:
            json.dump(generated_images, f, indent=2)

        # Update job status
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        jobs[job_id]["result"] = image_data.dict()

        print(f"[Job {job_id}] Completed successfully")

    except Exception as e:
        print(f"[Job {job_id}] Error: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


@app.post("/api/generate", response_model=JobResponse)
async def generate_image(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start async image generation and return job ID"""

    # Create job
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "scenario": request.scenario,
        "completed_at": None,
        "result": None,
        "error": None
    }

    # Start background task
    background_tasks.add_task(
        process_generation,
        job_id,
        request.scenario,
        request.custom_prompt
    )

    return JobResponse(**jobs[job_id])


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """Get status of a generation job"""

    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse(**jobs[job_id])


@app.get("/api/images", response_model=List[ImageResponse])
async def get_images():
    """Get all generated images"""

    # Load from JSON file
    try:
        if os.path.exists("/app/generated_images/metadata.json"):
            with open("/app/generated_images/metadata.json", "r") as f:
                data = json.load(f)
                return data
    except Exception as e:
        print(f"Error loading images: {e}")

    return generated_images


@app.get("/api/images/{image_id}", response_model=ImageResponse)
async def get_image(image_id: str):
    """Get a specific image by ID"""

    for img in generated_images:
        if img["id"] == image_id:
            return img

    raise HTTPException(status_code=404, detail="Image not found")


@app.delete("/api/images/{image_id}")
async def delete_image(image_id: str):
    """Delete an image"""

    global generated_images

    for i, img in enumerate(generated_images):
        if img["id"] == image_id:
            # Delete from storage
            storage.delete(image_id)

            # Remove from memory
            generated_images.pop(i)

            # Update JSON
            with open("/app/generated_images/metadata.json", "w") as f:
                json.dump(generated_images, f, indent=2)

            return {"message": "Image deleted"}

    raise HTTPException(status_code=404, detail="Image not found")


# ============================================================================
# 3D World Generation Endpoints
# ============================================================================

def process_3d_generation(job_id: str, image_id: str, scenario: str, classes: Optional[str] = None):
    """Background task to generate 3D world from panorama"""
    try:
        jobs[job_id]["status"] = JobStatus.PROCESSING

        if not world_gen.is_available():
            raise Exception("HunyuanWorld is not installed. Run install_hunyuan.sh first.")

        # Find the panorama image
        panorama_path = f"/app/generated_images/{image_id}.png"
        if not os.path.exists(panorama_path):
            raise Exception(f"Panorama image not found: {image_id}")

        # Determine scene class
        if not classes:
            classes = world_gen.get_scene_class(scenario)

        # Get foreground labels
        fg1, fg2 = world_gen.get_foreground_labels(scenario)

        print(f"[Job {job_id}] Generating 3D world from {panorama_path}")
        print(f"[Job {job_id}] Scene class: {classes}, FG labels: {fg1}, {fg2}")

        # Generate 3D world
        world_id = f"world_{image_id}"
        output_dir = f"/app/generated_worlds/{world_id}"

        glb_path = world_gen.generate_3d_world(
            panorama_path=panorama_path,
            output_path=output_dir,
            classes=classes,
            labels_fg1=fg1,
            labels_fg2=fg2
        )

        # Get public URL for the .glb file
        public_url = os.getenv("PUBLIC_URL", os.getenv("LOCAL_BASE_URL", "http://localhost:8000"))
        glb_filename = os.path.basename(glb_path)
        world_url = f"{public_url}/worlds/{world_id}/{glb_filename}"

        # Create response
        world_data = World3DResponse(
            id=world_id,
            image_id=image_id,
            world_url=world_url,
            created_at=datetime.utcnow().isoformat(),
            scenario=scenario
        )

        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        jobs[job_id]["result"] = world_data.dict()

        print(f"[Job {job_id}] 3D world generated successfully: {world_url}")

    except Exception as e:
        print(f"[Job {job_id}] 3D generation error: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


@app.post("/api/generate-3d", response_model=JobResponse)
async def generate_3d_world(request: Generate3DRequest, background_tasks: BackgroundTasks):
    """Generate 3D world from existing panorama image"""

    # Find the image to get scenario info
    image_data = None
    for img in generated_images:
        if img["id"] == request.image_id:
            image_data = img
            break

    if not image_data:
        raise HTTPException(status_code=404, detail=f"Image {request.image_id} not found")

    # Create job
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "created_at": datetime.utcnow().isoformat(),
        "scenario": image_data["scenario"],
        "completed_at": None,
        "result": None,
        "error": None
    }

    # Start background task
    background_tasks.add_task(
        process_3d_generation,
        job_id,
        request.image_id,
        image_data["scenario"],
        request.classes
    )

    return JobResponse(**jobs[job_id])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
