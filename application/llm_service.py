from google import genai
import os
import json
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """Gemini를 사용한 게임 스토리 생성 서비스"""

    def __init__(self):
        GEMINI_API_KEY = os.getenv("GEMINI_TOKEN")
        self.__client = genai.Client(api_key=GEMINI_API_KEY)
        self.gemini_model = os.getenv("GEMINI_MODEL")

    def generate_game_structure(
        self, personality: str, genre: str, playtime: int, characters: List[Dict]
    ) -> Dict:
        """
        게임 초기 구조 생성 (제목, 첫 세션 내용, 첫 씬)
        """
        characters_info = "\n".join(
            [
                f"- ID {char['id']}: {char['name']} - {char['personality']}"
                for char in characters
            ]
        )

        prompt = f"""당신은 미연시 게임 스토리 작가입니다.

다음 정보를 바탕으로 미연시 게임을 설계해주세요:
- 원하는 성격: {personality}
- 장르: {genre}
- 플레이 시간: {playtime}분
- 등장 캐릭터:
{characters_info}

다음 JSON 형식으로 응답해주세요:
{{
    "title": "게임 제목",
    "main_character_id": 선택한_메인_캐릭터_ID숫자,
    "main_character_name": "선택한_캐릭터의_정확한_이름",
    "first_session_content": "첫 번째 세션 설명 (장소와 상황을 명확히)",
    "first_scene": {{
        "role": "선택한_캐릭터의_정확한_이름",
        "type": "dialogue",
        "dialogue": "첫 대사",
        "character_id": 메인_캐릭터_ID숫자,
        "emotion": "표정"
    }}
}}

중요 규칙:
1. **메인 캐릭터 선택 (매우 중요!)**:
   - 위 캐릭터 목록에서 사용자가 원하는 성격 "{personality}"과 가장 잘 맞는 캐릭터 1명을 선택하세요
   - 선택한 캐릭터의 ID를 main_character_id에 입력하세요
   - **선택한 캐릭터의 이름을 main_character_name에 정확히 입력하세요 (위 목록의 이름 그대로)**
   - 이 캐릭터가 게임 전체에서 메인 캐릭터로 등장합니다
2. 세션은 동적으로 생성되므로 first_session_content만 작성
3. **first_session_content 작성 규칙 (매우 중요!)**:
   - 반드시 **구체적인 장소명**을 포함하세요
   - 형식: "장소명. 그 장소의 분위기와 상황"
   - 예시 (좋음): "학교 옥상. 시원한 바람이 부는 점심시간"
   - 예시 (좋음): "도서관. 조용한 분위기 속에서 책 읽는 학생들이 보인다"
   - 예시 (나쁨): "학교 건물 어딘가" (X - 구체적인 장소가 아님!)
4. **첫 씬은 반드시 메인 캐릭터의 dialogue로 시작**:
   - role은 선택한 메인 캐릭터의 이름 (위 목록의 이름 그대로, 절대 변경하지 마세요!)
   - character_id는 선택한 메인 캐릭터의 ID
   - emotion은 다음 중 하나: anger, blush, embarrassed, laugh, sad, smile, surprise, thinking, worry, 또는 빈 문자열(기본 표정)
5. 응답은 반드시 유효한 JSON 형식이어야 합니다
6. JSON만 출력하고 다른 설명은 하지 마세요"""

        response = self.__client.models.generate_content(
            model=self.gemini_model,
            contents=[prompt],
        )

        response_text = response.candidates[0].content.parts[0].text.strip()

        # JSON 추출 (마크다운 코드 블록 제거)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)

    def generate_next_scene(
        self,
        game_context: Dict,
        current_session_content: str,
        scene_history: List[Dict],
        emotion: Dict[str, int],
        elapsed_time: int,
        total_playtime: int,
        characters: List[Dict],
        main_character_id: int,
    ) -> Tuple[Dict, bool, Optional[str]]:
        """
        다음 씬 생성

        Returns:
            Tuple[Dict, bool, Optional[str]]: (씬 데이터, 세션 종료 여부, 새 세션 내용)
        """
        # 메인 캐릭터 정보 추출
        main_character = next((char for char in characters if char['id'] == main_character_id), None)
        main_character_name = main_character['name'] if main_character else "Unknown"
        
        characters_info = "\n".join(
            [f"- ID {char['id']}: {char['name']} - {char['personality']}" for char in characters]
        )

        # 감정 분석
        dominant_emotion = max(emotion.items(), key=lambda x: x[1])
        emotion_str = f"{dominant_emotion[0]} ({dominant_emotion[1]}%)"

        # 시간 진행도
        time_progress = (elapsed_time / (total_playtime * 60)) * 100 if total_playtime > 0 else 0
        remaining_time = (total_playtime * 60) - elapsed_time

        # 현재 장소 추출 (세션 내용에서)
        current_location = current_session_content.split("장소:")[0].strip() if "장소:" not in current_session_content else current_session_content

        # 현재 세션의 씬 개수 계산 (scene_history는 현재 세션의 씬들만 포함)
        current_session_scene_count = len(scene_history)

        # 현재 세션의 모든 대화 히스토리
        current_session_history = "\n".join(
            [
                f"[씬 {i+1}] {scene['role']}: {scene.get('dialogue', '') or '(선택지)'}"
                for i, scene in enumerate(scene_history)
            ]
        )

        prompt = f"""당신은 미연시 게임 스토리 작가입니다. 빠른 전개와 흥미로운 스토리를 만드는 것이 목표입니다.

게임 정보:
- 제목: {game_context['title']}
- 장르: {game_context['genre']}
- 캐릭터 성격: {game_context['personality']}

등장 캐릭터:
{characters_info}
* narrator: 나레이션 역할

**현재 세션 (현재 장소)**: {current_session_content}
**현재 세션의 씬 개수**: {current_session_scene_count}개

**현재 세션의 전체 대화 흐름**:
{current_session_history}

사용자 감정: {emotion_str}
게임 진행도: {time_progress:.1f}% (남은 시간: {remaining_time}초)

다음 씬을 생성해주세요. JSON 형식으로만 응답하세요:

{{
    "scene": {{
        "role": "{main_character_name} or user or narrator",
        "type": "dialogue or selection",
        "dialogue": "대사 내용 (type이 dialogue인 경우)",
        "selections": {{
            "1": "선택지 1",
            "2": "선택지 2"
        }},
        "character_id": {main_character_id} (캐릭터가 말하는 경우만, user/narrator면 null),
        "emotion": "표정" (캐릭터가 말하는 경우만, user/narrator면 null)
    }},
    "session_ended": false,
    "new_session_content": null
}}

중요 규칙:
1. **메인 캐릭터 고정 (매우 중요!)**:
   - 캐릭터가 등장하는 씬에서는 **반드시 메인 캐릭터만 사용**하세요
   - role에는 정확히 "{main_character_name}" 사용 (절대 변경하지 마세요!)
   - character_id는 항상 {main_character_id}
   - 다른 캐릭터는 절대 등장시키지 마세요
   - narrator는 사용 가능하지만, 캐릭터 대사는 항상 메인 캐릭터만

2. **빠른 전개**: 한 세션은 3-5개 정도의 짧은 씬으로 구성하세요
   - **중요!** 현재 씬 개수가 3개 이상이면 장소 이동이나 상황 변화를 적극적으로 고려
   - 현재 세션의 전체 대화 흐름을 보고 같은 이야기가 반복되지 않도록 하세요
   - 같은 장소에서 너무 오래 머물지 마세요
   - 대화만 길게 이어가지 말고, 행동이나 이벤트를 통해 스토리를 전개하세요
   - 이미 나온 주제나 대화는 반복하지 마세요

3. **선택지 활용**: 2-3개 씬마다 선택지를 제공하여 사용자 참여 유도
   - 선택지는 스토리에 영향을 주는 의미있는 선택이어야 함
   - 단순한 yes/no가 아닌 다양한 행동 옵션 제공
   - 장소 이동 관련 선택지를 적극 활용

4. **감정 반영**: 사용자 감정을 고려하여 스토리를 조정하세요
   - happy가 높으면: 긍정적인 이벤트, 로맨틱한 분위기
   - sad가 높으면: 위로하는 대화, 감동적인 장면
   - angry가 높으면: 갈등 해소, 카타르시스

5. **시간 관리**:
   - 남은 시간 50% 이상: 관계 형성, 캐릭터 소개
   - 남은 시간 30-50%: 본격적인 이벤트, 갈등 또는 친밀감 형성
   - 남은 시간 10-30%: 클라이맥스, 중요한 선택
   - 남은 시간 10% 이하: 엔딩으로 유도

6. **장소 변경 감지**:
   - 대화에서 "~로 가자", "~에 가볼까", "이동하자" 등의 이동 언급 시 session_ended=true
   - **중요!** 현재 씬 개수가 4개 이상이면 자연스러운 장소 전환을 적극 고려
   - **new_session_content 작성 규칙 (매우 중요!)**:
     * 반드시 **최종 도착 장소**만 작성하세요
     * 이동 과정(복도, 길, 계단 등)은 절대 작성하지 마세요
     * 형식: "최종 도착 장소명. 그 장소의 분위기와 상황"
     * 예시 (좋음): "보건실. 하얀 침대와 약 냄새가 나는 조용한 공간"
     * 예시 (나쁨): "보건실로 가는 복도" (X - 이동 과정은 안 됨!)

7. **현재 장소**: {current_location} - 이 장소와 다른 곳으로 이동하면 새 세션 시작

8. **캐릭터 표정 규칙**:
   - 메인 캐릭터가 말하는 경우 반드시 character_id={main_character_id}와 emotion 포함
   - emotion은 다음 중 하나: anger, blush, embarrassed, laugh, sad, smile, surprise, thinking, worry, 또는 빈 문자열(기본 표정)
   - user나 narrator인 경우 character_id와 emotion은 null

9. type이 "selection"이면 role은 "user", dialogue는 null
10. type이 "dialogue"면 selections는 null 또는 빈 객체
11. JSON만 출력하고 다른 설명은 하지 마세요"""

        response = self.__client.models.generate_content(
            model=self.gemini_model,
            contents=[prompt],
        )

        response_text = response.candidates[0].content.parts[0].text.strip()

        # JSON 추출
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result = json.loads(response_text)

        scene = result["scene"]
        session_ended = result.get("session_ended", False)
        new_session_content = result.get("new_session_content")

        return scene, session_ended, new_session_content

    def generate_scene_after_selection(
        self,
        game_context: Dict,
        current_session_content: str,
        scene_history: List[Dict],
        selected_option: str,
        emotion: Dict[str, int],
        elapsed_time: int,
        total_playtime: int,
        characters: List[Dict],
        main_character_id: int,
    ) -> Tuple[Dict, bool, Optional[str]]:
        """
        선택지 선택 후 다음 씬 생성
        """
        # 메인 캐릭터 정보 추출
        main_character = next((char for char in characters if char['id'] == main_character_id), None)
        main_character_name = main_character['name'] if main_character else "Unknown"
        
        characters_info = "\n".join(
            [f"- ID {char['id']}: {char['name']} - {char['personality']}" for char in characters]
        )

        # 감정 분석
        dominant_emotion = max(emotion.items(), key=lambda x: x[1])
        emotion_str = f"{dominant_emotion[0]} ({dominant_emotion[1]}%)"

        # 시간 진행도
        time_progress = (elapsed_time / (total_playtime * 60)) * 100 if total_playtime > 0 else 0
        remaining_time = (total_playtime * 60) - elapsed_time

        # 현재 장소 추출 (세션 내용에서)
        current_location = current_session_content.split("장소:")[0].strip() if "장소:" not in current_session_content else current_session_content

        # 현재 세션의 씬 개수 계산 (scene_history는 현재 세션의 씬들만 포함)
        current_session_scene_count = len(scene_history)

        # 현재 세션의 모든 대화 히스토리
        current_session_history = "\n".join(
            [
                f"[씬 {i+1}] {scene['role']}: {scene.get('dialogue', '') or '(선택지)'}"
                for i, scene in enumerate(scene_history)
            ]
        )

        # 바로 이전 씬 정보 (맥락 유지용)
        previous_scene_context = ""
        if len(scene_history) >= 2:
            prev_scene = scene_history[-2]
            previous_scene_context = f"직전 씬: [{prev_scene['role']}] {prev_scene.get('dialogue', '(선택지)')}"

        prompt = f"""당신은 미연시 게임 스토리 작가입니다. 빠른 전개와 흥미로운 스토리를 만드는 것이 목표입니다.

게임 정보:
- 제목: {game_context['title']}
- 장르: {game_context['genre']}
- 캐릭터 성격: {game_context['personality']}

**메인 캐릭터 (이 게임의 주인공)**: 
- ID: {main_character_id}
- 이름: {main_character_name} (이 이름을 정확히 사용하세요!)

등장 캐릭터:
{characters_info}
* narrator: 나레이션 역할

**현재 세션 (현재 장소)**: {current_session_content}
**현재 세션의 씬 개수**: {current_session_scene_count}개

**현재 세션의 전체 대화 흐름**:
{current_session_history}

{previous_scene_context}

**사용자가 선택한 행동: "{selected_option}"**

사용자 감정: {emotion_str}
게임 진행도: {time_progress:.1f}% (남은 시간: {remaining_time}초)

사용자의 선택에 대한 캐릭터의 반응을 생성해주세요. JSON 형식으로만 응답하세요:

{{
    "scene": {{
        "role": "{main_character_name} or narrator",
        "type": "dialogue",
        "dialogue": "캐릭터의 반응 대사",
        "character_id": {main_character_id} (캐릭터가 말하는 경우만, narrator면 null),
        "emotion": "표정" (캐릭터가 말하는 경우만, narrator면 null)
    }},
    "session_ended": false,
    "new_session_content": null
}}

중요 규칙:
1. **메인 캐릭터 고정 (매우 중요!)**:
   - 캐릭터가 등장하는 씬에서는 **반드시 메인 캐릭터만 사용**하세요
   - role에는 정확히 "{main_character_name}" 사용 (절대 변경하지 마세요!)
   - character_id는 항상 {main_character_id}
   - 다른 캐릭터는 절대 등장시키지 마세요
   - narrator는 사용 가능하지만, 캐릭터 대사는 항상 메인 캐릭터만

2. **맥락 유지 - 매우 중요!**:
   - 사용자가 선택한 행동 "{selected_option}"에 **직접적으로** 반응하세요
   - 현재 세션의 전체 대화 흐름을 보고 같은 이야기가 반복되지 않도록 하세요
   - 바로 직전 대화의 흐름을 **반드시** 이어받으세요
   - 갑자기 다른 주제로 넘어가거나 무관한 이야기를 하지 마세요
   - 선택지와 관련 없는 내용을 말하면 안 됩니다!

   예시:
   - 선택: "같이 점심 먹으러 갈까?" → 반응: "좋아! 어디 갈까?" (O)
   - 선택: "같이 점심 먹으러 갈까?" → 반응: "오늘 날씨 좋네!" (X - 맥락 파괴)

3. **자연스러운 반응**:
   - 선택지 이후는 항상 메인 캐릭터나 나레이터의 dialogue로 반응
   - 메인 캐릭터의 성격에 맞는 반응
   - 감정 표현이 자연스럽게

4. **빠른 전개**:
   - 한 세션은 3-5개 정도의 짧은 씬으로 구성
   - 현재 씬 개수가 3개 이상이면 장소 이동이나 상황 변화 고려
   - 같은 주제로 너무 오래 대화하지 마세요
   - 이미 나온 대화나 주제는 반복하지 마세요

5. **감정 반영**: 사용자 감정 {emotion_str}를 고려한 반응

6. **시간 관리**:
   - 남은 시간 30% 이하: 스토리 마무리 방향
   - 남은 시간 10% 이하: 엔딩으로 유도

7. **장소 변경 감지**:
   - 선택이 장소 이동 관련이면 (예: "도서관으로 가자", "카페 갈까?") session_ended=true
   - 반응: 나레이터가 이동을 설명하고 새 장소 분위기 묘사
   - **new_session_content 작성 규칙 (매우 중요!)**:
     * 반드시 **최종 도착 장소**만 작성하세요
     * 이동 과정(복도, 길, 계단 등)은 절대 작성하지 마세요
     * 형식: "최종 도착 장소명. 그 장소의 분위기와 상황"
     * 예시 (좋음): "보건실. 하얀 침대와 약 냄새가 나는 조용한 공간"
     * 예시 (나쁨): "보건실로 가는 복도" (X - 이동 과정은 안 됨!)
   - **중요!** 현재 씬 개수가 4개 이상이고 자연스러운 이동 타이밍이면 전환 고려

8. **현재 장소**: {current_location} - 선택으로 인해 다른 곳으로 이동하면 새 세션 시작

9. **캐릭터 표정 규칙**:
   - 메인 캐릭터가 말하는 경우 반드시 character_id={main_character_id}와 emotion 포함
   - emotion은 다음 중 하나: anger, blush, embarrassed, laugh, sad, smile, surprise, thinking, worry, 또는 빈 문자열(기본 표정)
   - narrator인 경우 character_id와 emotion은 null

9. JSON만 출력하고 다른 설명은 하지 마세요"""

        response = self.__client.models.generate_content(
            model=self.gemini_model,
            contents=[prompt],
        )

        response_text = response.candidates[0].content.parts[0].text.strip()

        # JSON 추출
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result = json.loads(response_text)

        scene = result["scene"]
        session_ended = result.get("session_ended", False)
        new_session_content = result.get("new_session_content")

        return scene, session_ended, new_session_content
