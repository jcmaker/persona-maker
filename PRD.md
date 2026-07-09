# persona-maker PRD

> **To AI agents:** This document is your implementation instruction. Where it is
> unclear, do not guess — ask the user. When a decision changes during
> implementation, update this document so it remains the source of truth (living
> document). Items marked `(assumption)` were not confirmed by the user — verify
> them before relying on them.
>
> Detailed design: `docs/superpowers/specs/2026-07-09-persona-maker-design.md`.
> Task-level implementation plan: `docs/superpowers/plans/2026-07-09-persona-maker.md`.

## 1. Overview

Designers, developers, and PMs tend to lean on their own taste and bias when
making product decisions, which leads to rework and user churn. persona-maker
generates persona cards and journey maps following research best practices and
lets you continually ask "how would each persona receive this decision?", giving
a **decision anchor grounded strictly in the user's perspective**. It is a Claude
Code plugin (+ Codex adapter). Its differentiator is a built-in **3-tier
confidence system** (assumption/partial/validated) that defends against the known
pitfalls of AI-synthesized personas (positivity bias, identity flattening).

## 2. Target Users & JTBD

- **Who:** designers, developers, and PMs at early-stage startups (including solo
  founders).
- **Situation:** before starting product development, or at a feature-decision
  moment, with no formal UX research team — holding only an idea memo or a few
  interview notes.
- **Job to be done:** decide from user-perspective evidence instead of subjective
  bias, and know transparently how strong that evidence is (assumption vs.
  validated).

## 3. Core Features (Scope)

1. **`/persona-maker:init`** — creates the `personas/` structure and `config.json`
   (model, count, language) in the user's project. Never overwrites an existing
   config; shows current settings instead.
2. **`/persona-maker:research`** — takes an idea description or interview notes,
   stores them under `research/`, and produces `research/insights.md` with needs,
   behaviors, and pain-point candidates plus evidence tags. The input source
   determines the confidence ceiling.
3. **`/persona-maker:generate`** — generates persona cards (default 5 = primary 1
   + secondary 3 + anti 1) and journey maps (excluding anti) from the insights.
   Dispatches one low-cost subagent per persona in parallel (Claude: `haiku`;
   Codex: `gpt-5-mini`; changeable via config). `--update` mode reflects new
   interviews by updating only the grades/attributes of existing cards.
4. **`/persona-maker:visualize`** — parses the artifact markdown into a
   zero-dependency, self-contained `index.html` (Canvas 2D particles, 4 scenes:
   Constellation / Needs Landscape / Journey Emotions / Decision Log) and opens it
   with a local server. Confidence grade is expressed as visual language (dashed
   faint vs. solid bright particles).
5. **`/persona-maker:consult`** — for a decision question, generates each persona's
   accept/neutral/reject reaction and rationale, and records agreements, conflicts,
   and a confidence disclosure under `consultations/`. Results feed the Decision
   Log scene.

## 4. Non-Goals

- No cloud hosting, team sharing, or real-time collaboration this version (local
  files + localhost only).
- No automated recruiting/recording/transcription of real user interviews (the
  user enters notes directly).
- No statistical clustering (k-means, etc.) of quantitative survey data this
  version.
- No build-tool-based web app (React/Vite, etc.) — single-HTML principle `[DO NOT CHANGE]`.
- No persona profile-image generation. (assumption)
- No output-quality guarantee for languages other than the user's chosen
  `config.language`. (assumption)

## 5. Technical Constraints & Prior Decisions

- Shared core (`core/`) + platform adapters (`skills/`+`agents/`, `codex-skill/`)
  so a methodology change reflects in both — `[DO NOT CHANGE]`.
- The visualization is a self-contained single HTML; no external CDN/font/package
  references — `[DO NOT CHANGE]`.
- `build.py` uses the Python standard library only (pytest is dev-only) — `[DO NOT CHANGE]`.
- Frontmatter uses only the YAML subset the build.py parser handles (scalars,
  inline lists, inline dicts, integers) — stated in the generator instructions.
- Persona generation model: Claude adapter defaults `haiku`, Codex adapter
  defaults `gpt-5-mini`, changeable anytime in `personas/config.json` — `[DO NOT CHANGE]`.
- Orchestration (insight summary, consultation synthesis) runs on the main-session
  model; only bulk generation goes to the low-cost model — the cost division-of-labor.
- Data handled: persona cards (id, name, role, archetype, confidence, sources,
  demographics, goals, frustrations, behaviors, tech_savviness, quote, narrative,
  push-back decisions), journey maps (persona_id, 5 stages, emotion scores -2..+2,
  touchpoints, pain points), consultation records (date, topic, per-persona
  reactions), config (model, persona_count, language).
- Privacy: interview notes are stored only on the user's machine, never
  transmitted externally. Participants are recorded by alias only. (assumption)

## 6. Phased Requirements

### Phase 1: Shared core + visualization

**Goal:** methodology, templates, builder, and visualization are complete, so you
can open the particle visualization from fixture data alone.

**Requirements:**
1. `core/methodology/` (persona-framework, journey-mapping, confidence-levels,
   interview-analysis) — diversity rules, positivity-bias prevention, grade
   promotion/demotion.
2. `core/templates/` (persona-card, journey-map, consultation) — frontmatter
   schema + body skeletons.
3. `core/visualizer/build.py`: frontmatter parser (YAML subset) → artifact
   collection/validation (skip broken files with warnings, default missing
   fields) → JSON injection at the `/*__PERSONA_DATA__*/` marker → CLI.
4. `core/visualizer/template.html`: tabs, card panel, particle base + the 4
   scenes; data-less scenes show guidance text.
5. pytest tests for parser/collection/HTML assembly (fixtures: 2 valid cards, 1
   missing-field card, 1 broken card, 1 journey, 1 consultation).

**Acceptance criteria:**
- [ ] `python -m pytest tests/ -v` passes fully.
- [ ] `python3 core/visualizer/build.py --personas-dir tests/fixtures/personas --output /tmp/index.html` exits 0, with a broken-card warning on stderr.
- [ ] Opening the built index.html switches all 4 tabs with zero console errors.
- [ ] assumption personas render dashed/low-opacity; validated render solid/high-opacity.
- [ ] index.html references zero external URLs.

### Phase 2: Claude Code plugin (needs Phase 1 core)

**Goal:** the full init→research→generate→visualize→consult workflow runs in
Claude Code via 5 commands.

**Requirements:**
1. `.claude-plugin/plugin.json` manifest (+ marketplace.json) and `commands/`.
2. Five skills; research/generate/visualize/consult stop with an init prompt when
   config.json is absent.
3. `agents/persona-generator.md` (model haiku, tools Read/Write) — one parallel
   dispatch per slot, one re-dispatch on frontmatter-validation failure.
4. `generate --update`: keep existing cards, update only grades/attributes,
   rewrite only changed cards.
5. consult confidence disclosure: state when assumption-grade cards are in the basis.

**Acceptance criteria:**
- [ ] init in an empty dir creates `personas/{research,cards,journeys,consultations}` and config.json.
- [ ] research→generate from an idea paragraph produces 5 cards, all `confidence: assumption`.
- [ ] the anti-persona has no journey file.
- [ ] after adding 3 interviews, `generate --update` promotes at least one card's confidence and cites the interviews in sources.
- [ ] visualize opens `http://localhost:<port>/index.html`, trying 8766–8775 on port conflict.
- [ ] consult creates a dated-topic file with every persona's accept/neutral/reject recorded.

### Phase 3: Codex adapter + docs (needs Phase 2 skill flow)

**Goal:** the same workflow runs in Codex with a `gpt-5-mini` default, and the
README explains install and usage.

**Requirements:**
1. `codex-skill/SKILL.md` — 5 modes in one file, config default model gpt-5-mini.
2. `README.md` — install, workflow, config options, confidence grades.
3. Two E2E walkthroughs (idea-only / 3-interview) verified against the plan's Task 14.

**Acceptance criteria:**
- [ ] codex-skill/SKILL.md states all 5 mode branches and the gpt-5-mini default.
- [ ] following the README examples reproduces the Phase 2 workflow.
- [ ] `python -m pytest tests/ -v` still passes (no regression).

## 7. Success Metrics

- From idea input to visualization (init→visualize), completion within 15 minutes excluding user input. (assumption)
- When generating 5 personas, all bulk text generation runs on the low-cost model (haiku/gpt-5-mini) — zero generation calls on the main-session model.
- Every persona card carries a confidence grade and (for validated) source citations — zero build.py warnings.
