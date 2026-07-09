# persona-maker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 편견 없는 사용자 관점 의사결정 기준점을 만들어주는 persona-maker 플러그인(Claude Code + Codex)을 구현한다.

**Architecture:** 플랫폼 중립 공유 코어(방법론 마크다운 + 산출물 템플릿 + 단일 HTML particle 시각화 빌더) 위에 Claude 플러그인 어댑터(5개 스킬 + haiku 서브에이전트)와 Codex 스킬 어댑터를 얹는다. 코드 로직은 `core/visualizer/build.py` 하나에 집중되며 TDD로 개발한다.

**Tech Stack:** Python 3 표준 라이브러리(빌더), pytest(테스트), Canvas 2D + vanilla JS(시각화, 의존성 0), 마크다운 + YAML frontmatter(산출물).

**Spec:** `docs/superpowers/specs/2026-07-09-persona-maker-design.md`

---

## 실행 모델 (사용자 지시사항)

- **지휘·감독·검수: Fable 5 (메인 세션).** 각 태스크 완료 시 Fable이 스펙 부합·코드 품질 2단계 리뷰를 수행하고 다음 태스크를 디스패치한다.
- **작업자: Sonnet 5 서브에이전트, 역할별 구성.** Agent tool 호출 시 `model: "sonnet"` 지정.

| 역할 | 담당 태스크 | 트랙 |
|------|------------|------|
| methodology-writer | Task 1, 2 | A (병렬) |
| python-engineer | Task 3, 4, 5 | B (병렬) |
| frontend-engineer | Task 6, 7, 8 | C (병렬) |
| plugin-engineer | Task 9, 10, 11, 12 | D (A 완료 후) |
| adapter-engineer | Task 13 | E (D 완료 후) |
| Fable (직접) | Task 14 통합 검증 | 최종 |

**병렬 규칙:** 트랙 A·B·C는 서로 의존이 없으므로 동시 디스패치한다. 트랙 내부 태스크는 순차 실행(같은 파일을 다룸). Task 5는 Task 3·4 완료 후, Task 8은 Task 6·7 완료 후. 트랙 D는 트랙 A의 방법론 문서를 참조하므로 A 완료 후 시작. Task 14는 전부 완료 후 Fable이 직접 수행.

**공통 규약 (모든 서브에이전트 프롬프트에 포함):**
- 커밋 메시지는 conventional commits (`feat:`, `test:`, `docs:`).
- Python은 표준 라이브러리만. 외부 패키지 import 금지 (pytest는 dev 전용).
- 한국어 사용자 대상 산출물 예시는 한국어, 코드 식별자·주석은 영어.
- research·generate·visualize·consult 스킬은 시작 시 `personas/config.json` 존재를 확인하고, 없으면 "먼저 /persona-maker:init을 실행하세요"를 안내하고 중단한다 (스펙 §7). 이 지시를 각 SKILL.md 서두에 포함할 것.

---

## 파일 구조 (전체 맵)

```
core/
├── methodology/
│   ├── persona-framework.md      # Task 1 — 카드 필수 요소·다양성 규칙·anti-persona
│   ├── journey-mapping.md        # Task 1 — 5단계·감정곡선 규칙
│   ├── confidence-levels.md      # Task 1 — 신뢰도 3등급 기준·승격 규칙
│   └── interview-analysis.md     # Task 1 — 인터뷰 → 인사이트 추출 방법
├── templates/
│   ├── persona-card.md           # Task 2 — frontmatter 스키마 + 본문 골격
│   ├── journey-map.md            # Task 2
│   └── consultation.md           # Task 2
└── visualizer/
    ├── build.py                  # Task 3, 4, 5 — 파서·수집·HTML 조립
    └── template.html             # Task 6, 7, 8 — particle 시각화 셸
tests/
├── test_frontmatter.py           # Task 3
├── test_collect.py               # Task 4
├── test_build_html.py            # Task 5
└── fixtures/personas/            # Task 3~5에서 점진 구축 (config.json, cards/, journeys/, consultations/)
claude-plugin/
├── .claude-plugin/plugin.json    # Task 9
├── skills/
│   ├── init/SKILL.md             # Task 9
│   ├── research/SKILL.md         # Task 10
│   ├── generate/SKILL.md         # Task 11
│   ├── visualize/SKILL.md        # Task 12
│   └── consult/SKILL.md          # Task 12
└── agents/persona-generator.md   # Task 11
codex-skill/SKILL.md              # Task 13
README.md                         # Task 14
```

**공유 데이터 계약 (모든 트랙이 준수):** 페르소나 frontmatter 필드는 스펙 §4.1과 동일 — `id`(p01…), `name`, `role`(primary|secondary|anti), `archetype`, `confidence`(assumption|partial|validated), `sources`(list), `demographics`(inline dict), `goals`/`frustrations`/`behaviors`(list), `tech_savviness`(int 1-5), `quote`. 저니맵 frontmatter: `persona_id`, `stages`(5개 고정: awareness|consideration|decision|usage|advocacy), `emotions`(int 배열 5개, -2~+2), `touchpoints`(list), `pain_points`(list). 상담 frontmatter: `date`, `topic`, `reactions`(persona_id → accept|neutral|reject 매핑). build.py가 template.html의 `/*__PERSONA_DATA__*/` 마커에 주입하는 JSON 스키마: `{"config": {...}, "personas": [...], "journeys": [...], "consultations": [...], "warnings": [...]}`.

---

## Track A — 방법론·템플릿 (methodology-writer, sonnet)

### Task 1: 방법론 문서 4종

**Files:**
- Create: `core/methodology/persona-framework.md`
- Create: `core/methodology/journey-mapping.md`
- Create: `core/methodology/confidence-levels.md`
- Create: `core/methodology/interview-analysis.md`

- [ ] **Step 1: persona-framework.md 작성**

포함 내용 (각 항목은 생성 에이전트가 그대로 따를 수 있는 지시문으로 작성):
- 카드 필수 요소: 이름(한국어 창작명), archetype, 목표·불만·행동(각 3~5개, 구체적 상황 서술), quote(1인칭), demographics(나이·직업·컨텍스트만 — 과도한 인구통계 금지).
- 다양성 규칙: 5명 기본 구성 = primary 1 + secondary 3 + anti 1. secondary 간에는 숙련도(tech_savviness)·사용 동기·이용 맥락 중 최소 2개 축이 서로 달라야 한다. 전원이 같은 연령대·직군이면 안 된다.
- positivity bias 방지 지시: "성공적이고 호의적인 인물"로 균질화하지 말 것. 각 페르소나에 "이 페르소나가 반대할 결정들" 섹션 필수 (최소 3개).
- anti-persona 정의: 제품을 쓰지 않거나 떠날 사용자. 왜 안 쓰는지가 핵심 정보.

- [ ] **Step 2: journey-mapping.md 작성**

- 5단계 고정: awareness → consideration → decision → usage → advocacy.
- 단계별 기록 항목: 행동 / 생각 / 감정 점수(-2~+2 정수) / 터치포인트 / pain point.
- 감정 점수 규칙: 5단계 전부 양수 금지(비현실적 낙관 방지) — 최소 한 단계는 0 이하.
- anti-persona는 저니맵 생성 제외.

- [ ] **Step 3: confidence-levels.md 작성**

- 3등급 기준표 (스펙 §4.2 그대로): assumption(아이디어만) / partial(인터뷰 1~2건 일부 속성 뒷받침) / validated(인터뷰 3건+ 핵심 속성 뒷받침).
- 승격 규칙: 인터뷰 추가 → `generate --update` 시 속성별로 인용 가능한 인터뷰를 `sources`에 연결, 기준 충족 시 등급 상향. 하향도 가능(인터뷰가 가정과 모순되면 해당 속성 수정 + partial 강등).
- 고지 문구 원문: assumption 등급 카드 상단 배너 "⚪ 가정 기반 proto-persona — 실사용자 검증 전에는 중요한 의사결정 근거로 사용하지 마세요."

- [ ] **Step 4: interview-analysis.md 작성**

- 인터뷰 노트 입력 형식: `research/interview-NN-<참가자별칭>.md` (원문 그대로 붙여넣기 허용).
- 추출 절차: ① 발화에서 니즈·불만·행동 증거 문장 추출 ② 증거 문장에 `[I-NN]` 태그 부여 ③ 페르소나 속성과 매핑. 추론과 직접 증거를 구분 표기.
- 편향 경고: 응답자가 3명 미만이면 "표본 부족 — partial 이상 등급 불가"를 명시하게 함.

- [ ] **Step 5: Commit**

```bash
git add core/methodology/ && git commit -m "docs(core): 방법론 문서 4종 (persona/journey/confidence/interview)"
```

### Task 2: 산출물 템플릿 3종

**Files:**
- Create: `core/templates/persona-card.md`
- Create: `core/templates/journey-map.md`
- Create: `core/templates/consultation.md`

- [ ] **Step 1: persona-card.md 작성** — 스펙 §4.1 frontmatter 전체 필드를 예시 값과 함께 포함. YAML은 build.py 파서가 지원하는 부분집합만 사용한다는 주석 명시: 스칼라, `["a", "b"]` 인라인 리스트, `{ k: v }` 인라인 딕셔너리, 정수. 블록 스타일 중첩 금지. 본문 골격: `## 서사`, `## 니즈 상세`, `## 이 페르소나가 반대할 결정들`.

- [ ] **Step 2: journey-map.md 작성** — frontmatter(`persona_id`, `stages`, `emotions`, `touchpoints`, `pain_points`) + 본문에 단계별 표(행동/생각/감정/터치포인트/pain point).

- [ ] **Step 3: consultation.md 작성** — frontmatter(`date`, `topic`, `reactions: { p01: accept, ... }`) + 본문 골격: `## 질문`, `## 페르소나별 반응`(수용/중립/거부 + 이유), `## 합의점과 충돌점`, `## 신뢰도 고지`.

- [ ] **Step 4: Commit**

```bash
git add core/templates/ && git commit -m "docs(core): 산출물 템플릿 3종"
```

---

## Track B — build.py (python-engineer, sonnet, TDD)

### Task 3: frontmatter 파서 (YAML 부분집합)

**Files:**
- Create: `core/visualizer/build.py`
- Create: `tests/test_frontmatter.py`
- Create: `tests/fixtures/personas/cards/persona-01-kim-seoyeon.md`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_frontmatter.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import parse_frontmatter

def test_scalar_and_int():
    text = "---\nid: p01\nname: \"김서연\"\ntech_savviness: 4\n---\n본문"
    meta, body = parse_frontmatter(text)
    assert meta["id"] == "p01"
    assert meta["name"] == "김서연"
    assert meta["tech_savviness"] == 4
    assert body.strip() == "본문"

def test_inline_list_and_dict():
    text = '---\ngoals: ["빠른 결정", "재작업 방지"]\ndemographics: { age: 32, occupation: "디자이너" }\n---\n'
    meta, _ = parse_frontmatter(text)
    assert meta["goals"] == ["빠른 결정", "재작업 방지"]
    assert meta["demographics"]["age"] == 32

def test_negative_int_list():
    text = "---\nemotions: [1, -2, 0, 2, 1]\n---\n"
    meta, _ = parse_frontmatter(text)
    assert meta["emotions"] == [1, -2, 0, 2, 1]

def test_missing_frontmatter_raises():
    import pytest
    with pytest.raises(ValueError):
        parse_frontmatter("frontmatter 없는 문서")
```

- [ ] **Step 2: 실패 확인** — Run: `python3 -m pytest tests/test_frontmatter.py -v` / Expected: FAIL (`ImportError` 또는 `ModuleNotFoundError`)

- [ ] **Step 3: 최소 구현**

```python
# core/visualizer/build.py
"""persona-maker visualizer builder. Stdlib only."""
import json, re

def _parse_value(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [] if not inner else [_parse_value(v) for v in _split_top(inner)]
    if raw.startswith("{") and raw.endswith("}"):
        out = {}
        for pair in _split_top(raw[1:-1]):
            k, v = pair.split(":", 1)
            out[k.strip().strip('"')] = _parse_value(v)
        return out
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw

def _split_top(s):
    parts, depth, cur = [], 0, ""
    in_str = False
    for ch in s:
        if ch == '"':
            in_str = not in_str
        if not in_str:
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(cur); cur = ""; continue
        cur += ch
    if cur.strip():
        parts.append(cur)
    return parts

def parse_frontmatter(text):
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    if not m:
        raise ValueError("frontmatter block (---) not found")
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, val = line.partition(":")
        meta[key.strip()] = _parse_value(val)
    return meta, m.group(2)
```

- [ ] **Step 4: 통과 확인** — Run: `python3 -m pytest tests/test_frontmatter.py -v` / Expected: 4 PASS

- [ ] **Step 5: fixture 카드 생성** — `tests/fixtures/personas/cards/persona-01-kim-seoyeon.md`에 스펙 §4.1 예시 frontmatter 전체 + 본문 3섹션을 실제 값으로 채워 저장 (Task 2 템플릿과 동일 구조).

- [ ] **Step 6: Commit**

```bash
git add core/visualizer/build.py tests/ && git commit -m "feat(visualizer): frontmatter parser (YAML subset, stdlib only)"
```

### Task 4: 산출물 수집·검증

**Files:**
- Modify: `core/visualizer/build.py`
- Create: `tests/test_collect.py`
- Create: `tests/fixtures/personas/` 나머지 (config.json, cards 2·3번, journeys/, consultations/, 깨진 카드 1개)

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_collect.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import collect
FIX = pathlib.Path(__file__).parent / "fixtures" / "personas"

def test_collect_personas_journeys_consultations():
    data = collect(FIX)
    ids = [p["id"] for p in data["personas"]]
    assert "p01" in ids and len(data["personas"]) == 3  # 깨진 카드 제외
    assert data["journeys"][0]["persona_id"] == "p01"
    assert data["consultations"][0]["topic"]
    assert data["config"]["persona_count"] == 5

def test_broken_card_becomes_warning_not_crash():
    data = collect(FIX)
    assert any("persona-99-broken.md" in w for w in data["warnings"])

def test_missing_required_field_warns():
    # persona-03 fixture는 confidence 필드 없음 → 경고 + assumption 기본값
    data = collect(FIX)
    p03 = next(p for p in data["personas"] if p["id"] == "p03")
    assert p03["confidence"] == "assumption"
    assert any("p03" in w and "confidence" in w for w in data["warnings"])
```

- [ ] **Step 2: fixture 확장** — `config.json`(`{"model": "haiku", "persona_count": 5, "language": "ko"}`), 카드 p02(secondary/validated, sources 포함)·p03(confidence 필드 누락), `persona-99-broken.md`(frontmatter 없음), `journeys/journey-p01.md`, `consultations/2026-07-09-onboarding.md` 생성. 값은 전부 실제 예시로 채운다.

- [ ] **Step 3: 실패 확인** — Run: `python3 -m pytest tests/test_collect.py -v` / Expected: FAIL (`collect` 미정의)

- [ ] **Step 4: 구현** — `collect(personas_dir)`: `cards/*.md`·`journeys/*.md`·`consultations/*.md`를 glob → `parse_frontmatter` 시도, `ValueError`는 `warnings`에 파일명과 함께 추가하고 건너뜀. 필수 필드(`id`,`name`,`role`,`confidence`) 검사 — 누락 시 경고 + 기본값(`confidence`→`assumption`). `config.json` 없으면 기본값 사용 + 경고. 반환: 공유 데이터 계약의 dict.

- [ ] **Step 5: 통과 확인** — Run: `python3 -m pytest tests/ -v` / Expected: 전체 PASS

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "feat(visualizer): collect & validate persona artifacts with warnings"
```

### Task 5: HTML 조립 + CLI

**Files:**
- Modify: `core/visualizer/build.py`
- Create: `tests/test_build_html.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_build_html.py
import sys, pathlib, json, re
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "core" / "visualizer"))
from build import build_html
FIX = pathlib.Path(__file__).parent / "fixtures" / "personas"

def test_injects_json_into_marker(tmp_path):
    template = "<script>const DATA = /*__PERSONA_DATA__*/{}/*__END__*/;</script>"
    out = build_html(FIX, template)
    m = re.search(r"/\*__PERSONA_DATA__\*/(.*)/\*__END__\*/", out, re.DOTALL)
    data = json.loads(m.group(1))
    assert data["personas"][0]["id"] == "p01"

def test_marker_missing_raises():
    import pytest
    with pytest.raises(ValueError):
        build_html(FIX, "<html>no marker</html>")
```

- [ ] **Step 2: 실패 확인** — Run: `python3 -m pytest tests/test_build_html.py -v` / Expected: FAIL

- [ ] **Step 3: 구현** — `build_html(personas_dir, template_text)`: `collect()` 결과를 `json.dumps(ensure_ascii=False)`로 직렬화해 `/*__PERSONA_DATA__*/…/*__END__*/` 마커 사이에 치환. 마커 없으면 `ValueError`. `main()`: argparse로 `--personas-dir`(기본 `personas`), `--template`(기본 스크립트 옆 `template.html`), `--output`(기본 `<personas-dir>/index.html`), warnings를 stderr로 출력, `if __name__ == "__main__": main()`.

- [ ] **Step 4: 통과 확인** — Run: `python3 -m pytest tests/ -v` / Expected: 전체 PASS

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat(visualizer): HTML assembly with data injection + CLI"
```

---

## Track C — template.html (frontend-engineer, sonnet)

### Task 6: HTML 셸 — 탭·데이터 로딩·카드 패널

**Files:**
- Create: `core/visualizer/template.html`

- [ ] **Step 1: 셸 작성** — 단일 파일, 외부 리소스 참조 0 (CSP 불필요하지만 원칙 유지). 구조:

```html
<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>persona-maker</title>
<style>/* 다크 기본 + prefers-color-scheme: light 대응, 시스템 폰트 스택 */</style>
</head><body>
<header>
  <h1 id="project-title"></h1>
  <nav id="tabs"><!-- constellation | needs | journeys | decisions --></nav>
  <div id="confidence-legend"><!-- ⚪🟡🟢 등급 범례 --></div>
</header>
<canvas id="stage"></canvas>
<aside id="card-panel" hidden><!-- 페르소나 카드 상세 --></aside>
<div id="warnings" hidden></div>
<script>
const DATA = /*__PERSONA_DATA__*/{"config":{},"personas":[],"journeys":[],"consultations":[],"warnings":[]}/*__END__*/;
// scene registry: 각 씬은 {enter(ctx,data), tick(dt), onClick(x,y), exit()} 인터페이스 구현
</script>
</body></html>
```

- [ ] **Step 2: 공통 로직 구현** — 탭 전환(씬 registry에서 enter/exit 호출), 캔버스 리사이즈(devicePixelRatio 대응), `requestAnimationFrame` 루프, 카드 패널 렌더러(페르소나 frontmatter 전 필드 + 등급 배너: assumption이면 confidence-levels.md의 경고 문구 표시), warnings 표시. 파티클 공통 클래스: `{x,y,vx,vy,target:{x,y},radius,color,alpha,dashed}` + 스프링 이동(`v += (target-pos)*k; v *= damping`).

- [ ] **Step 3: 수동 스모크 테스트** — Run: `python3 core/visualizer/build.py --personas-dir tests/fixtures/personas --output /tmp/index.html && open /tmp/index.html` / Expected: 탭 4개·범례·빈 캔버스 렌더링, 콘솔 에러 0.

- [ ] **Step 4: Commit**

```bash
git add core/visualizer/template.html && git commit -m "feat(visualizer): HTML shell with tabs, card panel, particle base"
```

### Task 7: Particle 엔진 + Constellation 씬

**Files:**
- Modify: `core/visualizer/template.html`

- [ ] **Step 1: Constellation 구현** — 페르소나당 파티클 군집 30~50개(황금각 나선 배치)가 페르소나 위치(원형 레이아웃)로 스프링 수렴. 시각 언어: `assumption` = alpha 0.45 + `setLineDash([3,4])` 외곽선, `partial` = alpha 0.7, `validated` = alpha 1.0 실선. role별 색상(primary 강조색, anti는 채도 낮은 경고색). 라벨: 이름 + archetype + 등급 이모지. 클릭 → 해당 군집 파티클이 화면 가장자리로 흩어지며 카드 패널 오픈, 닫으면 복귀.

- [ ] **Step 2: 스모크 테스트** — fixture 3명(assumption/validated/confidence 누락→assumption)이 시각적으로 구분되는지, 클릭 상호작용 확인. 콘솔 에러 0.

- [ ] **Step 3: Commit**

```bash
git add core/visualizer/template.html && git commit -m "feat(visualizer): constellation scene with confidence visual language"
```

### Task 8: Needs Landscape · Journey Emotions · Decision Log 씬

**Files:**
- Modify: `core/visualizer/template.html`

- [ ] **Step 1: Needs Landscape** — 전체 페르소나의 `goals`+`frustrations` 항목을 노드로, 동일/유사 텍스트(공백 제거 후 부분 문자열 매칭)를 병합해 공유 수를 카운트. 노드 반경 ∝ 공유 페르소나 수, 파티클이 노드 주위를 궤도 운동. 상위 3개 pain point는 라벨 강조. 호버 시 공유 페르소나 이름 툴팁.

- [ ] **Step 2: Journey Emotions** — x축 5단계, y축 감정 점수(-2~+2). 페르소나별 감정 곡선을 따라 파티클이 흐름(곡선 경로 위 이동 + 잔상). 페르소나 토글 가능. 전체 최저점 단계에 "개선 기회" 마커 자동 표시. journeys가 빈 배열이면 "저니맵이 아직 없습니다 — /persona-maker:generate 실행" 안내 텍스트.

- [ ] **Step 3: Decision Log** — consultations 목록을 좌측에, 선택 시 페르소나 파티클들이 accept(우측·초록)/neutral(중앙)/reject(좌측·적색)으로 갈라짐. 신뢰도 고지 문구 하단 표시. consultations 빈 배열이면 안내 텍스트.

- [ ] **Step 4: 스모크 테스트** — Run: Task 6 Step 3과 동일 명령 / Expected: 4개 씬 전환·상호작용 정상, 콘솔 에러 0.

- [ ] **Step 5: Commit**

```bash
git add core/visualizer/template.html && git commit -m "feat(visualizer): needs/journey/decision scenes"
```

---

## Track D — Claude 플러그인 (plugin-engineer, sonnet, Track A 완료 후)

### Task 9: plugin.json + init 스킬

**Files:**
- Create: `claude-plugin/.claude-plugin/plugin.json`
- Create: `claude-plugin/skills/init/SKILL.md`

- [ ] **Step 1: plugin.json 작성**

```json
{
  "name": "persona-maker",
  "version": "0.1.0",
  "description": "편견 없는 사용자 관점 의사결정을 위한 페르소나 리서치 플러그인",
  "author": { "name": "justin" }
}
```

- [ ] **Step 2: init/SKILL.md 작성** — frontmatter(`name: init`, `description: persona-maker 프로젝트 초기화 — personas/ 구조와 config.json 생성`). 본문 지시: ① `personas/{research,cards,journeys,consultations}` 생성 ② `personas/config.json`을 `{"model": "haiku", "persona_count": 5, "language": "ko"}`로 생성(이미 있으면 덮어쓰지 않고 현재 설정 표시) ③ 다음 단계(research) 안내. 설정 변경 요청 시 config.json 수정 방법 안내.

- [ ] **Step 3: Commit**

```bash
git add claude-plugin/ && git commit -m "feat(claude-plugin): plugin manifest + init skill"
```

### Task 10: research 스킬

**Files:**
- Create: `claude-plugin/skills/research/SKILL.md`

- [ ] **Step 1: SKILL.md 작성** — 지시 흐름: ① 입력 판별(아이디어 서술 → `research/idea-brief.md` 저장 / 인터뷰 노트 → `research/interview-NN-<별칭>.md` 저장) ② `core/methodology/interview-analysis.md` 절차에 따라(플러그인 루트 상대 경로 `${CLAUDE_PLUGIN_ROOT}/../core/...` 참조) 인사이트 요약 `research/insights.md` 생성 — 니즈·행동·pain point 후보 + 증거 태그 `[I-NN]` ③ 입력 소스 기록: 아이디어만이면 `available_confidence: assumption`, 인터뷰 N건이면 건수 기록 ④ 다음 단계(generate) 안내. 이 단계는 메인 세션 모델이 직접 수행(서브에이전트 아님 — 오케스트레이션 분업 원칙).

- [ ] **Step 2: Commit**

```bash
git add claude-plugin/skills/research/ && git commit -m "feat(claude-plugin): research skill"
```

### Task 11: generate 스킬 + persona-generator 에이전트

**Files:**
- Create: `claude-plugin/agents/persona-generator.md`
- Create: `claude-plugin/skills/generate/SKILL.md`

- [ ] **Step 1: persona-generator.md 작성** — frontmatter: `name: persona-generator`, `description: 단일 페르소나 카드(+저니맵)를 방법론에 따라 생성`, `model: haiku`, `tools: Read, Write`. 본문: 입력으로 받는 것(인사이트 요약 경로, 담당 슬롯 정의, 템플릿 경로, config), 출력 규칙(frontmatter는 YAML 부분집합만, 필수 필드 전부 포함, positivity bias 금지 지시 재강조, anti-persona면 저니맵 생성 안 함), 완료 보고 형식(생성 파일 경로 목록).

- [ ] **Step 2: generate/SKILL.md 작성** — 지시 흐름: ① `config.json` 읽기 — `model` 값을 서브에이전트 디스패치 시 model 파라미터로 전달 ② `research/insights.md` 없으면 차단 + research 안내 ③ 슬롯 설계(메인 세션): persona_count에 맞춰 primary 1·anti 1·나머지 secondary, 다양성 규칙(persona-framework.md)에 따라 슬롯별 차별화 축 정의 ④ **슬롯당 persona-generator 서브에이전트 1개를 병렬 디스패치** ⑤ 산출물 frontmatter 필수 필드 검증 — 실패 슬롯만 1회 재디스패치 ⑥ `--update` 모드: 기존 카드 + 신규 인터뷰를 대조해 confidence-levels.md 승격 규칙 적용, 변경된 카드만 재작성 ⑦ visualize 안내.

- [ ] **Step 3: Commit**

```bash
git add claude-plugin/ && git commit -m "feat(claude-plugin): generate skill + haiku persona-generator agent"
```

### Task 12: visualize + consult 스킬

**Files:**
- Create: `claude-plugin/skills/visualize/SKILL.md`
- Create: `claude-plugin/skills/consult/SKILL.md`

- [ ] **Step 1: visualize/SKILL.md 작성** — 지시: ① `python3 ${CLAUDE_PLUGIN_ROOT}/../core/visualizer/build.py --personas-dir personas` 실행 ② stderr 경고를 사용자에게 요약 전달 ③ `python3 -m http.server 8765 --directory personas`를 백그라운드 실행 후 `http://localhost:8765/index.html` 안내 ④ 포트 충돌 시 8766~8775 순차 시도.

- [ ] **Step 2: consult/SKILL.md 작성** — 지시: ① 의사결정 질문 접수 ② `cards/*.md` 전체 로드 ③ config의 model로 서브에이전트 1개 디스패치 — 페르소나별 반응(accept/neutral/reject + 근거는 해당 카드의 goals/frustrations/반대할 결정들에서 인용) ④ 메인 세션이 합의점·충돌점 종합 ⑤ `consultations/YYYY-MM-DD-<주제-slug>.md`로 저장(consultation.md 템플릿) — 신뢰도 고지 필수: assumption 등급 카드가 근거에 포함되면 명시 ⑥ visualize 재실행 안내.

- [ ] **Step 3: Commit**

```bash
git add claude-plugin/skills/ && git commit -m "feat(claude-plugin): visualize + consult skills"
```

---

## Track E — Codex 어댑터 (adapter-engineer, sonnet, Track D 완료 후)

### Task 13: codex-skill/SKILL.md

**Files:**
- Create: `codex-skill/SKILL.md`

- [ ] **Step 1: SKILL.md 작성** — Claude 스킬 5개의 지시 흐름을 단일 SKILL.md로 통합(Codex는 서브커맨드 구조가 없으므로 "모드: init|research|generate|visualize|consult"를 인자로 판별). 차이점만 명시: 기본 모델 `gpt-5-mini`(config.json 기본값을 `{"model": "gpt-5-mini", ...}`로 생성), 서브에이전트 디스패치는 Codex의 스폰 메커니즘 사용. 방법론·템플릿·build.py는 `../core/` 상대 경로로 동일 참조.

- [ ] **Step 2: Commit**

```bash
git add codex-skill/ && git commit -m "feat(codex): single-file skill adapter (gpt-5-mini default)"
```

---

## 최종 — 통합 검증 (Fable 직접)

### Task 14: E2E 워크스루 + README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 전체 테스트** — Run: `python3 -m pytest tests/ -v` / Expected: 전체 PASS
- [ ] **Step 2: E2E 시나리오 A (아이디어만)** — 임시 디렉토리에서 init→research(아이디어 1문단)→generate→visualize 순서로 스킬 지시를 따라 수행. 검증: 카드 5장 전부 `confidence: assumption`, anti-persona 저니맵 없음, index.html 4개 씬 정상.
- [ ] **Step 3: E2E 시나리오 B (인터뷰 3건 추가)** — research로 인터뷰 3건 추가 → `generate --update`. 검증: 등급 승격 발생, sources에 인터뷰 인용, 파일 단위 갱신(전체 재생성 아님)을 git diff로 확인.
- [ ] **Step 4: README.md 작성** — 설치(플러그인 등록 방법), 5개 커맨드 워크플로우, config.json 옵션표, 신뢰도 등급 설명, 스크린샷 자리는 파일 경로만 기재.
- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "docs: README + E2E 검증 완료"
```
