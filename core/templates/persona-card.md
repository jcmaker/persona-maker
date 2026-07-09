<!--
  persona-card.md — template for generating one persona card

  This file is the skeleton the persona-generator subagent (haiku/gpt-5-mini)
  copies and fills in when writing a persona card. The values are examples — do
  not keep them; replace everything with real persona content. The detailed
  rules live in core/methodology/persona-framework.md and
  core/methodology/confidence-levels.md — the comments in this file are only a
  summary of those rules and do not replace the originals.

  Frontmatter YAML subset (everything the core/visualizer/build.py parser
  supports):
    - scalars (unquoted values such as role/confidence)
    - "quoted strings"
    - integers (e.g., 32, 4)
    - inline lists on one line: ["a", "b"]
    - inline dicts on one line: { k: v }
  Block style (indented nested mappings, block lists starting with `- `) is NOT
  recognized by the parser — never use it.

  Note: the `# ...` below are explanatory inline comments used only in this
  template file. The parser skips a line as a comment only when the whole line
  starts with `#`; an inline comment after a value is NOT skipped (the whole
  line is read as the value string). When saving a real card, always delete the
  `# ...` part and keep only the value.

  Also: write all filled-in content in the project's `language` (config.json).
-->
---
id: p01
name: "Seoyeon Kim"
role: primary                # primary | secondary | anti — default 5-set: primary 1, secondary 3, anti 1
archetype: "Time-strapped hands-on designer"
confidence: assumption       # assumption | partial | validated — per confidence-levels.md. Do not set by gut feeling
sources: []                  # if validated/partial, evidence interview paths: ["research/interview-01-mina.md", ...]
demographics: { age: 32, occupation: "Product designer", context: "5-person startup" }
goals: ["...", "...", "..."]           # 3-5 items, concrete "when / in what situation / doing what" (no single-adjective summaries)
frustrations: ["...", "...", "..."]    # 3-5 items, same principle. At least 1 must target the product/team itself
behaviors: ["...", "...", "..."]       # 3-5 items, same principle. At least 1 must be an avoidance/abandonment/workaround behavior
tech_savviness: 4            # integer 1-5. The 3 secondaries must differ by >= 2 points, etc. (persona-framework.md §2)
quote: "One first-person sentence"     # as if the persona is speaking. No marketing slogans
---

## Narrative

<!-- 3-5 sentences. Connect demographics/archetype with goals/frustrations to
     explain why this person has these needs and frustrations. If role: anti,
     center it on "why they do not / cannot use this product"
     (persona-framework.md §4). -->

## Needs detail

<!-- 3-4 bullets expanding goals/frustrations into more concrete situations. Not
     abstract desires but "when / where / trying to do what gets blocked." -->

## Decisions this persona would push back on

<!-- At least 3. Each item is "a product/feature decision they'd oppose + the
     concrete reason" (positivity-bias prevention, persona-framework.md §3). If
     role: anti, at least 1 must object to the product's core premise itself
     (persona-framework.md §4). -->
