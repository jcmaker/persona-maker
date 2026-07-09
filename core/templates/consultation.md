<!--
  consultation.md — template for a persona consultation (consult) record

  The skeleton the main session copies and fills in when it simulates a specific
  decision against the persona cards and records the consultation result. The
  values are examples — replace everything with real content.

  Frontmatter YAML subset (everything the core/visualizer/build.py parser
  supports): scalars, "quoted strings", { k: v } inline dicts. Block style
  (indented nesting) is forbidden.

  Note: the `# ...` below are explanatory inline comments used only in this
  template. The parser skips a line only when the whole line starts with `#` —
  an inline comment after a value is folded into the value string and breaks
  parsing. When saving a real consultation, always delete the `# ...` part.

  Also: write all filled-in content in the project's `language` (config.json).
-->
---
date: "2026-07-09"
topic: "One-line decision topic"
reactions: { p01: accept, p02: neutral, p03: reject }   # accept | neutral | reject — include every persona id that participated
---

## Question

<!-- Describe the decision under consultation in 1-3 concrete sentences. If there
     are two or more options, state them explicitly. -->

## Per-persona reactions

<!-- One subheading per participating persona. State accept/neutral/reject, and
     the reason MUST be quoted from that card's goals/frustrations/behaviors or
     "Decisions this persona would push back on" — do not invent a reason absent
     from the card. If a role: anti persona participated, its reaction must
     reflect its stance on the product's core premise (persona-framework.md §4). -->

- **{name} ({id}, {role}) — accept/neutral/reject**: "{reason quoting card evidence}"

## Agreements and conflicts

<!-- Separate where personas agree (agreements) from where they directly clash
     (conflicts). Even if everyone reacts the same, check whether their reasons
     are the same too; if they differ, log it under conflicts. -->

## Confidence disclosure

<!-- Per confidence-levels.md. If any cited persona is assumption-grade, state
     "This conclusion is based on N assumption-grade personas" and add the
     warning not to use it as a basis for important decisions before validating
     with real users. If it consists only of partial/validated personas, state
     that too, to make the confidence level clear. -->
