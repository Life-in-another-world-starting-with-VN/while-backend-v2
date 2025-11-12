"""Verify all generated images have 16:9 aspect ratio"""
from pathlib import Path
from PIL import Image

images_dir = Path("static/generated_images")
png_files = list(images_dir.glob("*.png"))

print("="*80)
print(f"Verifying {len(png_files)} images for 16:9 aspect ratio")
print("="*80)

target_ratio = 16 / 9
tolerance = 0.01

all_pass = True

for filepath in png_files:
    img = Image.open(filepath)
    width, height = img.size
    ratio = width / height
    
    is_correct = abs(ratio - target_ratio) < tolerance
    status = "✓" if is_correct else "✗"
    
    print(f"{status} {filepath.name}: {width}x{height} (ratio: {ratio:.4f})")
    
    if not is_correct:
        all_pass = False

print("="*80)
if all_pass:
    print("✓ ALL IMAGES HAVE CORRECT 16:9 ASPECT RATIO!")
else:
    print("✗ Some images do not have 16:9 aspect ratio")
print("="*80)
