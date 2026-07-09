---
name: persona-maker
description: 페르소나 리서치·생성·시각화·의사결정 상담이 필요할 때 — 아이디어/인터뷰를 인사이트로 정리하거나, 페르소나 카드·저니맵을 만들거나, 시각화를 보여주거나, 기능 결정에 대한 페르소나 반응을 물어볼 때 사용
---

# persona-maker (Codex 어댑터)

Claude 플러그인(`claude-plugin/`)의 init/research/generate/visualize/consult
5개 스킬을 단일 파일로 통합한 Codex용 어댑터다. Codex에는 서브커맨드 구조가
없으므로, 사용자 요청을 아래 "모드 판별" 표로 분류한 뒤 해당 모드 섹션의
지시를 따른다.

**단일 진실 원천(SSOT):** 리서치·페르소나·저니맵·신뢰도 등급의 방법론은
`../core/methodology/*.md`, 산출물 포맷은 `../core/templates/*.md`에 있다.
이 파일은 절차 요약과 원문 참조만 제공한다 — 방법론이 바뀌어도 이 파일은
바뀌지 않는 것이 목표다. 아래 경로는 전부 **이 SKILL.md 파일이 위치한
`codex-skill/` 디렉토리 기준 상대 경로**다(`codex-skill/`과 `core/`는 리포
루트의 형제 디렉토리이므로 `${CLAUDE_PLUGIN_ROOT}` 같은 변수는 쓰지 않는다).

**경로 해석 규칙 (중요):** 작업 시작 시 이 SKILL.md가 설치된 디렉토리의
절대 경로를 확인해 `<SKILL_DIR>`로 삼아라. 본문의 `../core/...` 경로는 전부
`<SKILL_DIR>/../core/...`로 해석해 **절대 경로로** 읽고 실행한다. 사용자
프로젝트의 CWD 기준 상대 경로로 실행하면 안 된다 — `personas/` 산출물 경로만
사용자 프로젝트 CWD 기준이다.

## 모드 판별

사용자 요청을 아래 표에 대조해 모드를 정하라. 두 모드에 걸치거나 애매하면
**추측하지 말고 사용자에게 어떤 모드로 진행할지 물어라.**

| 사용자 요청 예시 | 모드 |
|---|---|
| "시작", "설정", "초기화", 프로젝트를 처음 준비할 때 | `init` |
| 제품 아이디어 설명, 인터뷰 원문/메모 붙여넣기 | `research` |
| "페르소나 만들어줘", "카드 생성", "갱신해줘", `--update` 요청 | `generate` |
| "보여줘", "시각화해줘", "visualize", 브라우저로 확인하고 싶을 때 | `visualize` |
| "이 결정 어떻게 생각할까", "페르소나들한테 물어봐줘", 기능/디자인 반응 확인 | `consult` |

모드가 정해지면 아래 해당 섹션만 따른다. 각 섹션은 Claude 플러그인의 동명
스킬(`claude-plugin/skills/<mode>/SKILL.md`)과 **동일한 게이트·절차·규칙**을
따르되, Codex 환경 차이(기본 모델, 경로, 서브에이전트 디스패치)만 다르다.

---

## init 모드

목표: `personas/` 작업 구조와 `personas/config.json`을 준비한다.

1. 현재 작업 디렉토리 기준으로 다음 디렉토리를 생성한다(이미 있으면 그대로
   둔다): `personas/research`, `personas/cards`, `personas/journeys`,
   `personas/consultations`.
2. `personas/config.json`이 이미 존재하는지 확인한다.
   - **없으면** 다음 내용으로 새로 생성한다(Codex 어댑터 기본값 —
     Claude 어댑터의 `haiku` 대신 `gpt-5-mini`를 기본으로 쓴다):
     ```json
     {
       "model": "gpt-5-mini",
       "persona_count": 5,
       "language": "ko"
     }
     ```
   - **이미 존재하면 절대 덮어쓰지 마라.** 대신 읽어서 현재 값을 그대로
     보여준다.
3. 각 설정 키를 설명한다:
   - `model`: 페르소나 생성/협의 판정을 위임할 때 사용할 모델. 기본값은
     `gpt-5-mini`(저비용 대량 생성용)이며 `gpt-5` 등 다른 OpenAI 모델명으로
     바꿀 수 있다.
   - `persona_count`: 생성할 페르소나 총 인원 수(3~10, 기본 5). 기본 5명은
     primary 1 + secondary 3 + anti-persona 1 구성이다.
   - `language`: 산출물(카드, 저니맵, 협의 기록 등) 작성 언어.
4. 설정 변경 요청이 오면 `personas/config.json`을 직접 편집하도록 안내한다
   (다음 실행부터 반영).
5. 다음 단계 안내: "아이디어 또는 인터뷰 노트를 입력하면 research 모드로
   정리합니다."

---

## research 모드

목표: 아이디어/인터뷰 입력을 `personas/research/`에 저장하고
`personas/research/insights.md`를 생성·갱신한다. 절차 원문은
`../core/methodology/interview-analysis.md`.

### 0. 전제 확인

`personas/config.json`이 없으면 "먼저 init 모드를 실행하세요."라고 안내하고
즉시 중단한다.

### 1. 입력 판별 및 저장

- **(a) 제품 아이디어 서술** → `personas/research/idea-brief.md`. 기존
  파일이 있으면 덮어쓰기 전에 갱신 여부를 확인한다.
- **(b) 인터뷰 노트** → `personas/research/interview-NN-<참가자별칭>.md`
  (`NN`은 기존 `interview-*.md` 다음 2자리 순번, 없으면 `01`). 참가자
  실명은 저장하지 않는다(별칭 미제공 시 사용자에게 확인). 원문은 가공 없이
  그대로 저장한다 — 요약·정제는 2단계에서만 한다.

애매하면 추측하지 말고 사용자에게 물어라.

### 2. 인사이트 추출

`../core/methodology/interview-analysis.md`를 읽고 그 절차를 그대로 따라
`personas/research/insights.md`를 생성/갱신한다. 핵심 규칙:

- 증거 문장은 원문에서 그대로(또는 최소 편집) 추출하고 `[I-NN]` 태그를
  붙인다. 원문에 없는 내용을 지어내지 않는다.
- **[증거]**(명시적 발화)와 **[추론]**(종합 판단)을 라벨로 반드시 구분하고
  섞지 않는다. 추론에는 근거 `[I-NN]` 목록을 병기한다.
- 인터뷰 0건이면 전 항목이 "[추론] (아이디어 기반 가정)"이며, 상단에
  `available_confidence: assumption`을 명시한다.
- 참가자(별칭 기준) 3명 미만이면 상단에 다음 문구를 정확히 명시한다:
  > 표본 부족 — validated 등급 불가 (partial까지만 허용).

  인터뷰 건수·참가자 수를 함께 기록한다(같은 참가자를 여러 번 인터뷰했을 수
  있으므로 둘 다 남긴다).

`insights.md` 권장 구조는 `interview-analysis.md`와 Claude 어댑터의
research 스킬 예시를 따른다(니즈/불만/행동 섹션, 각 항목에 `[증거]`/`[추론]`
라벨 + `[I-NN]` 태그).

### 3. 직접 수행 원칙

이 모드(입력 판별, 저장, 인사이트 추출)는 메인 세션이 **직접** 수행한다.
서브에이전트/스폰에 위임하지 않는다 — 증거/추론 구분과 표본 부족 판정은
오케스트레이션·판단 작업이며, 대량 생성을 위임하는 generate 모드와 분업이
다르다.

### 4. 완료 보고

저장된 파일 경로, 추출된 인사이트 건수(니즈/불만/행동별 증거·추론), 현재
참가자·인터뷰 수와 그에 따라 가능한 최대 신뢰도 등급을 요약한다. 마지막으로
다음 단계를 안내한다: 카드가 없으면 "generate 모드로 페르소나를
생성하세요", 있으면 "generate 모드(--update)로 갱신하세요."

---

## generate 모드

목표: `personas/research/insights.md`를 바탕으로 페르소나 카드(+저니맵)를
생성한다. 대량 본문 생성은 위임하고, 슬롯 설계·검증·등급 재평가는 메인
세션이 직접 수행한다.

### 0. 전제 확인

`personas/config.json`이 없으면 "먼저 init 모드를 실행하세요."라고 안내하고
중단한다. `personas/research/insights.md`가 없으면 "먼저 research 모드를
실행하세요."라고 안내하고 중단한다.

### 1. config 읽기

`personas/config.json`에서 `model`(기본값 `gpt-5-mini`), `persona_count`
(기본값 5), `language`를 읽는다.

### 2. 슬롯 설계 (메인 세션이 직접 수행)

위임하지 않는다.

1. `persona_count`에 맞춰 `primary` 1명, `anti` 1명, 나머지는 전부
   `secondary`로 구성한다.
2. `../core/methodology/persona-framework.md` §2 다양성 규칙을 읽고,
   secondary 슬롯끼리 구별되도록 슬롯별 차별화 축을 미리 배정한다 —
   `tech_savviness`(최소 2점 차), 사용 동기, 이용 맥락
   (`demographics.context`) 중 최소 2개 축이 슬롯마다 달라야 한다.
3. `insights.md` 상단 `available_confidence`(및 표본 부족 경고 유무)와
   `../core/methodology/confidence-levels.md` 규칙에 따라 슬롯별
   `confidence` 등급을 정한다. 인터뷰 0건이면 전원 `assumption`. 참가자
   3명 미만이면 어떤 슬롯도 `partial`을 넘지 않는다.
4. 슬롯마다 `id`(`p01`, `p02`, …), `role`, 차별화 축, `confidence`를
   정리해 다음 단계 위임에 그대로 전달할 수 있게 준비한다.

### 3. 위임 디스패치 (Codex 환경 차이)

슬롯마다 페르소나 카드(+저니맵) 1건씩 생성을 위임한다.

- **Codex의 서브에이전트/스폰 메커니즘이 있으면**: 슬롯마다 1개씩 위임하고,
  1단계에서 읽은 `config.json`의 `model` 값을 그 위임 호출의 모델로 지정한다.
  가능하면 병렬로 디스패치한다.
- **스폰 메커니즘이 없는 환경이면**: 같은 세션에서 슬롯을 순차 생성하되,
  **페르소나 1명 분량씩 나눠서** 만든다(한 번에 여러 슬롯을 뭉쳐 쓰지
  않는다) — 슬롯 간 혼선(차별화 축 누락, 등급 오적용)을 막기 위함이다.

각 위임(또는 각 순차 생성 단계)에 아래 6종을 명시한다(원본 지시 전문은
`claude-plugin/agents/persona-generator.md` 참조 — 카드마다 채워야 할 필수
필드, YAML 부분집합 제약, positivity bias 금지 체크리스트가 정의되어 있다):

1. `personas/research/insights.md` 경로
2. 해당 슬롯 정의(`id`, `role`, 차별화 축, `confidence`)
3. 템플릿 경로 — `../core/templates/persona-card.md`, (anti가 아니면)
   `../core/templates/journey-map.md`
4. 방법론 문서 경로 — `../core/methodology/persona-framework.md`,
   `../core/methodology/journey-mapping.md`,
   `../core/methodology/confidence-levels.md`
5. config(`language` 등)
6. 출력 파일 경로 — `personas/cards/persona-NN-<slug>.md`, (anti가 아니면)
   `personas/journeys/journey-pNN.md`

생성 시 반드시 지킬 핵심 규칙(전문은 `persona-framework.md` 및
`persona-generator.md` 참조):

- frontmatter는 YAML 부분집합(스칼라, `"따옴표 문자열"`, 정수, 한 줄 인라인
  리스트/딕셔너리)만 쓴다. 블록 스타일 중첩은 절대 쓰지 않는다.
- 카드 필수 필드: `id`/`name`/`role`/`archetype`/`confidence`/`sources`/
  `demographics`/`goals`/`frustrations`/`behaviors`/`tech_savviness`/
  `quote`. 저니맵 필수 필드: `persona_id`/`stages`(5개)/`emotions`(정수
  5개)/`touchpoints`/`pain_points`.
- positivity bias 금지: "## 이 페르소나가 반대할 결정들" 최소 3개,
  `frustrations` 중 최소 1개는 제품/팀 자체 대상, `behaviors` 중 최소 1개는
  회피/포기/우회, 저니맵 `emotions`는 전부 양수 금지(최소 1개는 0 이하).
- `sources`는 insights.md의 `[증거]` 항목만 인용한다.
- `confidence`는 배정된 등급을 그대로 쓴다(임의 변경 금지).

### 4. 검증

위임 결과를 확인한다: 카드/저니맵 필수 필드 존재, YAML 부분집합 준수,
저니맵 `emotions`에 0 이하 값 포함 여부, `role: anti` 슬롯에는 저니맵이
생성되지 않았는지. 실패한 슬롯은 무엇이 문제인지 구체적으로 명시해 **해당
슬롯만 1회** 재위임한다. 재실패하면 자동 수정하지 말고 사용자에게 보고한다.

### 5. `--update` 모드

`--update` 요청이거나, 별도 지정 없이도 `personas/cards/`에 이미 카드가
있으면 전체 재생성하지 않는다. 아래를 메인 세션이 **직접** 수행한다(위임하지
않는다 — 등급 판정은 판단 작업이다):

1. 기존 카드 전체와 `insights.md`의 신규 인사이트를 대조한다.
2. `../core/methodology/confidence-levels.md` §2(승격)·§3(강등) 규칙을
   적용한다. 신규 `[증거]`가 실제로 대응하는 속성만 `sources`에 추가하고
   (억지 연결 금지), 연결된 인터뷰 수로 등급을 재평가한다(0건 assumption,
   1~2건 partial, 3건+ validated, 단 참가자 3명 미만 상한 유지). 모순되면
   해당 속성을 수정하고 본문에 "이전 가정: …" 형태로 남긴 뒤 강등한다.
3. **변경이 필요한 카드만** 수정하고 나머지는 건드리지 않는다.

### 6. 완료 보고

생성/갱신 파일 목록, 등급 분포(assumption/partial/validated 각 N), 이번
실행의 승격·강등 내역을 요약한다. 마지막으로 "visualize 모드로 시각화를
생성하세요."라고 안내한다.

---

## visualize 모드

목표: `personas/cards/`·`personas/journeys/`·`personas/consultations/`를
조립해 `personas/index.html`을 빌드하고 로컬 서버로 연다.

### 0. 전제 확인

`personas/config.json`이 없으면 "먼저 init 모드를 실행하세요."라고 안내하고
중단한다. `personas/cards/`에 카드가 하나도 없으면 "먼저 generate 모드를
실행하세요."라고 안내하고 중단한다.

### 1. 빌드 실행

아래 명령을 실행한다. `<SKILL_DIR>`은 문서 서두의 경로 해석 규칙대로 이
SKILL.md가 위치한 디렉토리의 절대 경로다(사용자 프로젝트 CWD에서 실행해도
동작해야 하므로 절대 경로 사용). 출력·템플릿 경로는 지정하지 않는다 —
`build.py` 기본값(출력: `personas/index.html`, 템플릿: `build.py`와 같은
디렉토리의 `template.html`)을 그대로 쓴다.

```bash
python3 <SKILL_DIR>/../core/visualizer/build.py --personas-dir personas
```

- stdout에는 생성된 `index.html` 경로 한 줄이 찍힌다.
- stderr에는 경고(깨진 frontmatter, 필드 누락, 디렉토리 없음 등)가 0줄
  이상 찍힐 수 있다. 경고가 있어도 명령 자체는 실패하지 않는다 — exit
  code로 성공 여부를 판단한다. exit code가 0이 아니면 stderr 전체를
  사용자에게 보여주고 중단한다.

### 2. 경고 전달

stderr에 출력이 있었다면 각 경고를 "어떤 파일 / 무엇이 잘못됐는지 / 해당
파일 frontmatter를 수정한 뒤 다시 실행하면 반영된다"는 형식으로 요약해
보여준다. 경고가 있어도 `index.html`은 생성되므로(문제 파일만 제외하고
조립) 3단계로 계속 진행한다.

### 3. 서버 오픈

**3-1. 기존 서버 재사용 확인**: 8765부터 8775까지 순서대로
```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 1 http://localhost:<port>/index.html
```
로 이미 이 프로젝트를 서빙 중인 서버가 있는지 확인한다. `200`이 나오면 그
서버를 재사용하고(새 프로세스 기동 금지) 해당 URL을 안내한 뒤 4단계로
넘어간다.

**3-2. 새 서버 기동**: 재사용할 서버가 없으면 `8765`부터 최대 `8775`까지
(총 11개 포트) 아래를 반복한다.

1. 백그라운드로 `python3 -m http.server <port> --directory personas` 실행.
2. 성공 조건: `Serving HTTP on ... port <port> ...` 로그, 에러 없음. 실패
   조건: `OSError`/`Address already in use` — 해당 프로세스를 종료하고
   포트를 1 증가시켜 재시도.
3. 성공 시 위 curl 명령으로 `200` 최종 확인.

11개 포트 모두 실패하면 실패 사실을 알리고, 사용자가 직접
`python3 -m http.server <원하는 포트> --directory personas`를 실행하도록
안내한 뒤 중단한다.

### 4. 완료 안내

접속 URL(`http://localhost:<port>/index.html`)과 4개 씬(Constellation,
Needs Landscape, Journey Emotions, Decision Log)을 간단히 소개한다.
인터뷰 추가 시 research → generate(--update) → visualize 순서로 다시
실행해 최신화할 수 있음을 안내하고, 기능/디자인 결정에 대한 페르소나
반응이 필요하면 consult 모드를 안내한다.

---

## consult 모드

목표: 기능·디자인 결정을 `personas/cards/`의 페르소나들에게 시뮬레이션으로
"물어보고" accept/neutral/reject 반응과 근거를 협의 기록으로 남긴다.
페르소나별 반응 판정(대량 판단)은 위임하고, 질문 구체화·종합·신뢰도 고지는
메인 세션이 직접 수행한다.

### 0. 전제 확인

`personas/config.json`이 없으면 "먼저 init 모드를 실행하세요."라고 안내하고
중단한다. `personas/cards/`에 카드가 하나도 없으면 "먼저 generate 모드를
실행하세요."라고 안내하고 중단한다.

### 1. 질문 접수

사용자가 제시한 의사결정 질문을 구체화한다. 선택지가 불명확하거나 "이거
어떨까요?" 수준으로 추상적이면 추측하지 말고 되물어 선택지를 명확히 한다
(예: "온보딩에 회원가입을 강제할까요, 게스트 모드를 둘까요?"). 이미 구체적
(명확한 이분법/단일 결정 서술)이면 바로 진행한다.

### 2. 카드 로드

`personas/cards/*.md` 전체를 읽는다. 요약하거나 일부만 골라 읽지 않는다 —
협의는 카드의 goals/frustrations/behaviors/"이 페르소나가 반대할 결정들"
전체를 근거로 삼아야 한다.

### 3. 위임 디스패치 (Codex 환경 차이)

`personas/config.json`의 `model`(기본값 `gpt-5-mini`)로 판정을 위임한다.

- **Codex의 서브에이전트/스폰 메커니즘이 있으면**: 1회 위임 호출에 config의
  `model`을 지정하고, 카드 전체 + 구체화된 질문을 전달해 전원의 반응을
  한 번에 받는다.
- **스폰 메커니즘이 없는 환경이면**: 같은 세션에서 순차로 판정하되,
  **페르소나 1명 분량씩 나눠서** 판정한다(전원을 한 번에 뭉쳐서 판정하지
  않는다) — 카드 간 근거 혼선을 막기 위함이다.

위임 시 반드시 포함할 지시:

- 1단계에서 구체화한 질문(선택지 포함), 2단계에서 읽은 카드 전체(모든
  페르소나, frontmatter + 본문).
- 페르소나(`role: anti` 포함) 전원에 대해 개별적으로
  `accept`/`neutral`/`reject`를 판정하고 1~3문장 이유를 작성한다.
- **이유는 반드시 해당 카드의 `goals`/`frustrations`/`behaviors` 또는
  "## 이 페르소나가 반대할 결정들"에서 실제로 인용해야 한다.** 카드에 없는
  근거를 지어내지 않는다 — 인용할 근거가 없으면 그 사실을 그대로 보고한다.
- `role: anti` 페르소나의 반응은 개별 기능 호불호가 아니라 **제품 핵심
  전제에 대한 입장**을 반영해야 한다.
- 출력 형식: 페르소나 `id`마다 `판정: accept|neutral|reject` +
  `이유: "..."`를 명확히 구분해 반환하도록 요청한다(메인 세션이 그대로
  파싱할 수 있도록).

### 4. 종합 (메인 세션 직접 수행)

위임 결과를 받으면 이 단계는 메인 세션이 **직접** 수행한다(위임하지
않는다):

1. 페르소나 간 합의점(반응이 겹치는 지점)과 충돌점(정면으로 부딪히는 지점)을
   구분한다. 전원이 같은 반응이더라도 이유까지 같은지 확인하고, 다르면
   충돌점에 남긴다.
2. `../core/methodology/confidence-levels.md` 기준으로 신뢰도 고지를
   작성한다:
   - 근거로 인용된 페르소나 중 `assumption` 등급이 하나라도 있으면: "이
     결론은 assumption 등급 페르소나 N명 기반 — 실사용자 검증 전에는 중요한
     의사결정 근거로 사용하지 마세요." (N은 실제 인원 수로 치환, 문구
     그대로 사용)
   - 인용된 페르소나가 `partial`/`validated` 등급뿐이면: "이 결론은
     partial 이상 등급 페르소나 N명 기반입니다." 형태로 신뢰 수준을
     명시한다.

### 5. 저장

`../core/templates/consultation.md` 구조를 그대로 따라 협의 기록을
작성한다.

- 저장 경로: `personas/consultations/YYYY-MM-DD-<주제-slug>.md`.
  `YYYY-MM-DD`는 `date +%F` 명령으로 정확한 오늘 날짜를 확인해 사용한다
  (시스템 컨텍스트 날짜와 다를 수 있으므로 반드시 셸에서 직접 확인). 슬러그는
  질문을 요약한 소문자 kebab-case 로마자(예: "회원가입 강제 여부" →
  `signup-required`). 동일 날짜·주제 파일이 이미 있으면 `-2`, `-3`… 접미사를
  붙인다.
- frontmatter: `date`("YYYY-MM-DD" 따옴표 문자열), `topic`(구체화한 질문 한
  줄), `reactions: { p01: accept, p02: neutral, ... }`(협의에 참여한 모든
  페르소나 id 포함, YAML 부분집합만 사용 — 블록 스타일 중첩과 인라인 `#`
  주석은 절대 쓰지 않는다).
- 본문 섹션: "질문", "페르소나별 반응"(페르소나마다 소제목 + 카드 근거
  인용), "합의점과 충돌점", "신뢰도 고지"를 `consultation.md` 예시 형식
  그대로 채운다.

### 6. 완료 안내

반응 요약(`accept N명 / neutral N명 / reject N명`), 핵심 충돌점 1~2줄,
저장된 협의 기록 경로를 보여준다. 마지막으로 "visualize 모드를 다시
실행하면 Decision Log 씬에 이번 협의 결과가 반영됩니다."라고 안내한다.
