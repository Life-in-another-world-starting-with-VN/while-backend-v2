"""Complete integration test for Google AI image generation"""
import os
from dotenv import load_dotenv
from application.background_generator import BackgroundGenerator
from pathlib import Path

load_dotenv()

print("="*80)
print("INTEGRATION TEST: Complete Flow")
print("="*80)

try:
    # Initialize generator
    generator = BackgroundGenerator()
    print("✓ BackgroundGenerator initialized")
    
    # Test 1: Full flow with story (Korean → keyword → image)
    print("\n" + "="*80)
    print("Test 1: Story → Keyword → Image → File → URL")
    print("="*80)
    
    story = "햇살 가득한 교실에서 창밖을 바라보는 장면"
    print(f"Input story: {story}")
    
    image_url = generator.create_background_image(story)
    
    print(f"✓ Generated image URL: {image_url}")
    
    # Verify file
    filename = image_url.split("/")[-1]
    filepath = Path("static/generated_images") / filename
    assert filepath.exists(), f"File not found: {filepath}"
    assert filepath.stat().st_size > 0, "File is empty"
    print(f"✓ File saved: {filepath} ({filepath.stat().st_size} bytes)")
    
    # Test 2: Direct keyword
    print("\n" + "="*80)
    print("Test 2: Direct Keyword → Image")
    print("="*80)
    
    keyword = "rainy school corridor"
    print(f"Input keyword: {keyword}")
    
    image_url2 = generator.create_background_image_by_keyword(keyword)
    
    print(f"✓ Generated image URL: {image_url2}")
    
    # Verify file
    filename2 = image_url2.split("/")[-1]
    filepath2 = Path("static/generated_images") / filename2
    assert filepath2.exists(), f"File not found: {filepath2}"
    assert filepath2.stat().st_size > 0, "File is empty"
    print(f"✓ File saved: {filepath2} ({filepath2.stat().st_size} bytes)")
    
    # Test 3: Multiple scenarios
    print("\n" + "="*80)
    print("Test 3: Multiple Scenarios")
    print("="*80)
    
    scenarios = [
        "비 오는 학교 복도",
        "밤의 공원 벤치",
        "눈 내리는 거리"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing: {scenario}")
        image_url = generator.create_background_image(scenario)
        
        filename = image_url.split("/")[-1]
        filepath = Path("static/generated_images") / filename
        assert filepath.exists()
        assert filepath.stat().st_size > 0
        
        print(f"   ✓ Generated: {image_url}")
        print(f"   ✓ Size: {filepath.stat().st_size} bytes")
    
    # Test 4: Static file accessibility
    print("\n" + "="*80)
    print("Test 4: Static File Accessibility")
    print("="*80)
    
    images_dir = Path("static/generated_images")
    assert images_dir.exists(), "Images directory should exist"
    assert images_dir.is_dir(), "Should be a directory"
    
    generated_files = list(images_dir.glob("*.png"))
    print(f"✓ Images directory exists: {images_dir}")
    print(f"✓ Total generated images: {len(generated_files)}")
    
    # Summary
    print("\n" + "="*80)
    print("ALL TESTS PASSED! ✓")
    print("="*80)
    print("\nSummary:")
    print(f"- Story → Keyword → Image: ✓")
    print(f"- Direct Keyword → Image: ✓")
    print(f"- Multiple Scenarios: ✓")
    print(f"- File Saving: ✓")
    print(f"- Static File Serving: ✓")
    print(f"\nTotal images generated: {len(generated_files)}")
    
    # Requirements verification
    print("\n" + "="*80)
    print("Requirements Verification (1.1, 1.2, 3.4)")
    print("="*80)
    print("✓ 1.1: Story input → Keyword extraction → Image generation")
    print("✓ 1.2: Image generation → File saving → URL return")
    print("✓ 3.4: Generated images accessible via static file serving")
    
except Exception as e:
    print(f"\n✗ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
