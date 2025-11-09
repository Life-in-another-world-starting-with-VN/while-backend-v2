from google import genai
import os
from dotenv import load_dotenv
import requests

load_dotenv()


class BackgroundGenerator:
    def __init__(self):
        self.__fal_key = os.getenv("FAL_KEY")
        self.__fal_url = os.getenv("FAL_URL")
        self.__immage_size = os.getenv("IMAGE_SIZE")

        GEMINI_API_KEY = os.getenv("GEMINI_TOKEN")
        self.__client = genai.Client(api_key=GEMINI_API_KEY)
        self.gemini_model = os.getenv("GEMINI_MODEL")

    def create_background_image(self, story: str) -> str:
        prompt = self.__set_prompt(story)
        background_search_keyword = self.__get_search_word(prompt)
        print(f"Background keyword: {background_search_keyword}")

        return self.create_background_image_by_keyword(background_search_keyword)

    def create_background_image_by_keyword(self, keyword: str) -> str:
        background_image = self.__create_background_image(keyword)

        return background_image

    def __set_prompt(self, story: str) -> str:
        return (
            "미연시 게임 배경 이미지를 생성할 영어 검색어가 필요합니다.\n"
            f"장면 설명: {story}\n\n"
            "이 장면의 장소, 날씨, 분위기를 정확히 반영한 영어 검색어를 만들어주세요.\n"
            "날씨가 중요한 경우 반드시 포함하세요 (rainy, sunny, cloudy, snowy 등).\n"
            "응답은 검색어만 영어로! 설명 금지!\n\n"
            "예시:\n"
            "- 소나기 → rainy school corridor\n"
            "- 교실 → sunny classroom\n"
            "- 밤 공원 → night park\n"
            "- 눈 내리는 거리 → snowy street\n\n"
            "검색어:"
        )

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
        prompt = f"{background_search_keyword}, {image_style}, {self.__immage_size}, ultra detail, no people, environment background"

        payload = {"prompt": prompt, "aspect_ratio": f"{self.__immage_size}"}

        headers = {
            "Authorization": f"Key {self.__fal_key}",
            "Content-Type": "application/json",
        }

        res = requests.post(self.__fal_url, headers=headers, json=payload)
        res.raise_for_status()

        image_url = res.json()["images"][0]["url"]

        return image_url
