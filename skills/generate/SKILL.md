---
name: generate
description: Generate persona cards and journey maps from personas/research/insights.md. Also used with the --update flag to update existing personas against new interviews.
---

# generate

Generate persona cards (+ journey maps) from `personas/research/insights.md`.
Bulk text generation (writing card/journey bodies) is delegated to the
`persona-generator` subagent; judgment work (slot design, validation, grade
re-evaluation) is done directly by the main session.

## Language

Converse with the user in their language. Pass `config.language` to each
subagent so all generated artifacts are written in that language.

## Instructions

### 0. Prerequisite check

If `personas/config.json` is missing, tell the user and stop:

> Run `/persona-maker:init` first.

If `personas/research/insights.md` is missing, tell the user and stop:

> Run `/persona-maker:research` first.

### 1. Read config

Read `personas/config.json` for:

- `model` (default `haiku`) — use this value as the `model` parameter when
  dispatching subagents.
- `persona_count` (default 5)
- `language`

### 2. Slot design (done directly by the main session)

This is judgment work, so it is not delegated to a subagent.

1. Compose the set per `persona_count`: 1 `primary`, 1 `anti`, the rest
   `secondary`.
2. Read `${CLAUDE_PLUGIN_ROOT}/core/methodology/persona-framework.md` §2
   (diversity rules) and pre-assign a differentiation axis per slot so the
   secondary slots are distinct — at least 2 of `tech_savviness` (≥2-point gap),
   usage motivation, and usage context (`demographics.context`) must differ per
   slot.
3. Decide each slot's `confidence` grade from `insights.md`'s top
   `available_confidence` (and whether the insufficient-sample warning is
   present) plus
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md`. If 0
   interviews, everyone is `assumption`. If fewer than 3 participants, no slot
   exceeds `partial`.
4. For each slot, prepare `id` (`p01`, `p02`, …), `role`, differentiation axis,
   and `confidence` to pass to the subagent in the next step.

### 3. Parallel dispatch

Dispatch one `persona-generator` subagent **in parallel** per slot (using the
`model` value read from `config.json` in step 1). Include these 6 inputs in each
prompt.

1. Path to `personas/research/insights.md`
2. The slot definition (`id`, `role`, differentiation axis, `confidence`)
3. Template paths — `${CLAUDE_PLUGIN_ROOT}/core/templates/persona-card.md`, and
   (if not anti) `${CLAUDE_PLUGIN_ROOT}/core/templates/journey-map.md`
4. Methodology paths —
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/persona-framework.md`,
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/journey-mapping.md`,
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md`
5. config (`language`, etc.)
6. Output file paths — `personas/cards/persona-NN-<slug>.md`, and (if not anti)
   `personas/journeys/journey-pNN.md` (`NN` = the slot `id` number, `<slug>` = a
   romanized slug of the persona name)

### 4. Validation

When a subagent finishes, check each artifact.

- Does the card frontmatter contain all required fields (`id`/`name`/`role`/
  `archetype`/`confidence`/`sources`/`demographics`/`goals`/`frustrations`/
  `behaviors`/`tech_savviness`/`quote`)?
- Does the journey frontmatter have `persona_id`/`stages` (exactly 5)/`emotions`
  (5 integers)/`touchpoints`/`pain_points`?
- Do both files use only the YAML subset (scalars, `"quoted strings"`, integers,
  inline lists/dicts) with no block style mixed in?
- Are the journey `emotions` not all-positive (at least 1 is 0 or below)?
- Was no journey file created for a `role: anti` slot?

If a slot fails, state exactly what is wrong and **re-dispatch that slot once**.
If it fails again, do not auto-fix — report it to the user.

### 5. `--update` mode

If the user invoked `/persona-maker:generate --update`, or invoked without
`--update` but cards already exist in `personas/cards/`, do not regenerate
everything. Instead the main session does the following **directly** (grade
judgment is judgment work, not delegated to a subagent).

1. Compare all existing cards against the new insights in
   `personas/research/insights.md`.
2. Apply `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md` §2
   (promotion) and §3 (demotion).
   - Confirm which persona attribute each new `[evidence]` item actually
     corresponds to, and add only the confirmed ones to `sources` (no forced
     links).
   - Re-evaluate the grade by the number of linked interviews (0 = `assumption`,
     1–2 = `partial`, 3+ = `validated`). Keep the fewer-than-3-participants cap.
   - If a new interview contradicts an existing assumption, revise that
     attribute and leave a "Previous assumption: …" note in the body, then
     demote.
3. Modify **only the cards that need changes**; leave the rest untouched.

### 6. Completion report

When done, summarize:

- List of generated/updated files
- Grade distribution (`assumption N` / `partial N` / `validated N`)
- Any promotions/demotions in this run (which slot changed and why)

Finally, point to the next step:

> Run `/persona-maker:visualize` to build the visualization.
