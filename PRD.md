# persona-maker PRD

> **AI 에이전트에게:** 이 문서는 구현 지침입니다. 불명확한 부분은 추측하지 말고
> 사용자에게 질문하세요. 구현 중 결정이 바뀌면 이 문서를 갱신해 source of truth로
> 유지하세요. `(가정)` 표시 항목은 사용자가 확인하지 않은 내용이니, 의존하기
> 전에 사용자에게 확인하세요.
>
> 상세 설계는 `docs/superpowers/specs/2026-07-09-persona-maker-design.md`,
> 태스크 단위 구현 절차는 `docs/superpowers/plans/2026-07-09-persona-maker.md`를 따르세요.

## 1. 개요

디자이너·개발자·기획자는 제품 결정을 내릴 때 자신의 취향과 편견에 기대기 쉽고, 이는
재작업과 사용자 이탈로 이어진다. persona-maker는 리서치 모범사례에 따라 페르소나
카드·저니맵을 생성하고 "이 결정을 각 페르소나는 어떻게 받아들일까?"를 상시 질의할 수
있게 하여, **철저히 사용자의 시각에서 의사결정하는 기준점**을 제공하는 Claude Code
플러그인(+ Codex 스킬)이다. AI 합성 페르소나의 알려진 함정(positivity bias, 정체성
평면화)에 대한 방어로 **신뢰도 3등급 체계**(assumption/partial/validated)를 내장하는
것이 차별점이다.

## 2. 대상 사용자 & JTBD

- **누가:** 초기 스타트업의 디자이너·개발자·기획자 (1인 창업자 포함).
- **어떤 상황에서:** 제품 개발 착수 전 또는 기능 의사결정 순간에, 정식 UX 리서치
  조직 없이 아이디어 메모나 소수의 인터뷰 노트만 가진 상황.
- **무엇을 이루려고:** 주관적 편견 대신 사용자 관점의 근거로 결정하고, 그 근거의
  신뢰도(가정인지 검증인지)를 투명하게 알고 싶다.

## 3. 핵심 기능 (스코프)

1. **`/persona-maker:init`** — 사용자 프로젝트에 `personas/` 구조와
   `config.json`(모델·인원수·언어)을 생성한다. 이미 있으면 덮어쓰지 않고 현재 설정을 보여준다.
2. **`/persona-maker:research`** — 아이디어 서술 또는 인터뷰 노트를 받아
   `research/`에 저장하고, 니즈·행동·pain point 후보를 증거 태그와 함께 정리한
   `research/insights.md`를 만든다. 입력 소스가 신뢰도 등급 상한을 결정한다.
3. **`/persona-maker:generate`** — 인사이트 요약을 기반으로 페르소나 카드(기본 5명
   = primary 1 + secondary 3 + anti-persona 1)와 저니맵(anti 제외)을 생성한다.
   페르소나 1명당 저가 모델 서브에이전트 1개를 병렬 디스패치한다(Claude: haiku 기본,
   Codex: gpt-5-mini 기본, config로 변경). `--update` 모드는 신규 인터뷰를 반영해
   기존 카드의 등급·속성만 갱신한다(전체 재생성 금지).
4. **`/persona-maker:visualize`** — 산출물 마크다운을 파싱해 의존성 0의 자기완결
   `index.html`(Canvas 2D particle, 4개 씬: Constellation / Needs Landscape /
   Journey Emotions / Decision Log)을 생성하고 로컬 서버로 연다. 신뢰도 등급이 시각
   언어(흐릿한 점선 vs 선명한 입자)로 표현된다.
5. **`/persona-maker:consult`** — 의사결정 질문에 대해 각 페르소나의
   수용/중립/거부 반응과 근거를 생성하고, 합의점·충돌점·신뢰도 고지를 담아
   `consultations/`에 누적한다. 결과는 시각화 Decision Log 씬에 반영된다.

## 4. Non-Goals (하지 않는 것)

- 이번 버전에서 클라우드 호스팅·팀 공유·실시간 협업 기능은 구현하지 않는다 (로컬 파일 + 로컬호스트만).
- 이번 버전에서 실사용자 인터뷰 모집·녹취·전사 자동화는 구현하지 않는다 (노트는 사용자가 직접 입력).
- 이번 버전에서 정량 서베이 데이터의 통계적 클러스터링(k-means 등)은 구현하지 않는다.
- 이번 버전에서 React/Vite 등 빌드 도구 기반 웹앱은 만들지 않는다 (단일 HTML 원칙) `[변경 금지]`.
- 이번 버전에서 페르소나 프로필 이미지 생성은 하지 않는다. (가정)
- 이번 버전에서 한국어·영어 외 언어의 산출물 품질 보증은 하지 않는다. (가정)

## 5. 기술 제약 & 기존 결정

- 공유 코어(`core/`) + 플랫폼 어댑터(`claude-plugin/`, `codex-skill/`) 구조 — 방법론
  수정이 양쪽에 동시 반영되도록 `[변경 금지]`.
- 시각화는 자기완결 단일 HTML, 외부 CDN·폰트·패키지 참조 금지 `[변경 금지]`.
- `build.py`는 Python 3 표준 라이브러리만 사용 (pytest는 개발 전용) `[변경 금지]`.
- frontmatter는 build.py가 파싱 가능한 YAML 부분집합(스칼라·인라인 리스트·인라인
  딕셔너리·정수)만 사용 — 생성 에이전트 지시문에 명시.
- 페르소나 생성 모델: Claude 어댑터 haiku 기본, Codex 어댑터 gpt-5-mini 기본,
  `personas/config.json`에서 언제든 변경 가능 `[변경 금지]`.
- 오케스트레이션(인사이트 요약·상담 종합)은 메인 세션 모델, 대량 생성은 저가 모델 — 비용 분업 원칙.
- 다루는 데이터: 페르소나 카드(id, 이름, role, archetype, confidence, sources,
  demographics, goals, frustrations, behaviors, tech_savviness, quote, 서사, 반대할
  결정들), 저니맵(persona_id, 5단계, 감정 점수 -2~+2, 터치포인트, pain point),
  상담 기록(date, topic, 페르소나별 reactions), 설정(model, persona_count, language).
- 개인정보: 인터뷰 노트는 사용자 로컬에만 저장되며 외부 전송 없음. 참가자는 별칭으로만 기록. (가정)

## 6. 페이즈별 요구사항

### Phase 1: 공유 코어 + 시각화

**목표:** 방법론·템플릿·빌더·시각화가 완성되어 fixture 데이터만으로 particle 시각화를 열어볼 수 있다.

**요구사항:**
1. `core/methodology/` 문서 4종 작성 (persona-framework, journey-mapping, confidence-levels, interview-analysis) — 다양성 규칙(secondary 간 최소 2개 차별화 축), positivity bias 방지 지시, 등급 승격·강등 규칙 포함.
2. `core/templates/` 3종 작성 (persona-card, journey-map, consultation) — frontmatter 스키마와 본문 골격 포함.
3. `core/visualizer/build.py`: frontmatter 파서(YAML 부분집합) → 산출물 수집·검증(깨진 파일은 경고 후 건너뜀, 필수 필드 누락 시 기본값+경고) → `/*__PERSONA_DATA__*/` 마커 JSON 주입 → CLI(`--personas-dir`, `--template`, `--output`).
4. `core/visualizer/template.html`: 탭 4개·카드 패널·파티클 베이스 + Constellation(등급별 시각 언어, 클릭 시 카드), Needs Landscape(공유 pain point 클러스터), Journey Emotions(감정 곡선 흐름 + 최저점 마커), Decision Log(찬반 분산) 씬. 데이터 없는 씬은 안내 문구 표시.
5. pytest 테스트: 파서·수집·HTML 조립 (fixture: 정상 카드 2, 필드 누락 카드 1, 깨진 카드 1, 저니맵 1, 상담 1).

**수용 기준:**
- [ ] `python3 -m pytest tests/ -v` 전체 통과.
- [ ] `python3 core/visualizer/build.py --personas-dir tests/fixtures/personas --output /tmp/index.html` 실행 시 exit code 0, 깨진 카드 경고가 stderr에 출력된다.
- [ ] 생성된 index.html을 브라우저에서 열면 4개 탭이 모두 전환되고 콘솔 에러가 0건이다.
- [ ] assumption 등급 페르소나는 점선·저투명도로, validated는 실선·고투명도로 렌더링된다.
- [ ] index.html이 외부 URL을 하나도 참조하지 않는다 (`grep -c "https://" /tmp/index.html` 결과에 리소스 로드용 URL 0건).

### Phase 2: Claude Code 플러그인 (Phase 1의 코어 필요)

**목표:** Claude Code에서 5개 커맨드로 init→research→generate→visualize→consult 전체 워크플로우가 동작한다.

**요구사항:**
1. `claude-plugin/.claude-plugin/plugin.json` 매니페스트.
2. 스킬 5종 (init/research/generate/visualize/consult) — research·generate·visualize·consult는 시작 시 config.json 부재 시 init 안내 후 중단.
3. `agents/persona-generator.md` (model: haiku, 도구 Read·Write 한정) — 슬롯당 1개 병렬 디스패치, 출력 frontmatter 검증 실패 시 해당 슬롯만 1회 재시도.
4. `generate --update`: 기존 카드 유지하며 등급·속성만 갱신, 변경 카드만 재작성.
5. consult 결과의 신뢰도 고지: assumption 등급 카드가 근거에 포함되면 명시.

**수용 기준:**
- [ ] 빈 디렉토리에서 init 실행 시 `personas/{research,cards,journeys,consultations}`와 config.json이 생성된다.
- [ ] 아이디어 1문단만으로 research→generate 실행 시 카드 5장이 생성되고 전부 `confidence: assumption`이다.
- [ ] anti-persona의 저니맵 파일이 존재하지 않는다.
- [ ] 인터뷰 노트 3건 추가 후 `generate --update` 실행 시 최소 1개 카드의 confidence가 상향되고 sources에 인터뷰 파일이 인용된다.
- [ ] visualize 실행 시 `http://localhost:<port>/index.html`이 열리고, 포트 충돌 시 8766~8775를 순차 시도한다.
- [ ] consult 실행 시 `consultations/`에 날짜-주제 파일이 생성되고 페르소나 전원의 accept/neutral/reject가 기록된다.

### Phase 3: Codex 어댑터 + 문서화 (Phase 2의 스킬 흐름 필요)

**목표:** 동일 워크플로우가 Codex에서 gpt-5-mini 기본값으로 동작하고, README로 설치·사용이 안내된다.

**요구사항:**
1. `codex-skill/SKILL.md` — 모드 인자(init|research|generate|visualize|consult)로 5개 흐름 통합, config 기본 model이 gpt-5-mini.
2. `README.md` — 설치, 워크플로우, config 옵션표, 신뢰도 등급 설명.
3. E2E 워크스루 2종(아이디어만 / 인터뷰 3건) 수행 및 결과를 플랜 Task 14 기준으로 검증.

**수용 기준:**
- [ ] codex-skill/SKILL.md에 5개 모드 분기와 gpt-5-mini 기본값이 모두 명시되어 있다.
- [ ] README의 명령 예시를 그대로 따라 하면 Phase 2 수용 기준의 워크플로우가 재현된다.
- [ ] `python3 -m pytest tests/ -v` 전체 통과 (회귀 없음).

## 7. 성공 지표

- 아이디어 입력부터 시각화 확인까지(init→visualize) 사용자 개입 제외 15분 이내에 완료된다. (가정)
- 페르소나 5명 생성 시 대량 텍스트 생성이 전부 저가 모델(haiku/gpt-5-mini)에서 실행된다 — 메인 세션 모델의 생성 호출 0건.
- 모든 페르소나 카드가 신뢰도 등급과 (validated의 경우) 출처 인용을 갖는다 — build.py 경고 0건.
