# persona-maker

아이디어나 인터뷰 노트를 주면, **신뢰도 등급이 붙은 페르소나 카드·저니맵·particle 시각화**를 만들어주는 Claude Code 플러그인.

디자이너·개발자·기획자가 "내 취향"이 아니라 **사용자의 시각**으로 의사결정하도록, 근거 수준을 항상 드러내는 기준점을 제공합니다. 이후의 모든 기능·디자인 결정은 `/persona-maker:consult`로 페르소나들에게 미리 "물어볼" 수 있습니다.

## 왜 신뢰도 등급인가

LLM이 합성한 페르소나는 실제보다 성공적이고 호의적인 인물로 왜곡되고(positivity bias), 서로 비슷해지는(정체성 평면화) 문제가 학술적으로 확인되어 있습니다. persona-maker는 이를 두 겹으로 방어합니다 — 생성 규칙(반대할 결정 3개+, 회피 행동 필수, 전원 긍정 감정 금지)과 **신뢰도 3등급**:

| 등급 | 조건 | 표시 |
|------|------|------|
| ⚪ `assumption` | 아이디어만으로 AI 생성 | "실사용자 검증 전 중요 결정 금지" 배너 + 흐릿한 점선 파티클 |
| 🟡 `partial` | 인터뷰 1~2건이 일부 속성 뒷받침 | 검증 속성 / 가정 속성 구분 표기 |
| 🟢 `validated` | 인터뷰 3건 이상이 핵심 속성 뒷받침 | 속성별 출처(`[I-NN]`) 인용 + 선명한 파티클 |

인터뷰를 추가하면 `generate --update`가 전체 재생성 없이 등급·속성만 승격/강등합니다 — 페르소나는 **살아있는 문서**입니다.

## 설치

Claude Code에서:

```
/plugin marketplace add jcmaker/persona-maker
/plugin install persona-maker@persona-maker
```

Codex는 `codex-skill/SKILL.md`를 스킬 디렉토리에 등록하세요 (기본 모델만 `gpt-5-mini`로 다르고 워크플로우는 동일).

## 사용법

```
/persona-maker:init          personas/ 구조 + config.json 생성
/persona-maker:research      아이디어 또는 인터뷰 노트 → 증거 태그가 붙은 인사이트
/persona-maker:generate      페르소나 5명(primary 1 + secondary 3 + anti 1) + 저니맵
/persona-maker:visualize     particle 시각화 빌드 + 로컬 서버 오픈
/persona-maker:consult       "이 결정, 페르소나들은 어떻게 볼까?"
```

전형적인 흐름:

1. `init` → `research`에 아이디어 한 문단 → `generate` → `visualize` — 전원 ⚪ (화면의 점선 파티클이 "아직 가정"임을 계속 상기시킴)
2. 실사용자 인터뷰 후 `research`에 노트 붙여넣기 (참가자는 별칭으로 — 실명 저장 안 함)
3. `generate --update` — 변경된 카드만 갱신, ⚪ → 🟡 → 🟢
4. 기능 결정마다 `consult` — 반응·합의점·충돌점이 기록되고 Decision Log 씬에 누적

### 시각화 4개 씬

| 씬 | 답하는 질문 |
|----|-------------|
| **Constellation** | 우리 사용자들은 누구이고, 근거는 얼마나 단단한가? |
| **Needs Landscape** | 가장 많은 페르소나가 공유하는 pain point는? |
| **Journey Emotions** | 감정이 가장 꺾이는 단계(= 개선 기회)는 어디인가? |
| **Decision Log** | 지금까지의 결정에 페르소나들은 어떻게 반응했나? |

시각화는 의존성 0의 **자기완결 단일 HTML**(Canvas 2D)로 생성됩니다.

## 비용 설계

슬롯 설계·검증·등급 판정 같은 판단 작업은 메인 세션이, 대량 텍스트 생성은 저비용 모델이 담당합니다 (페르소나 1명당 서브에이전트 1개 병렬). `personas/config.json`에서 언제든 변경:

| 키 | 기본값 (Claude / Codex) | 설명 |
|----|------------------------|------|
| `model` | `haiku` / `gpt-5-mini` | 생성·상담 판정용 저비용 모델 |
| `persona_count` | `5` | 총 인원 (3~10) |
| `language` | `ko` | 산출물 언어 |

## 리포 구조

```
.claude-plugin/      # plugin.json + marketplace.json
commands/            # /persona-maker:* 커맨드 5종
skills/              # init · research · generate · visualize · consult
agents/              # persona-generator (haiku, 저비용 생성 전담)
core/
├── methodology/     # 페르소나·저니맵·신뢰도·인터뷰 분석 방법론 (단일 진실 원천)
├── templates/       # 산출물 마크다운 템플릿
└── visualizer/      # build.py (Python, 표준 라이브러리만) + template.html (Canvas 2D)
scripts/             # serve.sh (로컬 서버) · smoke_template.mjs (템플릿 무결성 검사)
codex-skill/         # Codex 단일 파일 어댑터
tests/               # pytest 스위트 + fixture
```

## 개발

```bash
python -m pytest tests/ -v                      # 빌더 테스트
node scripts/smoke_template.mjs                 # 템플릿 무결성 4종 검사
python3 core/visualizer/build.py --personas-dir tests/fixtures/personas --output /tmp/preview.html
bash scripts/serve.sh tests/fixtures/personas   # (빌드 후) 로컬 서버
```

설계 문서: `docs/superpowers/specs/` · 구현 플랜: `docs/superpowers/plans/` · PRD: `PRD.md`

## 라이선스

MIT
