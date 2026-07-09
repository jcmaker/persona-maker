<!--
  journey-map.md — 저니맵 1건 생성 템플릿

  persona-generator 서브에이전트가 페르소나 1명의 저니맵을 쓸 때 그대로 복사해 채우는
  뼈대다. 값은 예시이며 실제 내용으로 전부 교체한다. 상세 규칙은
  core/methodology/journey-mapping.md 를 따른다.

  중요: role: anti 페르소나에는 저니맵을 생성하지 않는다 (journey-mapping.md §1,
  persona-framework.md §4). 제품을 쓰지 않는 사용자에게 사용 여정은 존재하지 않는다.

  frontmatter YAML 부분집합 (core/visualizer/build.py 파서가 지원하는 전부): 스칼라,
  "따옴표 문자열", 정수, [a, b] / ["a", "b"] 인라인 리스트, { k: v } 인라인 딕셔너리.
  블록 스타일(들여쓰기 중첩, `- ` 블록 리스트) 금지.

  주의: 아래 예시의 `# ...` 는 이 템플릿 파일에서만 쓰는 설명용 인라인 주석이다.
  파서는 줄 전체가 `#`으로 시작할 때만 건너뛴다 — 값 뒤에 붙은 인라인 주석은 값
  문자열에 그대로 포함되어 파싱이 깨진다. 실제 저니맵을 저장할 때는 `# ...` 부분을
  반드시 삭제한다.
-->
---
persona_id: p01
stages: [awareness, consideration, decision, usage, advocacy]   # 5개 고정, 이 순서 그대로 — 추가·삭제·순서 변경 금지
emotions: [1, -1, 0, 2, 1]   # 정수 5개, -2~+2, stages와 인덱스 1:1 대응. 전부 양수 금지 — 최소 1개는 0 이하
touchpoints: ["...", "..."]  # 단계별 접점(채널/화면/사람), stages와 같은 순서로 5개
pain_points: ["...", "..."]  # 단계별 마찰, 5단계 모두 채운다 — "없음"으로 비워두지 않는다
---

## 단계별 여정

<!-- journey-mapping.md §3: 단계마다 행동/생각/감정/터치포인트/pain point를 전부 채운다.
     5행 고정, stages와 같은 순서. 감정 값은 frontmatter emotions 배열의 같은 인덱스와
     반드시 일치시킨다. 모든 단계에 pain point가 있어야 하며, 감정 곡선이 5단계 내내
     양수만은 아니어야 한다(journey-mapping.md §4). -->

| 단계 | 행동 | 생각 | 감정 | 터치포인트 | pain point |
| --- | --- | --- | --- | --- | --- |
| awareness | ... | ... | ... | ... | ... |
| consideration | ... | ... | ... | ... | ... |
| decision | ... | ... | ... | ... | ... |
| usage | ... | ... | ... | ... | ... |
| advocacy | ... | ... | ... | ... | ... |

## 요약

<!-- 감정 곡선을 2~4문장으로 서술한다. 하락 후 회복 등 굴곡이 있다면 어떤 단계에서
     왜 꺾였는지 짚어준다. -->
