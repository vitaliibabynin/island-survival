import random
from typing import Dict, List


class PromptGenerator:
    """
    Generates detailed prompts for island survival scenarios.
    Creates varied, high-quality prompts for panoramic generation.
    """

    def __init__(self):
        # Base scenarios with detailed descriptions
        self.scenarios: Dict[str, List[str]] = {
            "beach": [
                "pristine tropical beach with white sand, crystal clear turquoise water, palm trees swaying in the breeze, scattered driftwood, gentle waves lapping the shore",
                "rugged coastline with rocky outcrops, crashing waves, sea foam, distant mountains, overcast sky with dramatic clouds",
                "secluded cove with golden sand, shallow lagoon, coral visible underwater, tropical vegetation, bright sunny day",
                "volcanic black sand beach, dramatic cliffs, powerful surf, scattered volcanic rocks, moody atmosphere",
            ],
            "jungle": [
                "dense tropical rainforest, towering trees with thick canopy, hanging vines, lush undergrowth, filtered sunlight, exotic plants",
                "jungle clearing with ancient trees, vibrant flowers, butterflies, shafts of light breaking through leaves, misty atmosphere",
                "overgrown jungle path, massive tree roots, dense foliage, tropical birds, humid atmosphere, green everywhere",
                "bamboo forest with tall stalks, dappled light, zen-like atmosphere, occasional clearing, peaceful ambiance",
            ],
            "mountain": [
                "mountain peak vista, snow-capped summits in distance, rocky terrain, alpine meadow, clear blue sky, panoramic view",
                "high altitude mountain ridge, steep cliffs, jagged rocks, thin clouds below, dramatic elevation, vast landscape",
                "mountain valley overlook, forested slopes, winding river below, expansive view, golden hour lighting",
                "rocky mountain outcrop, mossy stones, small alpine plants, distant peaks, crisp mountain air",
            ],
            "cave": [
                "mysterious cave entrance, stalactites and stalagmites, pools of water reflecting light, bioluminescent fungi, ethereal glow",
                "deep cave chamber, ancient rock formations, underground lake, shafts of light from above, mystical atmosphere",
                "coastal cave with ocean visible through opening, tide pools, wet rocks, echoing sounds of waves",
                "volcanic cave with rough lava rock walls, otherworldly formations, hidden chambers, dramatic shadows",
            ],
            "ruins": [
                "ancient temple ruins overgrown with jungle, moss-covered stone blocks, carved pillars, tropical plants reclaiming the structure",
                "weathered stone ruins on coastal cliff, partially collapsed walls, ocean view, dramatic sky, sense of mystery",
                "abandoned civilization remnants, crumbling architecture, vine-covered statues, forgotten plaza, historical atmosphere",
                "mysterious megalithic structures, standing stones arranged in circle, grassy terrain, ancient power in the air",
            ],
            "storm": [
                "dramatic storm approaching over ocean, dark clouds, lightning in distance, choppy seas, wind-swept beach",
                "stormy jungle scene, rain pouring through canopy, lightning illuminating trees, wet foliage, intense atmosphere",
                "mountain storm, swirling clouds, limited visibility, powerful winds, dramatic weather patterns, nature's fury",
                "coastal storm, massive waves crashing, spray in the air, grey sky, turbulent sea, raw power of nature",
            ],
            "sunset": [
                "breathtaking sunset over ocean, vibrant orange and pink sky, sun touching horizon, silhouetted palm trees, calm water reflecting colors",
                "mountain sunset, golden light on peaks, long shadows, warm glow, transitioning to evening, spectacular colors",
                "jungle sunset, sun rays through trees, golden hour lighting, peaceful atmosphere, wildlife settling for night",
                "island sunset panorama, 360 degree view of colorful sky, warm light on landscape, end of day serenity",
            ],
            "night": [
                "starry night sky over island, Milky Way visible, bioluminescent waves on beach, moonlight, cosmic wonder",
                "moonlit jungle, mysterious shadows, nocturnal atmosphere, silvery light filtering through trees, quiet night sounds",
                "night mountain vista, stars above, city lights far in distance, cool night air, peaceful darkness",
                "beach at night, full moon reflection on water, stars above, gentle waves, tranquil nighttime scene",
            ],
        }

        # Additional elements to add variety
        self.weather_elements = [
            "clear sunny day",
            "partly cloudy",
            "dramatic clouds",
            "misty morning",
            "golden hour lighting",
            "overcast sky",
            "scattered clouds",
            "brilliant sunshine",
        ]

        self.atmosphere_elements = [
            "serene atmosphere",
            "mysterious ambiance",
            "dramatic mood",
            "peaceful setting",
            "untouched wilderness",
            "pristine nature",
            "wild and remote",
            "breathtaking vista",
        ]

    def generate(self, scenario: str = "random") -> str:
        """
        Generate a detailed prompt for the given scenario.

        Args:
            scenario: Type of scene (beach, jungle, mountain, etc.) or 'random'

        Returns:
            Detailed prompt string
        """

        # Handle random scenario
        if scenario == "random":
            scenario = random.choice(list(self.scenarios.keys()))

        # Get base prompt
        if scenario in self.scenarios:
            base_prompt = random.choice(self.scenarios[scenario])
        else:
            # Fallback to beach if unknown scenario
            base_prompt = random.choice(self.scenarios["beach"])

        # Add variety with additional elements
        weather = random.choice(self.weather_elements)
        atmosphere = random.choice(self.atmosphere_elements)

        # Combine elements
        full_prompt = f"{base_prompt}, {weather}, {atmosphere}"

        return full_prompt

    def generate_batch(self, scenario: str, count: int = 5) -> List[str]:
        """
        Generate multiple prompts for batch processing.

        Args:
            scenario: Type of scene
            count: Number of prompts to generate

        Returns:
            List of prompt strings
        """
        return [self.generate(scenario) for _ in range(count)]

    def get_all_scenarios(self) -> List[str]:
        """Get list of all available scenarios"""
        return list(self.scenarios.keys())


# Example usage and testing
if __name__ == "__main__":
    gen = PromptGenerator()

    print("=== Testing Prompt Generator ===\n")

    # Test each scenario
    for scenario in gen.get_all_scenarios():
        print(f"{scenario.upper()}:")
        print(gen.generate(scenario))
        print()

    # Test random
    print("RANDOM:")
    for _ in range(3):
        print(f"- {gen.generate('random')}")
