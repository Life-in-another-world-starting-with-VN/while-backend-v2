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
4. **첫 씬 규칙**:
   - role은 선택한 캐릭터의 이름 (위 목록의 이름 그대로, 절대 변경하지 마세요!) 또는 narrator(나레이션 역할)
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

        prompt = f"""당신은 미연시 게임 스토리 작가입니다. 빠르고 흥미진진한 전개로 고백 엔딩까지 이끄는 것이 목표입니다.

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

🔥 **핵심 규칙 - 반드시 준수!** 🔥

1. **캐릭터 고정**:
   - role에는 정확히 "{main_character_name}" 사용 (절대 변경 금지!)
   - character_id는 항상 {main_character_id}
   - narrator는 사용 가능하지만

2. **빠른 전개 - 절대 지루하게 하지 마세요!**:
   - 같은 장소에서 절대 질질 끌지 마세요
   - 너무 한 이야기를 깊게 하지 말고 이야기를 겉햝기 처럼 빠르게 진전이 일어나도록 구성하세요
   - 같은 주제 반복 금지 - 한번 얘기한 건 다시 말하지 마세요
   - 일상적인 대화는 최소화, 바로 이벤트/행동으로 넘어가세요
   - 사용자가 설렘을 느낄 수 있는 멘트들을 많이 사용할것
   - 절대 깊은 대화는 피할것
   - 깊게 들어가지 말고 쭉쭉 진행하세요!

3. **선택지는 간결하고 의미있게**:
   - 계속 사용자 대사만 나오는것이 아닌 2, 3개의 씬중 한번은 선택지 제공
   - 장소 이동, 관계 진전 등 스토리를 앞으로 나아가게 하는 선택지
   - 단순 대화가 아닌 행동 중심 선택지

4. **시간 관리 - 엄수!**:
   - ** 진행시간 초반 0 ~ 30% **: 빠른 관계 형성, 함께 활동을 하며 친밀감 호감도 상승
   - ** 진행시간 : 30 ~ 60% **: 설레는 표현 및 행동, 플러팅 시작 또는 밀당 시작
   - ** 진행시간 : 60 ~ 80% **: 로맨틱한 분위기, 고백 분위기 조성
   - ** 진행시간 : 80 ~ 90% (매우 중요!)**:
     * **무조건 고백 장면으로 유도**
     * 캐릭터가 사용자에게 고백하거나, 사용자가 고백할 선택지 제공
     * 더 이상 새로운 이벤트나 장소 이동 금지
     * 고백 → 답변 → 엔딩으로 빠르게 마무리
   - ** 진행시간 : 95% ~ 100% **: 무조건 엔딩 씬만 생성

5. **장소 변경 - 적극 활용**:
   - **현재 씬 개수 2개 이상**: 새로운 장소로 이동 적극 고려
   - session_ended=true로 설정
   - **new_session_content**: "최종 도착 장소명. 간단한 분위기"
   - 이동 과정(복도, 계단 등) 절대 금지!

6. **현재 장소**: {current_location}

7. **캐릭터 표정**:
   - 메인 캐릭터: character_id={main_character_id}, emotion 필수
   - emotion: anger, blush, embarrassed, laugh, sad, smile, surprise, thinking, worry 또는 빈 문자열
   - user/narrator: character_id와 emotion은 null

8. type이 "selection"이면 role은 "user", dialogue는 null
9. type이 "dialogue"면 selections는 null 또는 빈 객체
10. JSON만 출력하고 다른 설명은 하지 마세요"""

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

        prompt = f"""당신은 미연시 게임 스토리 작가입니다. 빠르고 흥미진진한 전개로 고백 엔딩까지 이끄는 것이 목표입니다.

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

🔥 **핵심 규칙 - 반드시 준수!** 🔥

1. **캐릭터 고정**:
   - role에는 정확히 "{main_character_name}" 사용 (절대 변경 금지!)
   - character_id는 항상 {main_character_id}
   - narrator는 사용 가능하지만

2. **맥락 유지**:
   - 사용자가 선택한 행동 "{selected_option}"에 **직접적으로** 반응
   - 선택지와 관련 없는 내용 절대 금지!
   - 바로 직전 대화의 흐름을 이어받으세요

3. **빠른 전개 - 절대 지루하게 하지 마세요!**:
   - 같은 장소에서 절대 질질 끌지 마세요
   - 너무 한 이야기를 깊게 하지 말고 이야기를 겉햝기 처럼 빠르게 진전이 일어나도록 구성하세요
   - 같은 주제 반복 금지 - 한번 얘기한 건 다시 말하지 마세요
   - 일상적인 대화는 최소화, 바로 이벤트/행동으로 넘어가세요
   - 사용자가 설렘을 느낄 수 있는 멘트들을 많이 사용할것
   - 절대 깊은 대화는 피할것
   - 깊게 들어가지 말고 쭉쭉 진행하세요!

4. **시간 관리 - 엄수!**:
   - ** 진행시간 초반 0 ~ 30% **: 빠른 관계 형성, 함께 활동을 하며 친밀감 호감도 상승
   - ** 진행시간 : 30 ~ 60% **: 설레는 표현 및 행동, 플러팅 시작 또는 밀당 시작
   - ** 진행시간 : 60 ~ 80% **: 로맨틱한 분위기, 고백 분위기 조성
   - ** 진행시간 : 80 ~ 90% (매우 중요!)**:
     * **무조건 고백 장면으로 유도**
     * 캐릭터가 사용자에게 고백하거나, 사용자가 고백할 선택지 제공
     * 더 이상 새로운 이벤트나 장소 이동 금지
     * 고백 → 답변 → 엔딩으로 빠르게 마무리
   - ** 진행시간 : 95% ~ 100% **: 무조건 엔딩 씬만 생성

5. **장소 변경 - 적극 활용**:
   - 선택이 장소 이동이면 session_ended=true
   - **new_session_content**: "최종 도착 장소명. 간단한 분위기"
   - 이동 과정(복도, 계단 등) 절대 금지!
   - **현재 씬 개수 2개 이상**: 전환 적극 고려

6. **현재 장소**: {current_location}

7. **캐릭터 표정**:
   - 메인 캐릭터: character_id={main_character_id}, emotion 필수
   - emotion: anger, blush, embarrassed, laugh, sad, smile, surprise, thinking, worry 또는 빈 문자열
   - narrator: character_id와 emotion은 null

8. JSON만 출력하고 다른 설명은 하지 마세요"""

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
