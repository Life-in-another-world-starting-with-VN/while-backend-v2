"""Check available image generation models"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_TOKEN"))

print("이미지 생성 가능한 모델 확인 중...\n")

models = client.models.list()
image_models = [m for m in models if 'image' in m.name.lower() or 'imagen' in m.name.lower()]

print(f"발견된 이미지 모델: {len(image_models)}개\n")

for model in image_models:
    print(f"✓ {model.name}")
    if hasattr(model, 'description'):
        print(f"  설명: {model.description}")
    print()
