<!--
  journey-map.md — template for generating one journey map

  The skeleton the persona-generator subagent copies and fills in when writing
  one persona's journey map. The values are examples — replace everything with
  real content. The detailed rules live in core/methodology/journey-mapping.md.

  Important: do NOT generate a journey map for a role: anti persona
  (journey-mapping.md §1, persona-framework.md §4). A user who does not use the
  product has no usage journey.

  Frontmatter YAML subset (everything the core/visualizer/build.py parser
  supports): scalars, "quoted strings", integers, [a, b] / ["a", "b"] inline
  lists, { k: v } inline dicts. Block style (indented nesting, `- ` block lists)
  is forbidden.

  Note: the `# ...` below are explanatory inline comments used only in this
  template. The parser skips a line only when the whole line starts with `#` —
  an inline comment after a value is folded into the value string and breaks
  parsing. When saving a real journey map, always delete the `# ...` part.

  Also: write all filled-in content in the project's `language` (config.json).
-->
---
persona_id: p01
stages: [awareness, consideration, decision, usage, advocacy]   # fixed 5, this order — no add/remove/reorder
emotions: [1, -1, 0, 2, 1]   # 5 integers, -2..+2, 1:1 with stages. Not all-positive — at least 1 is 0 or below
touchpoints: ["...", "..."]  # per-stage touchpoints (channel/screen/person), 5 in the same order as stages
pain_points: ["...", "..."]  # per-stage friction, fill all 5 stages — never leave "none"
---

## Stage-by-stage journey

<!-- journey-mapping.md §3: for each stage, fill in
     action/thought/emotion/touchpoint/pain point. 5 rows fixed, same order as
     stages. The emotion value must match the same index of the frontmatter
     emotions array. Every stage must have a pain point, and the emotion curve
     must not be all-positive across the 5 stages (journey-mapping.md §4). -->

| Stage | Action | Thought | Emotion | Touchpoint | Pain point |
| --- | --- | --- | --- | --- | --- |
| awareness | ... | ... | ... | ... | ... |
| consideration | ... | ... | ... | ... | ... |
| decision | ... | ... | ... | ... | ... |
| usage | ... | ... | ... | ... | ... |
| advocacy | ... | ... | ... | ... | ... |

## Summary

<!-- Describe the emotion curve in 2-4 sentences. If there's a dip-then-recovery
     or other texture, point out at which stage it dips and why. -->
