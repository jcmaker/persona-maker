# persona-maker

디자이너·개발자·기획자가 제품 개발에 앞서 **주관적 편견을 배제하고 철저히
사용자의 시각에서 의사결정할 수 있는 기준점**을 만들어주는 Claude Code 플러그인
(+ Codex 스킬)입니다.

아이디어 한 문단 또는 인터뷰 노트를 입력하면 — 리서치 모범사례에 따른 페르소나
카드·저니맵을 생성하고, particle 시각화로 보여주고, 이후 모든 의사결정을
"페르소나들에게 물어볼" 수 있게 합니다.

**차별점 — 신뢰도 등급 체계.** LLM이 합성한 페르소나는 실제보다 긍정적이고
균질한 인물로 왜곡되는 문제(positivity bias, 정체성 평면화)가 학술적으로
확인되어 있습니다. persona-maker는 모든 페르소나에 근거 수준을 명시합니다:

| 등급 | 조건 | 의미 |
|------|------|------|
| ⚪ `assumption` | 아이디어만으로 AI 생성 | 가정 기반 proto-persona — 실사용자 검증 전 중요 결정 금지 배너 표시 |
| 🟡 `partial` | 인터뷰 1~2건이 일부 속성 뒷받침 | 검증된 속성 / 가정 속성 구분 표기 |
| 🟢 `validated` | 인터뷰 3건 이상이 핵심 속성 뒷받침 | 속성별 출처(`[I-NN]`) 인용 |

인터뷰를 추가할수록 등급이 승격되고, 가정과 모순되면 강등됩니다 — 페르소나는
일회성 산출물이 아니라 **살아있는 문서**입니다.

## 설치

### Claude Code

```bash
# 마켓플레이스/로컬 경로로 플러그인 등록 (claude-plugin/ 디렉토리)
claude plugin install <이 리포 경로>/claude-plugin
```

플러그인은 리포의 `core/`(방법론·템플릿·시각화 빌더)를 참조하므로 리포 전체를
클론한 상태로 사용하세요.

### Codex

`codex-skill/SKILL.md`를 Codex 스킬 디렉토리에 등록하세요. 기본 생성 모델만
다르고(gpt-5-mini) 워크플로우는 동일합니다.

## 워크플로우 (5개 커맨드)

```
/persona-maker:init        프로젝트 초기화 — personas/ 구조 + config.json
/persona-maker:research    아이디어 또는 인터뷰 노트 → 증거 태그가 붙은 인사이트 정리
/persona-maker:generate    페르소나 5명(primary 1 + secondary 3 + anti 1) + 저니맵 생성
/persona-maker:visualize   particle 시각화 index.html 빌드 + 로컬 서버 오픈
/persona-maker:consult     "이 결정, 페르소나들은 어떻게 볼까?" — 반응·합의점·충돌점 기록
```

전형적인 사용 흐름:

1. `init` → `research`에 아이디어 한 문단 입력 → `generate` → `visualize`
   (전원 ⚪ assumption — 화면의 흐릿한 점선 파티클이 "아직 가정"임을 상기시킴)
2. 실사용자 인터뷰 진행 후 `research`에 노트 붙여넣기 (참가자는 별칭으로)
3. `generate --update` — 전체 재생성 없이 등급·속성만 갱신 (⚪ → 🟡 → 🟢)
4. 기능 결정마다 `consult` — 결과는 Decision Log 씬에 누적

### 시각화 4개 씬

- **Constellation** — 페르소나별 파티클 군집. 신뢰도가 시각 언어로 표현됨
  (assumption = 흐릿한 점선, validated = 선명한 실선). 클릭 시 카드 상세.
- **Needs Landscape** — 니즈·불만 키워드가 공유 페르소나 수만큼 크게 뭉침.
  가장 많이 공유되는 pain point가 한눈에 보임.
- **Journey Emotions** — 5단계 감정 곡선. 최저점에 "개선 기회" 마커 자동 표시.
- **Decision Log** — 상담 기록별 수용/중립/거부 분포. assumption 근거 포함 시 경고.

스크린샷: `docs/assets/screenshot-constellation.png` (추가 예정)

## 설정 (`personas/config.json`)

| 키 | 기본값 (Claude / Codex) | 설명 |
|----|------------------------|------|
| `model` | `haiku` / `gpt-5-mini` | 페르소나 생성·상담 판정에 쓸 저비용 모델. 언제든 변경 가능 |
| `persona_count` | `5` | 총 인원 (3~10). 기본 5 = primary 1 + secondary 3 + anti 1 |
| `language` | `ko` | 산출물 언어 |

비용 설계: 슬롯 설계·검증·등급 판정 같은 판단 작업은 메인 세션이, 대량 텍스트
생성만 저비용 모델이 담당합니다. 페르소나 1명당 서브에이전트 1개가 병렬로
실행됩니다.

## 리포 구조

```
core/                # 플랫폼 중립 공유 코어 (단일 진실 원천)
├── methodology/     # 페르소나·저니맵·신뢰도·인터뷰 분석 방법론
├── templates/       # 산출물 마크다운 템플릿
└── visualizer/      # build.py (파이썬 표준 라이브러리만) + template.html (의존성 0)
claude-plugin/       # Claude Code 어댑터 (스킬 5종 + haiku 에이전트)
codex-skill/         # Codex 어댑터 (단일 SKILL.md, gpt-5-mini 기본)
tests/               # build.py pytest 스위트 + fixture
```

## 개발

```bash
python -m pytest tests/ -v          # 빌더 테스트 (9개)
python3 core/visualizer/build.py --personas-dir tests/fixtures/personas --output /tmp/preview.html
```

설계 문서: `docs/superpowers/specs/2026-07-09-persona-maker-design.md` ·
구현 플랜: `docs/superpowers/plans/2026-07-09-persona-maker.md` · PRD: `PRD.md`
