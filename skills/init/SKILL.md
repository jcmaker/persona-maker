---
name: init
description: persona-maker 프로젝트 초기화 — personas/ 구조와 config.json 생성. 사용자가 페르소나 리서치를 시작하려 할 때 가장 먼저 실행
---

# init

persona-maker 워크플로우(research → generate → visualize → consult)를 시작하기 위한
디렉토리 구조와 설정 파일을 현재 프로젝트에 준비한다.

## 지시사항

1. 현재 작업 디렉토리 기준으로 아래 디렉토리를 생성하라(이미 존재하면 그대로 둔다):
   - `personas/research`
   - `personas/cards`
   - `personas/journeys`
   - `personas/consultations`

2. `personas/config.json` 파일이 이미 존재하는지 확인하라.
   - **존재하지 않으면** 다음 내용으로 새로 생성하라:
     ```json
     {
       "model": "haiku",
       "persona_count": 5,
       "language": "ko"
     }
     ```
   - **이미 존재하면 절대 덮어쓰지 마라.** 대신 파일을 읽어 현재 설정값을 사용자에게
     그대로 보여줘라.

3. 생성했든 기존 값을 보여줬든, 각 설정 키의 의미를 사용자에게 설명하라:
   - `model`: 페르소나 생성 시 사용할 서브에이전트 모델. 기본값은 `haiku`(저비용
     대량 생성용)이며 `sonnet` 등으로 변경할 수 있다.
   - `persona_count`: 생성할 페르소나 총 인원 수(3~10, 기본 5). 기본 5명은
     primary 1 + secondary 3 + anti-persona 1 구성이다.
   - `language`: 산출물(페르소나 카드, 저니맵, 상담 기록 등)의 작성 언어.

4. 사용자가 설정 변경을 요청하면, `personas/config.json`을 직접 편집하는 방법을
   안내하라(원하는 키의 값을 수정하면 다음 실행부터 반영된다).

5. 마지막으로 다음 단계를 안내하라: "`/persona-maker:research`로 아이디어 또는
   인터뷰 노트를 입력하세요."
