from google import genai
import os
from dotenv import load_dotenv
from pathlib import Path
import base64
import uuid
import logging
import requests
from PIL import Image
import io
import re
from datetime import datetime
from typing import List, Optional

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class BackgroundGenerator:
    def __init__(self):
        # Google AI client setup
        GEMINI_API_KEY = os.getenv("GEMINI_TOKEN")
        
        # API 키 누락 시 명확한 에러 메시지
        if not GEMINI_API_KEY:
            error_msg = "GEMINI_TOKEN environment variable is required. Please set your Google AI API key."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            self.__client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            error_msg = f"Failed to initialize Google AI client: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        self.gemini_model = os.getenv("GEMINI_MODEL")
        
        # Image generation model
        self.__image_model = os.getenv("IMAGE_MODEL", "imagen-3.0-generate-001")
        self.__api_key = GEMINI_API_KEY
        
        # Image settings
        self.__immage_size = os.getenv("IMAGE_SIZE")
        
        # Image storage directory
        self.__images_dir = Path("static/generated_images")
        try:
            self.__images_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            error_msg = f"Failed to create image storage directory: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def get_existing_images(self) -> List[str]:
        """저장된 이미지 파일 목록 반환 (키워드 부분만)"""
        existing_images = []
        for file in self.__images_dir.glob("*.png"):
            # 파일명에서 타임스탬프 제거하고 키워드만 추출
            # 예: rainy_school_corridor_20251114_153045.png -> rainy_school_corridor
            filename = file.stem  # 확장자 제거
            # 마지막 타임스탬프 부분 제거 (YYYYMMDD_HHMMSS 패턴)
            keyword = re.sub(r'_\d{8}_\d{6}$', '', filename)
            if keyword:
                existing_images.append(keyword)
        return existing_images

    def find_matching_image(self, keyword: str) -> Optional[str]:
        """키워드와 일치하는 기존 이미지 찾기"""
        clean_keyword = re.sub(r'[^\w\s-]', '', keyword)
        clean_keyword = re.sub(r'[\s]+', '_', clean_keyword)
        clean_keyword = clean_keyword[:50]
        
        # 정확히 일치하는 파일 찾기
        for file in self.__images_dir.glob(f"{clean_keyword}_*.png"):
            image_url = f"/static/generated_images/{file.name}"
            logger.info(f"Found existing image for keyword '{keyword}': {file.name}")
            return image_url
        
        return None

    def create_background_image(self, story: str) -> str:
        # 기존 이미지 목록 가져오기
        existing_images = self.get_existing_images()
        
        # LLM에게 기존 이미지 목록 전달하여 키워드 생성
        prompt = self.__set_prompt(story, existing_images)
        background_search_keyword = self.__get_search_word(prompt)
        print(f"Background keyword: {background_search_keyword}")

        return self.create_background_image_by_keyword(background_search_keyword)

    def create_background_image_by_keyword(self, keyword: str) -> str:
        # 먼저 기존 이미지 확인
        existing_image = self.find_matching_image(keyword)
        if existing_image:
            print(f"Reusing existing image: {existing_image}")
            return existing_image
        
        # 없으면 새로 생성
        print(f"Generating new image for: {keyword}")
        background_image = self.__create_background_image(keyword)

        return background_image

    def __set_prompt(self, story: str, existing_images: List[str] = None) -> str:
        base_prompt = (
            "미연시 게임 배경 이미지를 생성할 영어 검색어가 필요합니다.\n"
            f"장면 설명: {story}\n\n"
        )
        
        # 기존 이미지 목록이 있으면 추가
        if existing_images:
            base_prompt += (
                "이미 생성된 배경 이미지 목록:\n"
                f"{', '.join(existing_images)}\n\n"
                "위 목록에 있는 배경과 유사하다면 정확히 같은 검색어를 사용하세요.\n"
                "!!!(매우중요)!!! : 기존이미지를 사용할때는 이미 생성된 배경 이미지 목록에 있는 이름과 100% 동일하도록 구성하세요."
                "완전히 다른 장면이라면 새로운 검색어를 만드세요.\n\n"
            )
        
        base_prompt += (
            "- 새로운 검색어 생성 방법"
            "   이 장면의 장소, 날씨, 분위기를 정확히 반영한 영어 검색어를 만들어주세요.\n"
            "   날씨가 중요한 경우 반드시 포함하세요 (rainy, sunny, cloudy, snowy 등).\n"
            "   응답은 검색어만 영어로! 설명 금지!\n\n"
            "   예시:\n"
            "   - 소나기가 내리는 학교 → rainy school corridor\n"
            "   - 화창한 교실 → sunny classroom\n"
            "   - 밤 공원 → night park\n"
            "   - 눈 내리는 거리 → snowy street\n\n"
            "가능하다면 기존 이미지를 사용할 수 있도록 해주고 없다면 배경 이미지 생성을 해줘"
        )
        
        return base_prompt

    def __get_search_word(self, prompt: str) -> str:
        response = self.__client.models.generate_content(
            model=self.gemini_model,
            contents=[prompt],
        )

        return response.candidates[0].content.parts[0].text.strip()

    def __create_background_image(self, background_search_keyword):
        image_style = """
        visual novel style,
        clean line art,
        Makoto Shinkai-inspired sky,
        studio-quality anime background,
        romantic visual novel scene,
        NO PEOPLE,
        NO CHARACTERS,
        environment only,
        empty scene
        """
        
        # Add aspect ratio to prompt (16:9 widescreen format)
        aspect_ratio_instruction = "16:9 widescreen aspect ratio, horizontal landscape orientation"
        full_prompt = f"{background_search_keyword}, {image_style}, {aspect_ratio_instruction}, ultra detail, no people, environment background"

        logger.info(f"Generating background image for keyword: {background_search_keyword}")
        logger.debug(f"Full prompt: {full_prompt}")

        # 이미지 생성 실패 시 예외 처리 및 로깅
        try:
            # Generate image using gemini-2.5-flash-image via REST API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.__image_model}:generateContent"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": full_prompt
                    }]
                }],
                "generationConfig": {
                    "responseModalities": ["IMAGE"]
                }
            }
            
            params = {
                "key": self.__api_key
            }
            
            response = requests.post(url, headers=headers, json=payload, params=params, timeout=60)
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", {}).get("message", response.text)
                
                # API 키 인증 에러 처리
                if response.status_code in [401, 403]:
                    error_msg = f"Google AI authentication failed. Please check your API key: {error_msg}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # 일반 이미지 생성 실패
                error_msg = f"Failed to generate background image (HTTP {response.status_code}): {error_msg}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            response_data = response.json()
            
        except requests.exceptions.Timeout:
            error_msg = "Image generation request timed out after 60 seconds"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while generating image: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except ValueError as e:
            # Re-raise authentication errors
            raise
        except Exception as e:
            error_msg = f"Failed to generate background image: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Extract generated image data from response
        try:
            candidates = response_data.get("candidates", [])
            if not candidates:
                error_msg = "No candidates in API response"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                error_msg = "No parts in API response"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # Find the part with inline_data (image)
            image_base64 = None
            for part in parts:
                if "inlineData" in part:
                    image_base64 = part["inlineData"].get("data")
                    break
            
            if not image_base64:
                error_msg = "No image data in API response"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
        except (KeyError, IndexError) as e:
            error_msg = f"Failed to parse API response: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Generate filename with keyword and timestamp
        # Clean keyword for filename (remove special chars, limit length)
        clean_keyword = re.sub(r'[^\w\s-]', '', background_search_keyword)
        clean_keyword = re.sub(r'[\s]+', '_', clean_keyword)
        clean_keyword = clean_keyword[:50]  # Limit length
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_keyword}_{timestamp}.png"
        filepath = self.__images_dir / filename
        
        # 파일 저장 실패 시 에러 처리
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_base64)
            
            # Open image with PIL to crop to 16:9
            img = Image.open(io.BytesIO(image_bytes))
            original_width, original_height = img.size
            
            logger.info(f"Original image size: {original_width}x{original_height}")
            
            # Calculate 16:9 dimensions
            target_ratio = 16 / 9
            current_ratio = original_width / original_height
            
            if abs(current_ratio - target_ratio) > 0.01:  # If not already 16:9
                # Crop to 16:9 from center
                if current_ratio > target_ratio:
                    # Image is wider, crop width
                    new_width = int(original_height * target_ratio)
                    left = (original_width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, original_height))
                else:
                    # Image is taller, crop height
                    new_height = int(original_width / target_ratio)
                    top = (original_height - new_height) // 2
                    img = img.crop((0, top, original_width, top + new_height))
                
                logger.info(f"Cropped to 16:9: {img.size[0]}x{img.size[1]}")
            
            # Save as PNG
            img.save(filepath, "PNG")
            
            logger.info(f"Image saved successfully: {filename}")
        except Exception as e:
            error_msg = f"Failed to save image file to {filepath}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        # Return URL path for the saved image
        image_url = f"/static/generated_images/{filename}"
        return image_url
