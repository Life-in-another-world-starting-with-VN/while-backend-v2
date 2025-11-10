"""Test that images are generated with 16:9 aspect ratio"""
import os
from dotenv import load_dotenv
from application.background_generator import BackgroundGenerator
from pathlib import Path
from PIL import Image

load_dotenv()

print("="*80)
print("Testing 16:9 Aspect Ratio")
print("="*80)

try:
    generator = BackgroundGenerator()
    print("✓ BackgroundGenerator initialized")
    
    # Generate test image
    keyword = "sunny classroom"
    print(f"\nGenerating image for: {keyword}")
    
    image_url = generator.create_background_image_by_keyword(keyword)
    print(f"✓ Image generated: {image_url}")
    
    # Get file path
    filename = image_url.split("/")[-1]
    filepath = Path("static/generated_images") / filename
    
    # Open image and check dimensions
    img = Image.open(filepath)
    width, height = img.size
    
    print(f"\nImage dimensions:")
    print(f"  Width: {width}px")
    print(f"  Height: {height}px")
    
    # Calculate aspect ratio
    aspect_ratio = width / height
    expected_ratio = 16 / 9
    
    print(f"\nAspect ratio:")
    print(f"  Actual: {aspect_ratio:.4f}")
    print(f"  Expected (16:9): {expected_ratio:.4f}")
    print(f"  Difference: {abs(aspect_ratio - expected_ratio):.4f}")
    
    # Check if aspect ratio is close to 16:9 (allow small tolerance)
    tolerance = 0.05
    if abs(aspect_ratio - expected_ratio) < tolerance:
        print(f"\n✓ PASS: Image has correct 16:9 aspect ratio!")
    else:
        print(f"\n✗ FAIL: Image aspect ratio is not 16:9")
        print(f"  Image appears to be {width}:{height}")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
