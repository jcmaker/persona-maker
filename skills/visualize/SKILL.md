---
name: visualize
description: 페르소나 산출물을 particle 시각화 HTML로 빌드하고 로컬 서버로 열 때 — 사용자가 "시각화해줘", "페르소나 보여줘", "visualize" 등을 요청했을 때 실행
---

# visualize

`personas/cards/`·`personas/journeys/`·`personas/consultations/`를 조립해
particle 기반 시각화 HTML(`personas/index.html`)을 생성하고, 로컬 정적 서버로
열어 사용자가 브라우저에서 바로 볼 수 있게 한다.

## 지시사항

### 0. 전제 확인

`personas/config.json`이 없으면 다음을 안내하고 즉시 중단하라:

> 먼저 `/persona-maker:init`을 실행하세요.

`personas/cards/`에 카드가 하나도 없으면 다음을 안내하고 즉시 중단하라:

> 먼저 `/persona-maker:generate`를 실행하세요.

### 1. 빌드 실행

아래 명령을 그대로 실행한다. 출력 파일 경로와 템플릿 경로는 지정하지 않는다 —
`build.py`의 기본값(출력: `personas/index.html`, 템플릿: `build.py`와 같은
디렉토리의 `template.html`)을 그대로 쓴다.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/core/visualizer/build.py --personas-dir personas
```

- 표준 출력(stdout)에는 생성된 `index.html`의 경로 한 줄이 찍힌다.
- 표준 에러(stderr)에는 경고(깨진 frontmatter, 필드 누락, 디렉토리 없음 등)가
  0줄 이상 찍힐 수 있다. 명령 자체는 경고가 있어도 실패하지 않는다(exit code로
  성공 여부를 확인하라). exit code가 0이 아니면 stderr 전체를 사용자에게 보여주고
  중단하라.

### 2. 경고 전달

stderr에 한 줄 이상 출력됐다면, 각 경고를 다음 형식으로 사용자에게 요약해
보여줘라:

- 어떤 파일이 문제인지 (경고 메시지에 포함된 파일명/경로)
- 무엇이 잘못됐는지 (frontmatter 파싱 실패 / 필수 필드 누락 / 디렉토리 없음 등)
- 해결 방법: 해당 카드(또는 저니맵·협의 기록) 파일의 frontmatter를 직접 수정한
  뒤 `/persona-maker:visualize`를 다시 실행하면 반영된다고 안내한다.

경고가 있어도 `index.html`은 생성되므로(문제 파일만 건너뛰고 나머지로 조립),
3단계로 계속 진행한다.

### 3. 서버 오픈

아래 스크립트를 실행한다. 8765~8775 범위에서 이미 서빙 중인 서버가 있으면
재사용하고, 없으면 빈 포트에 `python3 -m http.server`를 백그라운드로 띄운 뒤
접속 URL을 stdout으로 돌려준다:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/serve.sh personas
```

- exit code 0이면 stdout의 URL(`http://localhost:<port>/index.html`)을
  사용자에게 안내하고 4단계로 넘어간다.
- exit code가 0이 아니면 stderr 메시지를 사용자에게 보여준다. 모든 포트가
  사용 중인 경우이므로, 사용자가 직접
  `python3 -m http.server <원하는 포트> --directory personas`를 실행하도록
  안내한 뒤 중단한다.

### 4. 완료 안내

서버가 열리면 다음을 사용자에게 안내한다:

- 접속 URL: `http://localhost:<port>/index.html`
- 4개 씬 간단 소개:
  - **Constellation** — 전체 페르소나를 파티클로 한눈에 보는 개요 씬
  - **Needs Landscape** — 페르소나별 니즈·불만을 좌표 공간에 펼친 씬
  - **Journey Emotions** — 저니맵의 단계별 감정 곡선을 보여주는 씬
  - **Decision Log** — `/persona-maker:consult` 협의 기록을 누적해 보여주는 씬
- "인터뷰를 추가하면 `/persona-maker:research` → `/persona-maker:generate --update`
  → `/persona-maker:visualize` 순서로 다시 실행해 시각화를 최신 상태로 갱신할 수
  있습니다."
- "특정 기능·디자인 결정에 대해 페르소나들의 반응을 미리 확인하려면
  `/persona-maker:consult`를 실행하세요."
