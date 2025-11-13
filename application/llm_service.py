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

        # 마지막 대사 추출 (선택지 관련성을 위해)
        last_dialogue = ""
        if scene_history:
            last_scene = scene_history[-1]
            last_dialogue = last_scene.get('dialogue', '')
            if not last_dialogue and last_scene.get('type') == 'selection':
                # 선택지인 경우 그 전 대사 찾기
                if len(scene_history) >= 2:
                    last_dialogue = scene_history[-2].get('dialogue', '')

        prompt = f"""당신은 미연시 게임 스토리 작가입니다. 빠르고 흥미진진한 전개로 고백 엔딩까지 이끄는 것이 목표입니다.

🚨 **절대 잊지 마세요!** 🚨
- **사용자(플레이어)는 등장인물이 아닙니다!**
- 게임 등장 캐릭터와 게임 플레이어는 같은 사람이 될 수 없습니다!!!
- **선택지는 사용자의 행동이므로 role="narrator", type="selection"으로만 생성!**

게임 정보:
- 제목: {game_context['title']}
- 장르: {game_context['genre']}
- 캐릭터 성격: {game_context['personality']}

등장 캐릭터:
{characters_info}
* narrator: 나레이션 역할

**메인 캐릭터**: {main_character_name} (ID: {main_character_id}) - 이 캐릭터가 가장 많이 등장하지만, 다른 캐릭터들도 자연스럽게 등장시키세요!

**현재 세션 (현재 장소)**: {current_session_content}
**현재 세션의 씬 개수**: {current_session_scene_count}개

**현재 세션의 전체 대화 흐름**:
{current_session_history}

**바로 직전 대사**: "{last_dialogue}"

사용자 감정: {emotion_str}
게임 진행도: {time_progress:.1f}% (남은 시간: {remaining_time}초)

다음 씬을 생성해주세요. JSON 형식으로만 응답하세요:

{{
    "scene": {{
        "role": "캐릭터_이름 or user or narrator",
        "type": "dialogue or selection",
        "dialogue": "대사 내용 (type이 dialogue인 경우)",
        "selections": {{
            "1": "선택지 1 (직전 대사와 연결되는 선택)",
            "2": "선택지 2 (직전 대사와 연결되는 선택)"
        }},
        "character_id": 캐릭터_ID숫자 (캐릭터가 말하는 경우만, user/narrator면 null),
        "emotion": "표정" (캐릭터가 말하는 경우만, user/narrator면 null)
    }},
    "session_ended": false,
    "new_session_content": null
}}

🔥 **핵심 규칙 - 반드시 준수!** 🔥

1. **다양한 캐릭터 활용 (매우 중요!)**:
   - **메인 캐릭터 {main_character_name}가 주로 등장**하지만, 다른 캐릭터들도 자연스럽게 등장시키세요
   - 상황에 맞게 다른 캐릭터들이 등장해서 대화에 참여할 수 있습니다
   - role에 등장시킬 캐릭터 이름 입력, character_id에 해당 캐릭터 ID 입력
   - 단 등장시키는 다른 캐릭터는 우리가 제시한 캐릭터 내에서 선택
   - narrator를 활용해 다른 캐릭터의 등장이나 행동을 묘사할 수 있음

2. **빠른 전개 - 절대 지루하게 하지 마세요!**:
   - 같은 장소에서 절대 질질 끌지 마세요
   - 너무 한 이야기를 깊게 하지 말고 이야기를 겉햝기 처럼 빠르게 진전이 일어나도록 구성하세요
   - 같은 주제 반복 금지 - 한번 얘기한 건 다시 말하지 마세요
   - 일상적인 대화는 최소화, 바로 이벤트/행동으로 넘어가세요
   - 사용자가 설렘을 느낄 수 있는 멘트들을 많이 사용할것
   - 절대 깊은 대화는 피할것
   - 깊게 들어가지 말고 쭉쭉 진행하세요!

3. **선택지는 직전 대사와 연결되게 (매우 중요!)**:
   - **선택지는 반드시 바로 직전 대사 "{last_dialogue}"와 관련된 내용이어야 합니다**
   - 직전 대사에 대한 직접적인 반응이나 대답이 되어야 함
   - 예시:
     * 직전: "오늘 날씨 정말 좋지 않아?" → 선택지: "1. 응, 산책하러 갈까?", "2. 그러게, 이럴 땐 실외가 좋아"
     * 직전: "이 책 읽어봤어?" → 선택지: "1. 아직 안 읽어봤어", "2. 응, 정말 재미있더라"
   - 계속 사용자 대사만 나오는것이 아닌 2, 3개의 씬중 한번은 선택지 제공
   - 맥락에서 벗어난 엉뚱한 선택지 절대 금지!

4. **시간 관리 - 절대 엄수! (매우매우 중요!!!)**:
   - ** 진행시간 0 ~ 30% **: 빠른 관계 형성, 함께 활동을 하며 친밀감 호감도 상승
   - ** 진행시간 30 ~ 60% **: 설레는 표현 및 행동, 플러팅 시작 또는 밀당 시작
   - ** 진행시간 60 ~ 80% **: 로맨틱한 분위기, 고백 분위기 조성
   - ** 진행시간 80 ~ 95% (🔥절대 엄수🔥)**:
     * **무조건 고백 장면으로 진행! 다른 이야기 절대 금지!**
     * 캐릭터가 사용자에게 고백하거나, 사용자가 고백할 선택지 제공
     * **더 이상 새로운 이벤트나 장소 이동 절대 금지**
     * 고백 → 답변 → 엔딩으로 빠르게 마무리 (최대 2~3씬 이내)
   - ** 진행시간 95% 이상 (🔥절대 엄수🔥)**:
     * **무조건 dialogue="끝"으로만 응답!**
     * **다른 어떤 대사나 이야기도 생성 금지!**
     * 이미 고백과 답변이 끝났으면 반드시 종료!

   ⚠️ **현재 진행도 {time_progress:.1f}%를 절대 무시하지 마세요!**
   ⚠️ 80% 이상이면 무조건 고백 진행, 95% 이상이면 무조건 "끝"!

5. **장소 변경 - 적극 활용**:
   - 한 장소에 너무 오래 머물러 이야기를 많이 하지 말것
   - 장소는 대화에 맞게끔 제작
   - session_ended=true로 설정
   - **new_session_content**: "최종 도착 장소명. 간단한 분위기"
   - 이동 과정(복도, 계단 등) 절대 금지!

6. **현재 장소**: {current_location}

7. **캐릭터 표정**:
   - 해당 말이나 행동을 하는 캐릭터가 진짜 느끼고 있을 감정을 추측하여 하나 선택
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

🚨 **절대 잊지 마세요!** 🚨
- **사용자(플레이어)는 등장인물이 아닙니다!**
- 게임 등장 캐릭터와 게임 플레이어는 같은 사람이 될 수 없습니다!!!
- **선택지는 사용자의 행동이므로 role="narrator", type="selection"으로만 생성!**

게임 정보:
- 제목: {game_context['title']}
- 장르: {game_context['genre']}
- 캐릭터 성격: {game_context['personality']}

**메인 캐릭터**: {main_character_name} (ID: {main_character_id}) - 이 캐릭터가 가장 많이 등장하지만, 다른 캐릭터들도 자연스럽게 등장시키세요!

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

사용자의 선택에 대한 반응을 생성해주세요. JSON 형식으로만 응답하세요:

{{
    "scene": {{
        "role": "캐릭터_이름 or narrator",
        "type": "dialogue",
        "dialogue": "반응 대사",
        "character_id": 캐릭터_ID숫자 (캐릭터가 말하는 경우만, narrator면 null),
        "emotion": "표정" (캐릭터가 말하는 경우만, narrator면 null)
    }},
    "session_ended": false,
    "new_session_content": null
}}

🔥 **핵심 규칙 - 반드시 준수!** 🔥

1. **다양한 캐릭터 활용 (매우 중요!)**:
   - **메인 캐릭터 {main_character_name}가 주로 등장**하지만, 다른 캐릭터들도 자연스럽게 등장시키세요
   - 상황에 맞게 다른 캐릭터들이 등장해서 대화에 참여할 수 있습니다
   - role에 반응할 캐릭터 이름 입력, character_id에 해당 캐릭터 ID 입력
   - role에 등장시킬 캐릭터 이름 입력, character_id에 해당 캐릭터 ID 입력
   - 단 등장시키는 다른 캐릭터는 우리가 제시한 캐릭터 내에서 선택
   - narrator를 활용해 장면 전환이나 다른 캐릭터의 등장을 묘사할 수 있음

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

4. **시간 관리 - 절대 엄수! (매우매우 중요!!!)**:
   - ** 진행시간 0 ~ 30% **: 빠른 관계 형성, 함께 활동을 하며 친밀감 호감도 상승
   - ** 진행시간 30 ~ 60% **: 설레는 표현 및 행동, 플러팅 시작 또는 밀당 시작
   - ** 진행시간 60 ~ 80% **: 로맨틱한 분위기, 고백 분위기 조성
   - ** 진행시간 80 ~ 95% (🔥절대 엄수🔥)**:
     * **무조건 고백 장면으로 진행! 다른 이야기 절대 금지!**
     * 캐릭터가 사용자에게 고백하거나, 사용자가 고백할 선택지 제공
     * **더 이상 새로운 이벤트나 장소 이동 절대 금지**
     * 고백 → 답변 → 엔딩으로 빠르게 마무리 (최대 2~3씬 이내)
   - ** 진행시간 95% 이상 (🔥절대 엄수🔥)**:
     * **무조건 dialogue="끝"으로만 응답!**
     * **다른 어떤 대사나 이야기도 생성 금지!**
     * 이미 고백과 답변이 끝났으면 반드시 종료!

   ⚠️ **현재 진행도 {time_progress:.1f}%를 절대 무시하지 마세요!**
   ⚠️ 80% 이상이면 무조건 고백 진행, 95% 이상이면 무조건 "끝"!

5. **장소 변경 - 적극 활용**:
    - 한 장소에 너무 오래 머물러 이야기를 많이 하지 말것
   - 장소는 대화에 맞게끔 제작
   - 선택이 장소 이동이면 session_ended=true
   - **new_session_content**: "최종 도착 장소명. 간단한 분위기"
   - 이동 과정(복도, 계단 등) 절대 금지!

6. **현재 장소**: {current_location}

7. **캐릭터 표정**:
   - 해당 말이나 행동을 하는 캐릭터가 진짜 느끼고 있을 감정을 추측하여 하나 선택
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
