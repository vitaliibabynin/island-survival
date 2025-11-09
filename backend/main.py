from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from datetime import datetime
import json

from image_generator import FluxPanoramaGenerator
from prompt_generator import PromptGenerator
from storage import ImageStorage

app = FastAPI(title="Island Survival API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
generator = FluxPanoramaGenerator()
prompt_gen = PromptGenerator()
storage = ImageStorage()

# In-memory storage (replace with database in production)
generated_images = []


class GenerateRequest(BaseModel):
    scenario: str = "random"
    custom_prompt: Optional[str] = None


class ImageResponse(BaseModel):
    id: str
    prompt: str
    image_url: str
    created_at: str
    scenario: str


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


@app.post("/api/generate", response_model=ImageResponse)
async def generate_image(request: GenerateRequest):
    """Generate a 360° panoramic image based on scenario"""

    try:
        # Generate or use custom prompt
        if request.custom_prompt:
            prompt = request.custom_prompt
        else:
            prompt = prompt_gen.generate(request.scenario)

        print(f"Generating image with prompt: {prompt}")

        # Generate image
        image = generator.generate(prompt)

        # Save and upload image
        image_id = f"{int(datetime.utcnow().timestamp())}"
        local_path = f"/app/generated_images/{image_id}.png"
        image.save(local_path)

        # Upload to S3 (or use local URL for development)
        image_url = storage.upload(local_path, image_id)

        # Create response
        image_data = ImageResponse(
            id=image_id,
            prompt=prompt,
            image_url=image_url,
            created_at=datetime.utcnow().isoformat(),
            scenario=request.scenario
        )

        # Store in memory (replace with database)
        generated_images.insert(0, image_data.dict())

        # Save to JSON file as backup
        with open("/app/generated_images/metadata.json", "w") as f:
            json.dump(generated_images, f, indent=2)

        return image_data

    except Exception as e:
        print(f"Error generating image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
