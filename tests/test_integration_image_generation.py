"""
Integration test for Google AI image generation flow.
Tests: Story input → Keyword extraction → Image generation → File saving → URL return
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from application.background_generator import BackgroundGenerator

# Load environment variables
load_dotenv()

def test_full_flow_with_story():
    """Test complete flow: story → keyword → image → file → URL"""
    print("\n" + "="*80)
    print("통합 테스트: 전체 플로우 테스트")
    print("="*80)
    
    # Initialize generator
    generator = BackgroundGenerator()
    
    # Test story
    story = "햇살 가득한 교실에서 창밖을 바라보는 장면"
    
    print(f"\n입력 스토리: {story}")
    
    # Execute full flow
    image_url = generator.create_background_image(story)
    
    print(f"\n생성된 이미지 URL: {image_url}")
    
    # Verify URL format
    assert image_url.startswith("/static/generated_images/"), \
        f"URL이 '/static/generated_images/'로 시작해야 합니다. 받은 값: {image_url}"
    assert image_url.endswith(".png"), \
        f"URL이 '.png'로 끝나야 합니다. 받은 값: {image_url}"
    
    # Verify file exists
    filename = image_url.split("/")[-1]
    filepath = Path("static/generated_images") / filename
    assert filepath.exists(), f"이미지 파일이 존재하지 않습니다: {filepath}"
    assert filepath.stat().st_size > 0, "이미지 파일이 비어있습니다"
    
    print(f"✓ 이미지 파일 저장 성공: {filepath}")
    print(f"✓ 파일 크기: {filepath.stat().st_size} bytes")
    print("\n" + "="*80)
    print("✓ 전체 플로우 테스트 성공!")
    print("="*80)

def test_keyword_flow():
    """Test flow with direct keyword: keyword → image → file → URL"""
    print("\n" + "="*80)
    print("통합 테스트: 키워드 플로우 테스트")
    print("="*80)
    
    # Initialize generator
    generator = BackgroundGenerator()
    
    # Test keyword
    keyword = "sunny classroom"
    
    print(f"\n입력 키워드: {keyword}")
    
    # Execute keyword flow
    image_url = generator.create_background_image_by_keyword(keyword)
    
    print(f"\n생성된 이미지 URL: {image_url}")
    
    # Verify URL format
    assert image_url.startswith("/static/generated_images/"), \
        f"URL이 '/static/generated_images/'로 시작해야 합니다. 받은 값: {image_url}"
    assert image_url.endswith(".png"), \
        f"URL이 '.png'로 끝나야 합니다. 받은 값: {image_url}"
    
    # Verify file exists
    filename = image_url.split("/")[-1]
    filepath = Path("static/generated_images") / filename
    assert filepath.exists(), f"이미지 파일이 존재하지 않습니다: {filepath}"
    assert filepath.stat().st_size > 0, "이미지 파일이 비어있습니다"
    
    print(f"✓ 이미지 파일 저장 성공: {filepath}")
    print(f"✓ 파일 크기: {filepath.stat().st_size} bytes")
    print("\n" + "="*80)
    print("✓ 키워드 플로우 테스트 성공!")
    print("="*80)

def test_static_file_accessibility():
    """Test that generated images are accessible via static file serving"""
    print("\n" + "="*80)
    print("통합 테스트: 정적 파일 접근성 테스트")
    print("="*80)
    
    # Initialize generator
    generator = BackgroundGenerator()
    
    # Generate an image
    keyword = "rainy street"
    print(f"\n입력 키워드: {keyword}")
    
    image_url = generator.create_background_image_by_keyword(keyword)
    
    print(f"\n생성된 URL: {image_url}")
    
    # Verify the file path structure matches FastAPI static files setup
    assert image_url.startswith("/static/"), \
        "URL은 FastAPI 정적 파일을 위해 /static/으로 시작해야 합니다"
    
    # Verify file exists in the correct directory
    relative_path = image_url.lstrip("/")  # Remove leading slash
    filepath = Path(relative_path)
    assert filepath.exists(), \
        f"정적 파일 서빙을 위해 파일이 {filepath}에 존재해야 합니다"
    
    print(f"✓ 파일 접근 가능: {filepath}")
    print(f"✓ 정적 파일 서빙 경로 확인 완료")
    print("\n" + "="*80)
    print("✓ 정적 파일 접근성 테스트 성공!")
    print("="*80)

if __name__ == "__main__":
    import time
    
    passed_tests = []
    failed_tests = []
    
    # Test 1: Full flow with story
    try:
        test_full_flow_with_story()
        passed_tests.append("스토리 입력 → 키워드 추출 → 이미지 생성 → 파일 저장 → URL 반환")
        time.sleep(2)  # Wait between API calls
    except Exception as e:
        failed_tests.append(("전체 플로우 테스트", str(e)))
    
    # Test 2: Keyword flow
    try:
        test_keyword_flow()
        passed_tests.append("키워드 직접 입력 → 이미지 생성 → 파일 저장 → URL 반환")
        time.sleep(2)  # Wait between API calls
    except Exception as e:
        failed_tests.append(("키워드 플로우 테스트", str(e)))
    
    # Test 3: Static file accessibility
    try:
        test_static_file_accessibility()
        passed_tests.append("생성된 이미지가 정적 파일로 접근 가능")
    except Exception as e:
        failed_tests.append(("정적 파일 접근성 테스트", str(e)))
    
    # Print summary
    print("\n" + "="*80)
    print("테스트 결과 요약")
    print("="*80)
    
    if passed_tests:
        print(f"\n✓ 성공한 테스트 ({len(passed_tests)}개):")
        for test in passed_tests:
            print(f"  ✓ {test}")
    
    if failed_tests:
        print(f"\n✗ 실패한 테스트 ({len(failed_tests)}개):")
        for test_name, error in failed_tests:
            print(f"  ✗ {test_name}")
            print(f"    이유: {error[:100]}...")
    
    print("\n" + "="*80)
    
    if not failed_tests:
        print("🎉 모든 통합 테스트 성공!")
        print("="*80 + "\n")
        exit(0)
    else:
        print(f"⚠️  {len(passed_tests)}/{len(passed_tests) + len(failed_tests)} 테스트 통과")
        print("="*80 + "\n")
        exit(1)
