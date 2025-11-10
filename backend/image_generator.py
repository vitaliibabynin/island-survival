import torch
from PIL import Image
import os

try:
    from diffusers import FluxPipeline
except ImportError:
    # Fallback for older diffusers versions
    from diffusers import DiffusionPipeline as FluxPipeline


class FluxPanoramaGenerator:
    """
    Handles Flux.dev model loading and panoramic image generation.
    Uses the 24GB Flux.dev model for high-quality 360° panoramas.
    """

    def __init__(self):
        self.pipe = None
        self.model_id = "black-forest-labs/FLUX.1-dev"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.loaded = False

        # Load model on initialization
        self.load_model()

    def load_model(self):
        """Load the Flux.dev model"""
        try:
            print(f"Loading Flux.dev model on {self.device}...")

            # Get HuggingFace token from environment
            hf_token = os.getenv("HUGGINGFACE_TOKEN")

            if not hf_token:
                print("WARNING: HUGGINGFACE_TOKEN not set. You may need this for model access.")

            # Load pipeline with optimizations for 24GB VRAM
            # Don't move to device yet - use CPU offloading instead
            self.pipe = FluxPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.bfloat16,
                token=hf_token,
            )

            # Enable memory optimizations
            if self.device == "cuda":
                # Enable model CPU offloading (reduces VRAM usage significantly)
                print("Enabling CPU offloading for memory efficiency...")
                if hasattr(self.pipe, 'enable_model_cpu_offload'):
                    self.pipe.enable_model_cpu_offload()
                else:
                    # Fallback: sequential CPU offload
                    if hasattr(self.pipe, 'enable_sequential_cpu_offload'):
                        self.pipe.enable_sequential_cpu_offload()
                    else:
                        # Last resort: move to device normally
                        self.pipe = self.pipe.to(self.device)

                # Enable attention slicing for memory efficiency
                if hasattr(self.pipe, 'enable_attention_slicing'):
                    self.pipe.enable_attention_slicing(1)

                # Enable VAE slicing
                if hasattr(self.pipe, 'vae') and hasattr(self.pipe.vae, 'enable_slicing'):
                    self.pipe.vae.enable_slicing()
            else:
                self.pipe = self.pipe.to(self.device)

            self.loaded = True
            print("Flux.dev model loaded successfully!")

        except Exception as e:
            print(f"Error loading model: {e}")
            self.loaded = False
            raise

    def generate(
        self,
        prompt: str,
        width: int = 2048,
        height: int = 1024,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5,
    ) -> Image.Image:
        """
        Generate a panoramic image.

        Args:
            prompt: Text description of the scene
            width: Image width (default 2048 for panorama)
            height: Image height (default 1024 for 2:1 ratio)
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt

        Returns:
            PIL Image object
        """

        if not self.loaded:
            raise Exception("Model not loaded")

        # Add panoramic context to prompt
        enhanced_prompt = f"360 degree equirectangular panorama, seamless looping, {prompt}, ultra high quality, photorealistic, 8k"

        print(f"Generating with enhanced prompt: {enhanced_prompt}")

        try:
            # Generate image
            with torch.inference_mode():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                )

            image = result.images[0]

            return image

        except torch.cuda.OutOfMemoryError:
            print("CUDA out of memory! Try reducing image size or enabling CPU offload.")
            raise
        except Exception as e:
            print(f"Error during generation: {e}")
            raise

    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.loaded

    def unload_model(self):
        """Unload model to free memory"""
        if self.pipe:
            del self.pipe
            if self.device == "cuda":
                torch.cuda.empty_cache()
            self.loaded = False
            print("Model unloaded")
