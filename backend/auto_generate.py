#!/usr/bin/env python3
"""
Automated image generation script.
Run this to generate multiple panoramas automatically.
"""

import asyncio
import argparse
from datetime import datetime
from image_generator import FluxPanoramaGenerator
from prompt_generator import PromptGenerator
from storage import ImageStorage
import json
import os


async def generate_single(
    generator: FluxPanoramaGenerator,
    prompt_gen: PromptGenerator,
    storage: ImageStorage,
    scenario: str,
    output_dir: str = "/app/generated_images"
):
    """Generate a single image"""

    # Generate prompt
    prompt = prompt_gen.generate(scenario)
    print(f"\n{'='*60}")
    print(f"Scenario: {scenario}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}")

    # Generate image
    print("Generating image...")
    start_time = datetime.now()

    image = generator.generate(prompt)

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"Generated in {elapsed:.2f} seconds")

    # Save image
    image_id = f"{int(datetime.utcnow().timestamp())}"
    local_path = f"{output_dir}/{image_id}.png"
    image.save(local_path)
    print(f"Saved locally: {local_path}")

    # Upload to storage
    image_url = storage.upload(local_path, image_id)
    print(f"Available at: {image_url}")

    # Create metadata
    metadata = {
        "id": image_id,
        "prompt": prompt,
        "image_url": image_url,
        "created_at": datetime.utcnow().isoformat(),
        "scenario": scenario,
        "generation_time": elapsed
    }

    return metadata


async def generate_batch(
    scenarios: list,
    count_per_scenario: int = 1,
    output_dir: str = "/app/generated_images"
):
    """Generate multiple images across scenarios"""

    # Initialize components
    print("Initializing generator...")
    generator = FluxPanoramaGenerator()
    prompt_gen = PromptGenerator()
    storage = ImageStorage()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load existing metadata
    metadata_file = f"{output_dir}/metadata.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            all_metadata = json.load(f)
    else:
        all_metadata = []

    # Generate images
    total = len(scenarios) * count_per_scenario
    current = 0

    print(f"\n{'='*60}")
    print(f"Starting batch generation")
    print(f"Scenarios: {scenarios}")
    print(f"Count per scenario: {count_per_scenario}")
    print(f"Total images to generate: {total}")
    print(f"{'='*60}\n")

    for scenario in scenarios:
        for i in range(count_per_scenario):
            current += 1
            print(f"\nProgress: {current}/{total}")

            metadata = await generate_single(
                generator, prompt_gen, storage, scenario, output_dir
            )

            # Add to metadata list
            all_metadata.insert(0, metadata)

            # Save metadata after each generation
            with open(metadata_file, "w") as f:
                json.dump(all_metadata, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Batch generation complete!")
    print(f"Generated {total} images")
    print(f"Metadata saved to: {metadata_file}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Automated panorama generation")

    parser.add_argument(
        "--scenarios",
        type=str,
        default="all",
        help="Comma-separated scenarios or 'all' (default: all)"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of images per scenario (default: 1)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="/app/generated_images",
        help="Output directory (default: /app/generated_images)"
    )

    args = parser.parse_args()

    # Parse scenarios
    prompt_gen = PromptGenerator()
    all_scenarios = prompt_gen.get_all_scenarios()

    if args.scenarios == "all":
        scenarios = all_scenarios
    else:
        scenarios = [s.strip() for s in args.scenarios.split(",")]
        # Validate scenarios
        for s in scenarios:
            if s not in all_scenarios and s != "random":
                print(f"Warning: Unknown scenario '{s}'")

    # Run generation
    asyncio.run(generate_batch(scenarios, args.count, args.output))


if __name__ == "__main__":
    main()
