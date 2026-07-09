---
name: persona-maker
description: Use when persona research, generation, visualization, or decision consultation is needed — distilling ideas/interviews into insights, creating persona cards/journey maps, showing a visualization, or asking how personas would react to a feature decision.
---

# persona-maker (Codex adapter)

A single-file Codex adapter consolidating the 5 Claude-plugin skills
(init/research/generate/visualize/consult, in the repo-root `skills/`) into one
document. Codex has no subcommand structure, so classify the user's request via
the "mode selection" table below, then follow that mode's section.

**Single source of truth (SSOT):** The methodology for research, personas,
journey maps, and confidence grading lives in `../core/methodology/*.md`; the
artifact formats live in `../core/templates/*.md`. This file provides only
procedure summaries and references — the goal is that it does not change even
when the methodology changes.

**Path resolution (important):** At the start of work, determine the absolute
path of the directory this SKILL.md is installed in and call it `<SKILL_DIR>`.
Resolve all `../core/...` paths in this document as
`<SKILL_DIR>/../core/...` and read/run them by **absolute path** (`codex-skill/`
and `core/` are sibling directories at the repo root, so no `${CLAUDE_PLUGIN_ROOT}`
variable is used). Do not resolve them relative to the user project's CWD — only
`personas/` artifact paths are relative to the user project CWD.

**Language:** Converse with the user in their language. Write all output
artifacts (cards, journey maps, consultations, insights) in `config.language`
from `personas/config.json`. This adapter's instructions are in English but the
output follows the user.

## Mode selection

Match the user's request against the table to choose a mode. If it spans two
modes or is ambiguous, **don't guess — ask the user which mode to run.**

| Example user request | Mode |
|---|---|
| "start", "set up", "initialize", first-time project prep | `init` |
| product-idea description, pasting raw interview notes/memos | `research` |
| "make personas", "generate cards", "update them", `--update` | `generate` |
| "show me", "visualize", "open in the browser" | `visualize` |
| "how would users feel about this", "ask the personas", checking a feature/design reaction | `consult` |

Once the mode is set, follow only that section. Each section follows the **same
gates, procedure, and rules** as the same-named Claude-plugin skill
(`../skills/<mode>/SKILL.md`), differing only in Codex-specific environment
details (default model, paths, subagent dispatch).

---

## init mode

Goal: prepare the `personas/` working structure and `personas/config.json`.

1. Create the following directories under the current CWD (leave them if they
   exist): `personas/research`, `personas/cards`, `personas/journeys`,
   `personas/consultations`.
2. Check whether `personas/config.json` already exists.
   - **If not**, create it with this content (this adapter's default model is
     `gpt-5-mini`, not the Claude adapter's `haiku`; set `language` to the user's
     language, `en` as fallback):
     ```json
     {
       "model": "gpt-5-mini",
       "persona_count": 5,
       "language": "en"
     }
     ```
   - **If it exists, never overwrite it.** Read it and show the current values.
3. Explain each config key:
   - `model`: the model delegated for persona generation / consultation judgment.
     Default `gpt-5-mini` (low-cost bulk generation); changeable to `gpt-5`, etc.
   - `persona_count`: total number of personas (3–10, default 5). The default 5
     is primary 1 + secondary 3 + anti-persona 1.
   - `language`: the language of the output artifacts (cards, journey maps,
     consultations, etc.).
4. On a settings-change request, tell the user to edit `personas/config.json`
   directly (effective next run).
5. Next step: "Enter an idea or interview notes and I'll organize them in
   research mode."

---

## research mode

Goal: store idea/interview input under `personas/research/` and generate/update
`personas/research/insights.md`. The full procedure is in
`../core/methodology/interview-analysis.md`.

### 0. Prerequisite check

If `personas/config.json` is missing, say "Run init mode first." and stop.

### 1. Classify input and store

- **(a) Product-idea description** → `personas/research/idea-brief.md`. If it
  exists, confirm before updating.
- **(b) Interview notes** → `personas/research/interview-NN-<alias>.md` (`NN` =
  next 2-digit number after existing `interview-*.md`, or `01`). Do not store
  real names (ask for an alias if none). Store raw text as-is — summarizing
  happens only in step 2.

If ambiguous, don't guess — ask the user.

### 2. Insight extraction

Read `../core/methodology/interview-analysis.md` and follow it exactly to
generate/update `personas/research/insights.md`. Key rules:

- Extract evidence sentences verbatim (or minimally edited) and tag each `[I-NN]`.
  Do not fabricate anything not in the transcript.
- Always distinguish **[evidence]** (explicit utterance) from **[inference]**
  (synthesized judgment); do not mix them. Attach the source `[I-NN]` list to
  inferences.
- 0 interviews → all items are "[inference] (idea-based assumption)"; state
  `available_confidence: assumption` at the top.
- Fewer than 3 distinct participants (by alias) → state at the top, verbatim:
  > Insufficient sample — validated grade not allowed (partial is the ceiling).

  Also record interview count and participant count (they can differ if the same
  participant was interviewed multiple times).

The recommended `insights.md` structure follows `interview-analysis.md` and the
Claude adapter's research skill example (Needs/Frustrations/Behaviors sections,
each item labeled `[evidence]`/`[inference]` + `[I-NN]` tag).

### 3. Direct-execution principle

This mode (classify input, store, extract insights) is performed by the main
session **directly**. Do not delegate to a subagent/spawn — evidence/inference
distinction and sample-size judgment are orchestration/judgment work, distinct
from the bulk generation delegated in generate mode.

### 4. Completion report

Summarize the stored file paths, the number of extracted insights
(evidence/inference by needs/frustrations/behaviors), the current
participant/interview counts, and the resulting maximum confidence grade. Then:
if no cards, "Run generate mode to create personas"; if cards exist, "Run
generate mode (--update) to update them."

---

## generate mode

Goal: generate persona cards (+ journey maps) from
`personas/research/insights.md`. Bulk body generation is delegated; slot design,
validation, and grade re-evaluation are done by the main session directly.

### 0. Prerequisite check

If `personas/config.json` is missing, say "Run init mode first." and stop. If
`personas/research/insights.md` is missing, say "Run research mode first." and
stop.

### 1. Read config

Read `model` (default `gpt-5-mini`), `persona_count` (default 5), and `language`
from `personas/config.json`.

### 2. Slot design (main session, directly)

Not delegated.

1. Compose per `persona_count`: 1 `primary`, 1 `anti`, the rest `secondary`.
2. Read `../core/methodology/persona-framework.md` §2 (diversity rules) and
   pre-assign a differentiation axis per slot so secondaries are distinct — at
   least 2 of `tech_savviness` (≥2-point gap), usage motivation, and usage
   context (`demographics.context`) must differ per slot.
3. Decide each slot's `confidence` from `insights.md`'s top
   `available_confidence` (and the insufficient-sample warning) plus
   `../core/methodology/confidence-levels.md`. 0 interviews → all `assumption`.
   Fewer than 3 participants → no slot exceeds `partial`.
4. Prepare each slot's `id` (`p01`, `p02`, …), `role`, differentiation axis, and
   `confidence` to pass on for delegation.

### 3. Delegation dispatch (Codex environment difference)

Delegate generation of one persona card (+ journey) per slot.

- **If Codex has a subagent/spawn mechanism**: delegate one per slot, setting the
  delegated call's model to `config.json`'s `model`. Dispatch in parallel if
  possible.
- **If no spawn mechanism exists**: generate slots sequentially in the same
  session, but **one persona at a time** (do not lump multiple slots into one
  pass) — to prevent slot cross-contamination (missing differentiation axes,
  misapplied grades).

Specify these 6 items per delegation (the full instruction text is in
`../agents/persona-generator.md` — it defines the required fields per card, the
YAML-subset constraint, and the positivity-bias checklist):

1. Path to `personas/research/insights.md`
2. The slot definition (`id`, `role`, differentiation axis, `confidence`)
3. Template paths — `../core/templates/persona-card.md`, and (if not anti)
   `../core/templates/journey-map.md`
4. Methodology paths — `../core/methodology/persona-framework.md`,
   `../core/methodology/journey-mapping.md`,
   `../core/methodology/confidence-levels.md`
5. config (`language`, etc.)
6. Output paths — `personas/cards/persona-NN-<slug>.md`, and (if not anti)
   `personas/journeys/journey-pNN.md`

Core rules to enforce during generation (full text in `persona-framework.md` and
`persona-generator.md`):

- Frontmatter uses only the YAML subset (scalars, `"quoted strings"`, integers,
  one-line inline lists/dicts). Never block-style nesting.
- Card required fields: `id`/`name`/`role`/`archetype`/`confidence`/`sources`/
  `demographics`/`goals`/`frustrations`/`behaviors`/`tech_savviness`/`quote`.
  Journey required fields: `persona_id`/`stages` (5)/`emotions` (5 integers)/
  `touchpoints`/`pain_points`.
- Positivity-bias prevention: `## Decisions this persona would push back on` ≥ 3
  items, ≥ 1 `frustrations` targeting the product/team, ≥ 1 `behaviors` being
  avoidance/abandonment/workaround, journey `emotions` not all-positive (≥ 1 is 0
  or below).
- `sources` cites only `[evidence]` items from insights.md.
- Write `confidence` as assigned (no arbitrary change).

### 4. Validation

Check delegated outputs: card/journey required fields present, YAML subset
respected, journey `emotions` includes a value ≤ 0, and no journey created for a
`role: anti` slot. For a failed slot, state exactly what is wrong and
**re-delegate that slot once**. On repeated failure, don't auto-fix — report to
the user.

### 5. `--update` mode

On `--update`, or when cards already exist in `personas/cards/` even without the
flag, do not regenerate everything. The main session does the following
**directly** (grade judgment is judgment work, not delegated):

1. Compare all existing cards with the new insights in `insights.md`.
2. Apply `../core/methodology/confidence-levels.md` §2 (promotion) / §3
   (demotion). Add only actually-corresponding new `[evidence]` to `sources` (no
   forced links); re-evaluate the grade by linked-interview count (0 assumption,
   1–2 partial, 3+ validated, keeping the fewer-than-3-participants cap). On
   contradiction, revise the attribute and leave a "Previous assumption: …" note,
   then demote.
3. Modify **only the cards that need changes**; leave the rest untouched.

### 6. Completion report

Summarize generated/updated files, the grade distribution (assumption/partial/
validated N each), and this run's promotions/demotions. Then: "Run visualize mode
to build the visualization."

---

## visualize mode

Goal: assemble `personas/cards/`, `personas/journeys/`, and
`personas/consultations/` into `personas/index.html` and open a local server.

### 0. Prerequisite check

If `personas/config.json` is missing, say "Run init mode first." and stop. If no
cards in `personas/cards/`, say "Run generate mode first." and stop.

### 1. Build

Run the command below. `<SKILL_DIR>` is the absolute path of this SKILL.md's
directory per the path-resolution rule at the top (use an absolute path so it
works from the user project CWD). Do not specify output/template paths — use
`build.py`'s defaults (output: `personas/index.html`, template: `template.html`
next to `build.py`).

```bash
python3 <SKILL_DIR>/../core/visualizer/build.py --personas-dir personas
```

- stdout prints the generated `index.html` path (one line).
- stderr may print 0+ warnings (broken frontmatter, missing fields, no
  directory). The command doesn't fail on warnings — judge success by the exit
  code. On nonzero exit, show the full stderr and stop.

### 2. Relay warnings

If stderr had output, summarize each warning as "which file / what's wrong / fix
that file's frontmatter and re-run." Warnings still produce `index.html` (only
the problem files are skipped), so continue to step 3.

### 3. Open the server

Run `bash <SKILL_DIR>/../scripts/serve.sh personas`. It reuses an existing server
in the 8765–8775 range if serving this project, otherwise starts a background
`python3 -m http.server` on a free port and prints the access URL on stdout. On
exit code 0, give the user the URL; on nonzero, show stderr and tell the user to
run `python3 -m http.server <port> --directory personas` manually, then stop.

### 4. Wrap-up

Give the access URL (`http://localhost:<port>/index.html`) and briefly introduce
the 4 scenes (Constellation, Needs Landscape, Journey Emotions, Decision Log).
Note that after adding interviews they can re-run research → generate (--update)
→ visualize to refresh, and point to consult mode for feature/design reactions.

---

## consult mode

Goal: "ask" the personas in `personas/cards/` about a feature/design decision via
simulation, recording accept/neutral/reject reactions and rationale. Per-persona
judgment is delegated; question refinement, synthesis, and confidence disclosure
are done by the main session directly.

### 0. Prerequisite check

If `personas/config.json` is missing, say "Run init mode first." and stop. If no
cards in `personas/cards/`, say "Run generate mode first." and stop.

### 1. Receive the question

Refine the decision question. If options are unclear or it's abstract ("what do
you think of this?"), ask back to clarify options (e.g., "Force sign-up during
onboarding, or offer a guest mode?"). If already concrete (a clear either/or or
single decision), proceed.

### 2. Load cards

Read all of `personas/cards/*.md`. Do not summarize or read only a subset — the
consultation must use each card's full goals/frustrations/behaviors/"Decisions
this persona would push back on."

### 3. Delegation dispatch (Codex environment difference)

Delegate judgment using `config.json`'s `model` (default `gpt-5-mini`).

- **If Codex has a subagent/spawn mechanism**: one delegated call with the model
  set, passing all cards + the refined question, returning everyone's reactions at
  once.
- **If no spawn mechanism exists**: judge sequentially in the same session, but
  **one persona at a time** (do not lump everyone into one pass) — to prevent
  cross-card evidence contamination.

Instructions to include in the delegation:

- The refined question (with options), and the full card contents from step 2
  (all personas, frontmatter + body).
- For every persona (including `role: anti`), individually judge
  `accept`/`neutral`/`reject` with a 1–3 sentence reason.
- **The reason must actually be quoted from that card's
  `goals`/`frustrations`/`behaviors` or "## Decisions this persona would push
  back on."** Do not invent a reason absent from the card — if none exists,
  report that fact.
- A `role: anti` persona's reaction must reflect its stance on the product's
  **core premise**, not a like/dislike of the individual feature.
- Output format: for each persona `id`, return `verdict: accept|neutral|reject` +
  `reason: "..."` clearly separated (so the main session can parse it).

### 4. Synthesis (main session, directly)

When results arrive, the main session does this **directly** (not delegated):

1. Separate agreements (overlapping reactions) from conflicts (direct clashes).
   Even if everyone reacts the same, check whether reasons match; if not, log a
   conflict.
2. Write the confidence disclosure per `../core/methodology/confidence-levels.md`:
   - If any cited persona is `assumption`-grade: "This conclusion is based on N
     assumption-grade personas — do not use as a basis for important decisions
     before validating with real users." (replace N with the actual count, use
     verbatim)
   - If only `partial`/`validated`: state that (e.g., "This conclusion is based on
     N personas graded partial or higher") to make the confidence level clear.

### 5. Save

Following `../core/templates/consultation.md`, write the record.

- Save path: `personas/consultations/YYYY-MM-DD-<topic-slug>.md`. Get the date
  with `date +%F` (check in the shell, as it may differ from the ambient date
  context). Slug = lowercase kebab-case romanization of the question (e.g., "force
  sign-up" → `signup-required`). If a same-date, same-topic file exists, append
  `-2`, `-3`, ….
- Frontmatter: `date` (`"YYYY-MM-DD"` quoted string), `topic` (the refined
  one-line question), `reactions: { p01: accept, p02: neutral, ... }` (include
  every participating persona id, YAML subset only — no block nesting, no inline
  `#` comments).
- Body sections: "Question", "Per-persona reactions" (one subheading per persona
  with cited card evidence), "Agreements and conflicts", "Confidence disclosure",
  filled per the `consultation.md` format.

### 6. Wrap-up

Summarize the reaction counts (`accept N / neutral N / reject N`), the key
conflict in 1–2 lines, and the saved record path. Then: "Re-run visualize mode to
reflect this consultation in the Decision Log scene."
