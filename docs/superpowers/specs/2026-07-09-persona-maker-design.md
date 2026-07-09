# persona-maker 설계 문서

- 날짜: 2026-07-09
- 상태: 승인됨 (브레인스토밍 세션 결과)
- 대상: Claude Code 플러그인 + Codex 스킬

## 1. 목적과 문제 정의

디자이너·개발자·기획자가 제품 개발에 앞서 **주관적 편견을 배제하고 철저히 사용자의 시각에서
생각하고 의사결정할 수 있는 기준점**을 만들도록 돕는 플러그인/스킬.

핵심 가치:

- 페르소나 카드·저니맵을 리서치 모범사례에 따라 생성한다.
- AI 합성 페르소나의 학술적으로 확인된 함정(positivity bias, 정체성 평면화, WEIRD 편향)에
  대한 방어 장치로 **신뢰도 등급 체계**를 내장한다. 이것이 차별화 포인트다.
- 페르소나는 일회성 산출물이 아니라 **살아있는 문서**다. 인터뷰가 추가되면 등급이 승격된다.
- 생성 이후에도 "이 결정을 각 페르소나는 어떻게 받아들일까?"라는 **의사결정 상담**으로
  기준점 역할을 계속한다.

## 2. 확정된 결정 사항

| 항목 | 결정 |
|------|------|
| 입력 소스 | 아이디어(→ proto-persona) + 인터뷰 노트(→ 검증 페르소나) 둘 다, 신뢰도 등급으로 구분 |
| 산출물 범위 | 페르소나 카드 + 저니맵 + 의사결정 상담(consult) |
| 시각화 방식 | 자기완결 단일 HTML (의존성 0, Canvas 2D particle) |
| 페르소나 구성 | 기본 5명 = primary 1 + secondary 3 + anti-persona 1, 설정으로 3~10명 조절 |
| 플랫폼 전략 | 공유 코어 + Claude/Codex 양쪽 어댑터 |
| 커맨드 구조 | 단계별 서브커맨드 5개 (init/research/generate/visualize/consult) |
| 생성 모델 | Claude: haiku 기본, Codex: gpt-5-mini 기본, `config.json`으로 변경 가능 |

## 3. 아키텍처

### 3.1 리포 구조

```
persona-maker/
├── core/                          # 플랫폼 중립 공유 코어 (단일 진실 원천)
│   ├── methodology/
│   │   ├── persona-framework.md   # 카드 필수 요소, 다양성 규칙, anti-persona 정의
│   │   ├── journey-mapping.md     # 5단계 + 감정곡선 + pain point 규칙
│   │   ├── confidence-levels.md   # assumption/partial/validated 등급 기준
│   │   └── interview-analysis.md  # 인터뷰 노트 → 인사이트 추출 방법
│   ├── templates/
│   │   ├── persona-card.md
│   │   ├── journey-map.md
│   │   └── consultation.md
│   └── visualizer/
│       ├── template.html          # particle 시각화 셸 (Canvas 2D, 의존성 0)
│       └── build.py               # 마크다운 파싱 → JSON 임베드 → index.html 생성
├── claude-plugin/
│   ├── .claude-plugin/plugin.json
│   ├── skills/                    # init·research·generate·visualize·consult
│   └── agents/persona-generator.md  # model: haiku
├── codex-skill/                   # SKILL.md, 기본 gpt-5-mini
└── docs/superpowers/specs/
```

코어는 방법론·템플릿·시각화를 소유하고, 어댑터는 "어떤 모델로 어떻게 서브에이전트를
부르는가"만 담당한다. 방법론 수정은 한 곳에서 이루어져 양쪽에 동시 반영된다.

### 3.2 사용자 프로젝트 산출물 구조

```
personas/
├── config.json          # 모델·인원수·언어 설정
├── research/            # 입력: idea-brief.md 또는 interview-*.md
├── cards/               # persona-01-*.md ~ (신뢰도 등급 표기)
├── journeys/            # journey-p01.md ~ (감정 곡선 포함)
├── consultations/       # YYYY-MM-DD-<주제>.md (누적)
└── index.html           # 자기완결 particle 시각화 (재생성 가능)
```

### 3.3 워크플로우 (커맨드 5개)

1. `/persona-maker:init` — `personas/` 구조와 `config.json` 생성. 모델·인원수 설정 안내.
2. `/persona-maker:research` — 아이디어 브리프 또는 인터뷰 노트를 받아 구조화된
   인사이트 요약(니즈·행동·pain point 후보)을 생성. 입력 소스가 신뢰도 등급을 결정한다.
3. `/persona-maker:generate` — 인사이트 요약 기반으로 페르소나 카드 + 저니맵 생성.
   `--update` 모드는 전체 재생성 없이 기존 페르소나의 등급·속성만 갱신한다.
4. `/persona-maker:visualize` — `build.py`로 마크다운 → `index.html` 생성 후
   `python3 -m http.server`로 오픈.
5. `/persona-maker:consult` — 기존 카드 전체를 컨텍스트로 의사결정 질의.
   결과를 `consultations/`에 누적하고 시각화 Decision Log 씬에 반영.

각 단계는 독립 재실행이 가능하다(예: 인터뷰 추가 → research → generate --update →
visualize만 다시). 이것이 "살아있는 문서" 원칙과 토큰 비용 통제의 근간이다.

## 4. 데이터 모델

### 4.1 페르소나 카드 (`cards/persona-NN-<slug>.md`)

YAML frontmatter(기계 판독, 시각화 빌더의 유일한 파싱 소스) + 마크다운 본문(서사)의 이원 구조.

```yaml
---
id: p01
name: "김서연"                # 기억용 창작 프레이밍
role: primary                # primary | secondary | anti
archetype: "바쁜 실무 디자이너"
confidence: assumption       # assumption | partial | validated
sources: []                  # validated면 research/interview-*.md 인용 목록
demographics: { age: 32, occupation: "프로덕트 디자이너", context: "5인 스타트업" }
goals: ["빠른 의사결정 근거 확보"]
frustrations: ["감으로 결정했다가 재작업"]
behaviors: ["새 도구는 동료 추천으로만 도입"]
tech_savviness: 4            # 1-5, 파티클 축 매핑용
quote: "제 취향이 아니라 사용자가 원하는 걸 알고 싶어요"
---
```

본문 섹션: 서사(하루 일과, 제품 접점), 니즈 상세, **"이 페르소나가 반대할 결정들"**.
편견 배제 목적상 페르소나가 무엇을 싫어하는지가 좋아하는지만큼 중요하다.

### 4.2 신뢰도 등급 (3단계)

| 등급 | 조건 | 표시 |
|------|------|------|
| `assumption` | 아이디어만으로 AI 생성 (proto-persona) | ⚪ "가정 기반 — 실사용자 검증 전 중요 결정 금지" 배너 |
| `partial` | 인터뷰 1~2건이 일부 속성 뒷받침 | 🟡 검증 속성/가정 속성 구분 표기 |
| `validated` | 인터뷰 3건 이상이 핵심 속성 뒷받침 | 🟢 속성별 출처 인용 링크 |

`research`에 인터뷰가 추가되면 `generate --update`가 등급을 재평가·승격한다.

### 4.3 저니맵 (`journeys/journey-pNN.md`)

primary·secondary 페르소나에 대해서만 생성한다(anti-persona는 제품을 쓰지 않는 사용자이므로
저니맵 제외). 5단계(인지 → 고려 → 결정 → 사용 → 옹호) × 단계별 행동/생각/감정 점수(-2~+2)/
터치포인트/pain point. 감정 점수는 frontmatter 배열로 저장해 시각화가 감정 곡선으로 그린다.

### 4.4 의사결정 상담 (`consultations/YYYY-MM-DD-<주제>.md`)

질문, 페르소나별 반응(수용/중립/거부 + 이유), 합의점·충돌점 요약, 신뢰도 고지
("이 결론은 assumption 등급 페르소나 N명 기반").

## 5. 모델 위임과 비용 통제

- **분업 원칙**: 오케스트레이션(인사이트 요약, 상담 종합)은 메인 세션 모델,
  대량 텍스트 생성은 저가 모델.
- Claude: `agents/persona-generator.md`에 `model: haiku` 기본 지정.
  `generate`가 **페르소나 1명당 1개 haiku 서브에이전트를 병렬 디스패치** (5명 = 5개).
  각 호출은 인사이트 요약 + 템플릿 + 담당 슬롯 정의만 받아 컨텍스트가 작다.
- Codex: 동일 방법론 참조, `config.json`의 `model: "gpt-5-mini"` 기본값.
- 설정: `personas/config.json` → `{ "model": "haiku", "persona_count": 5, "language": "ko" }`.
  모든 스킬이 실행 시 이 파일을 먼저 읽는다.

## 6. Particle 시각화

Canvas 2D 파티클(수백 개 수준, WebGL 불필요, 외부 의존성 0). 각 씬이 하나의 질문에
답하는 narrative-driven 구조, 4개 씬 탭 전환:

1. **Constellation** — 파티클이 페르소나별 클러스터로 뭉침. 클릭 시 카드 확대.
   신뢰도 등급의 시각 언어: `assumption`은 흐릿한 점선 입자, `validated`는 선명한 입자.
2. **Needs Landscape** — 니즈·불만 키워드 파티클이 공유 페르소나 수만큼 크게 뭉침
   → 가장 많이 공유되는 pain point가 한눈에 보인다.
3. **Journey Emotions** — 감정 점수 곡선을 파티클 흐름으로 렌더링, 페르소나별 겹쳐 보기
   → 감정 최저점(개선 기회)이 드러난다.
4. **Decision Log** — 상담 기록별 수용/거부 분포. 파티클이 찬반으로 갈라진다.

## 7. 에러 처리

- config 없이 다른 커맨드 실행 → `init` 안내.
- research 산출물 없이 `generate` → 차단 + 안내.
- 서브에이전트 출력은 frontmatter 스키마 검증, 실패 시 1회 재시도.
- `build.py`는 파이썬 표준 라이브러리만 사용. 파싱 실패한 카드는 건너뛰고 경고 출력.

## 8. 테스트 전략

- 코드 로직은 `build.py`에 집중되므로 pytest로 검증:
  샘플 카드/저니맵 fixture → JSON 추출 정확성, 등급별 렌더링 데이터, 깨진 frontmatter 내성.
- 스킬 마크다운은 예시 시나리오(아이디어만 / 인터뷰 3건) 워크스루 문서로 검증.

## 9. 리서치 근거 (요약)

- 페르소나는 데이터 기반이어야 하며 행동·목표·동기 중심 (IxDF, Maze, NN/g).
- 저니맵 필수 요소: 단계·터치포인트·감정 곡선·pain point (IxDF, UXPressia).
- LLM 합성 페르소나의 함정: positivity bias, 정체성 평면화, WEIRD 편향
  (NN/g Synthetic Users, ACM Interactions, arXiv 2504.04927). → 신뢰도 등급으로 방어.
- 파티클 시각화는 질문 중심 narrative-driven 설계가 핵심. 수백 파티클은 Canvas 2D로 충분.
