---
name: generate
description: personas/research/insights.md를 바탕으로 페르소나 카드와 저니맵을 일괄 생성한다. --update 플래그로 기존 페르소나를 새 인터뷰에 맞춰 갱신할 때도 사용
---

# generate

`personas/research/insights.md`를 바탕으로 페르소나 카드(+저니맵)를 생성한다.
대량 텍스트 생성(카드·저니맵 본문 작성)은 `persona-generator` 서브에이전트에
위임하고, 슬롯 설계·검증·등급 재평가 같은 판단 작업은 메인 세션이 직접 수행한다.

## 지시사항

### 0. 전제 확인

`personas/config.json`이 없으면 다음을 안내하고 즉시 중단하라:

> 먼저 `/persona-maker:init`을 실행하세요.

`personas/research/insights.md`가 없으면 다음을 안내하고 즉시 중단하라:

> 먼저 `/persona-maker:research`를 실행하세요.

### 1. config 읽기

`personas/config.json`을 읽어 아래 값을 확인한다.

- `model` (기본값 `haiku`) — 이후 서브에이전트를 디스패치할 때 이 값을 그대로
  `model` 파라미터로 사용한다.
- `persona_count` (기본값 5)
- `language`

### 2. 슬롯 설계 (메인 세션이 직접 수행)

이 단계는 판단 작업이므로 서브에이전트에 위임하지 않는다.

1. `persona_count`에 맞춰 구성을 정한다: `primary` 1명, `anti` 1명, 나머지는
   전부 `secondary`.
2. `${CLAUDE_PLUGIN_ROOT}/core/methodology/persona-framework.md` §2
   다양성 규칙을 읽고, secondary 슬롯끼리 서로 구별되도록 슬롯별 차별화 축을
   미리 배정한다 — `tech_savviness`(최소 2점 차), 사용 동기, 이용 맥락
   (`demographics.context`) 중 최소 2개 축이 슬롯마다 달라야 한다.
3. `personas/research/insights.md` 상단의 `available_confidence`(및 표본 부족
   경고 유무)와 `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md`
   규칙에 따라 각 슬롯의 `confidence` 등급을 결정한다. 인터뷰가 0건이면 전원
   `assumption`이다. 참가자가 3명 미만이면 어떤 슬롯도 `partial`을 넘지
   않는다.
4. 슬롯마다 `id`(예: `p01`, `p02`, …), `role`, 차별화 축, `confidence`를
   정리해 다음 단계에서 서브에이전트에 그대로 전달할 수 있도록 준비한다.

### 3. 병렬 디스패치

슬롯마다 `persona-generator` 서브에이전트 1개를 **병렬로** 디스패치한다(모델은
1단계에서 읽은 `config.json`의 `model` 값을 사용). 각 프롬프트에 아래 6종을
명시한다.

1. `personas/research/insights.md` 경로
2. 해당 슬롯 정의(`id`, `role`, 차별화 축, `confidence`)
3. 템플릿 경로 — `${CLAUDE_PLUGIN_ROOT}/core/templates/persona-card.md`,
   (anti가 아니면) `${CLAUDE_PLUGIN_ROOT}/core/templates/journey-map.md`
4. 방법론 문서 경로 — `${CLAUDE_PLUGIN_ROOT}/core/methodology/persona-framework.md`,
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/journey-mapping.md`,
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md`
5. config(`language` 등)
6. 출력 파일 경로 — `personas/cards/persona-NN-<slug>.md`, (anti가 아니면)
   `personas/journeys/journey-pNN.md` (`NN`은 슬롯 `id`의 번호, `<slug>`는
   페르소나 이름의 로마자 슬러그)

### 4. 검증

서브에이전트가 완료하면 각 산출물을 확인한다.

- 카드 frontmatter에 필수 필드(`id`/`name`/`role`/`archetype`/`confidence`/
  `sources`/`demographics`/`goals`/`frustrations`/`behaviors`/
  `tech_savviness`/`quote`)가 전부 있는가
- 저니맵 frontmatter에 `persona_id`/`stages`(정확히 5개)/`emotions`(정수
  5개)/`touchpoints`/`pain_points`가 있는가
- 두 파일 모두 YAML 부분집합(스칼라, `"따옴표 문자열"`, 정수, 인라인 리스트/
  딕셔너리)만 쓰고 블록 스타일이 섞이지 않았는가
- 저니맵 `emotions`가 전부 양수는 아닌가(최소 1개는 0 이하)
- `role: anti` 슬롯에 저니맵 파일이 생성되지 않았는가

실패한 슬롯이 있으면 무엇이 문제인지 구체적으로 명시해 **해당 슬롯만 1회**
재디스패치한다. 재실패하면 그 슬롯은 자동 수정하지 말고 사용자에게 보고한다.

### 5. `--update` 모드

사용자가 `/persona-maker:generate --update`를 호출했거나, `--update` 지정 없이
호출했더라도 `personas/cards/`에 이미 카드가 있으면 전체 재생성을 하지 않는다.
대신 아래를 메인 세션이 **직접** 수행한다(등급 판정은 판단 작업이므로
서브에이전트에 위임하지 않는다).

1. 기존 카드 전체와 `personas/research/insights.md`의 신규 인사이트를
   대조한다.
2. `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md` §2(승격
   규칙)·§3(강등 규칙)을 적용한다.
   - 신규 `[증거]` 항목이 어떤 페르소나 속성과 실제로 대응하는지 확인하고,
     대응이 확인된 것만 `sources`에 추가한다(억지 연결 금지).
   - 연결된 인터뷰 수에 따라 등급을 재평가한다(0건 `assumption`, 1~2건
     `partial`, 3건+ `validated`). 참가자 3명 미만 상한을 넘기지 않는다.
   - 새 인터뷰가 기존 가정과 모순되면 해당 속성을 수정하고 본문에 "이전
     가정: …" 형태로 무엇이 왜 바뀌었는지 남긴 뒤 등급을 강등한다.
3. **변경이 필요한 카드만** 수정하고, 나머지 카드·저니맵은 건드리지 않는다.

### 6. 완료 보고

작업을 마치면 다음을 요약해 보여준다.

- 생성/갱신된 파일 목록
- 등급 분포 (`assumption N` / `partial N` / `validated N`)
- 이번 실행에서 발생한 승격·강등 내역(어떤 슬롯이 왜 바뀌었는지)

마지막으로 다음 단계를 안내한다:

> `/persona-maker:visualize`로 시각화를 생성하세요.
