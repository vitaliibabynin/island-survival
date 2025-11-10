import os
import subprocess
from PIL import Image
from typing import Optional


class HunyuanWorldGenerator:
    """
    Wrapper for HunyuanWorld-1.0 to generate 3D worlds from panoramic images.
    """

    def __init__(self):
        self.hunyuan_path = "/workspace/HunyuanWorld-1.0"
        self.available = os.path.exists(self.hunyuan_path)

        if not self.available:
            print("⚠️  HunyuanWorld not installed. 3D generation will be disabled.")
            print("   Run: bash install_hunyuan.sh to enable 3D world generation")

    def is_available(self) -> bool:
        """Check if HunyuanWorld is installed and ready"""
        return self.available

    def generate_3d_world(
        self,
        panorama_path: str,
        output_path: str,
        classes: str = "outdoor",
        labels_fg1: Optional[str] = None,
        labels_fg2: Optional[str] = None
    ) -> str:
        """
        Generate 3D world mesh from panoramic image.

        Args:
            panorama_path: Path to panoramic image (equirectangular)
            output_path: Directory to save generated 3D mesh
            classes: Scene class (outdoor, indoor, etc.)
            labels_fg1: Foreground object labels (layer 1)
            labels_fg2: Foreground object labels (layer 2)

        Returns:
            Path to generated .glb file
        """

        if not self.available:
            raise Exception("HunyuanWorld is not installed. Run install_hunyuan.sh first.")

        # Create output directory
        os.makedirs(output_path, exist_ok=True)

        # Build command
        cmd = [
            "python3",
            f"{self.hunyuan_path}/demo_scenegen.py",
            "--image_path", panorama_path,
            "--classes", classes,
            "--output_path", output_path,
        ]

        # Add optional foreground labels
        if labels_fg1:
            cmd.extend(["--labels_fg1", labels_fg1])
        if labels_fg2:
            cmd.extend(["--labels_fg2", labels_fg2])

        print(f"Running HunyuanWorld: {' '.join(cmd)}")

        # Prepare environment with HuggingFace token
        env = os.environ.copy()
        if "HUGGINGFACE_TOKEN" in env:
            env["HF_TOKEN"] = env["HUGGINGFACE_TOKEN"]  # HuggingFace libraries use HF_TOKEN

        # Run HunyuanWorld scene generation
        try:
            result = subprocess.run(
                cmd,
                cwd=self.hunyuan_path,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env=env  # Pass environment variables including HF_TOKEN
            )

            if result.returncode != 0:
                print(f"Error output: {result.stderr}")
                raise Exception(f"HunyuanWorld generation failed: {result.stderr}")

            print(f"HunyuanWorld output: {result.stdout}")

            # Find generated .glb file
            glb_file = os.path.join(output_path, "scene.glb")

            if not os.path.exists(glb_file):
                # Try alternative paths
                possible_paths = [
                    os.path.join(output_path, "mesh.glb"),
                    os.path.join(output_path, "output.glb"),
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        glb_file = path
                        break
                else:
                    raise Exception(f"Generated .glb file not found in {output_path}")

            return glb_file

        except subprocess.TimeoutExpired:
            raise Exception("3D generation timed out (>10 minutes)")
        except Exception as e:
            raise Exception(f"3D generation failed: {str(e)}")

    def get_scene_class(self, scenario: str) -> str:
        """Map scenario to scene class for HunyuanWorld"""
        outdoor_scenarios = ["beach", "jungle", "mountain", "ruins", "storm", "sunset", "night", "random"]

        if scenario in outdoor_scenarios:
            return "outdoor"
        elif scenario in ["cave"]:
            return "indoor"
        else:
            return "outdoor"  # default

    def get_foreground_labels(self, scenario: str) -> tuple[Optional[str], Optional[str]]:
        """Get suggested foreground labels based on scenario"""

        label_map = {
            "beach": ("tree", "rock"),
            "jungle": ("tree", "plant"),
            "mountain": ("rock", "tree"),
            "cave": ("rock", "stalactite"),
            "ruins": ("column", "wall"),
            "storm": ("tree", "cloud"),
            "sunset": ("tree", "cloud"),
            "night": ("tree", "star"),
        }

        return label_map.get(scenario, (None, None))


# Example usage
if __name__ == "__main__":
    gen = HunyuanWorldGenerator()

    if gen.is_available():
        print("HunyuanWorld is ready!")

        # Test generation
        panorama = "/path/to/panorama.png"
        output = "/path/to/output"

        glb_path = gen.generate_3d_world(panorama, output, classes="outdoor")
        print(f"Generated 3D world: {glb_path}")
    else:
        print("HunyuanWorld not installed.")
