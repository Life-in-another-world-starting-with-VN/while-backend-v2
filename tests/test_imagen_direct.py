"""Test Imagen API directly"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_TOKEN"))

test_prompt = "sunny classroom, visual novel style, clean line art, no people, environment only"

print(f"Testing Imagen 3.0...")
print(f"Prompt: {test_prompt}\n")

try:
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=test_prompt,
        config={
            "number_of_images": 1,
            "aspect_ratio": "16:9",
            "safety_filter_level": "block_low_and_above",
            "person_generation": "dont_allow"
        }
    )
    
    print(f"Response received!")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print(f"\nHas generated_images: {hasattr(response, 'generated_images')}")
    
    if hasattr(response, 'generated_images'):
        print(f"Number of images: {len(response.generated_images)}")
        if response.generated_images:
            print(f"First image type: {type(response.generated_images[0])}")
            print(f"First image: {response.generated_images[0]}")
            
            # Check attributes
            img = response.generated_images[0]
            print(f"\nImage attributes:")
            for attr in dir(img):
                if not attr.startswith('_'):
                    print(f"  - {attr}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
