"""Test gemini-2.5-flash-image with REST API"""
import os
from dotenv import load_dotenv
from application.background_generator import BackgroundGenerator

load_dotenv()

print("="*80)
print("Testing gemini-2.5-flash-image integration")
print("="*80)

try:
    # Initialize generator
    generator = BackgroundGenerator()
    print("✓ BackgroundGenerator initialized successfully")
    
    # Test with a simple keyword
    keyword = "sunny classroom"
    print(f"\nGenerating image for keyword: {keyword}")
    print("This may take 30-60 seconds...")
    
    image_url = generator.create_background_image_by_keyword(keyword)
    
    print(f"\n✓ SUCCESS!")
    print(f"Image URL: {image_url}")
    
    # Verify file exists
    from pathlib import Path
    filename = image_url.split("/")[-1]
    filepath = Path("static/generated_images") / filename
    
    if filepath.exists():
        print(f"✓ File exists: {filepath}")
        print(f"✓ File size: {filepath.stat().st_size} bytes")
    else:
        print(f"✗ File not found: {filepath}")
    
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
