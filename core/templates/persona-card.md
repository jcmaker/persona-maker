<!--
  persona-card.md — 페르소나 카드 1장 생성 템플릿

  이 파일은 persona-generator 서브에이전트(haiku/gpt-5-mini)가 페르소나 카드를 쓸 때
  그대로 복사해 채우는 뼈대다. 값은 예시이며 그대로 쓰지 말고 실제 페르소나 내용으로
  전부 교체한다. 상세 규칙은 core/methodology/persona-framework.md 와
  core/methodology/confidence-levels.md 를 따른다 — 이 파일의 주석은 그 규칙의 요약일 뿐
  원문을 대체하지 않는다.

  frontmatter YAML 부분집합 (core/visualizer/build.py 파서가 지원하는 전부):
    - 스칼라(quote 없는 값, role/confidence 등)
    - "따옴표 문자열"
    - 정수 (예: 32, 4)
    - ["a", "b"] 형태의 인라인 리스트 (한 줄)
    - { k: v } 형태의 인라인 딕셔너리 (한 줄)
  블록 스타일(들여쓰기로 중첩된 매핑, `- ` 로 시작하는 블록 리스트)은 파서가 인식하지
  못하므로 절대 쓰지 않는다.

  주의: 아래 예시의 `# ...` 는 이 템플릿 파일에서만 쓰는 설명용 인라인 주석이다.
  파서는 줄 전체가 `#`으로 시작할 때만 주석으로 건너뛰고, 값 뒤에 붙은 인라인 주석은
  건너뛰지 않는다(줄 전체가 값 문자열로 읽힌다). 실제 카드를 저장할 때는 각 줄에서
  `# ...` 부분을 반드시 삭제하고 값만 남긴다.
-->
---
id: p01
name: "김서연"
role: primary                # primary | secondary | anti — 5명 기본 구성: primary 1, secondary 3, anti 1
archetype: "바쁜 실무 디자이너"
confidence: assumption       # assumption | partial | validated — confidence-levels.md 기준. 감으로 정하지 않는다
sources: []                  # validated/partial이면 근거 인터뷰 경로: ["research/interview-01-민지.md", ...]
demographics: { age: 32, occupation: "프로덕트 디자이너", context: "5인 스타트업" }
goals: ["...", "...", "..."]           # 3~5개, "언제·어떤 상황에서·무엇을" 수준의 구체적 상황 서술 (형용사 한 단어 요약 금지)
frustrations: ["...", "...", "..."]    # 3~5개, 동일 원칙. 최소 1개는 제품/팀 자체를 향한 불만이어야 함
behaviors: ["...", "...", "..."]       # 3~5개, 동일 원칙. 최소 1개는 회피·포기·우회 행동이어야 함
tech_savviness: 4            # 1-5 정수. secondary 3명끼리는 최소 2점 이상 차이 등 분화 조건 있음 (persona-framework.md §2)
quote: "1인칭 한 문장"        # 페르소나가 직접 말하듯 쓴다. 마케팅 문구·슬로건 금지
---

## 서사

<!-- 3~5문장. demographics/archetype과 goals·frustrations를 자연스럽게 연결해, 왜 이
     사람이 이런 니즈와 불만을 갖는지 배경을 서술한다. role: anti면 "왜 이 제품을 안/못
     쓰는가"를 중심으로 쓴다 (persona-framework.md §4). -->

## 니즈 상세

<!-- goals·frustrations를 더 구체적인 상황으로 풀어쓴 3~4개 불릿. 추상적 욕구가 아니라
     "언제·어디서·무엇을 하려다 막히는지" 수준으로 쓴다. -->

## 이 페르소나가 반대할 결정들

<!-- 최소 3개. 각 항목은 "반대하는 제품/기능 결정 + 반대하는 구체적 이유"로 쓴다
     (positivity bias 방지, persona-framework.md §3). role: anti면 이 중 최소 1개는
     이 제품의 핵심 전제 자체에 대한 반대여야 한다 (persona-framework.md §4). -->
