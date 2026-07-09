---
name: research
description: Organize a product idea or interview notes into evidence-tagged research insights — run when the user describes an idea or pastes raw interview notes.
---

# research

Store the user's product-idea description or interview notes under
`personas/research/`, and generate/update `personas/research/insights.md`
following the procedure in `core/methodology/interview-analysis.md`.

## Language

Converse with the user in their language. Write all artifacts
(`insights.md`, stored notes) in `config.language` from `personas/config.json`.

## Instructions

### 0. Prerequisite check

If `personas/config.json` is missing, tell the user and stop immediately:

> Run `/persona-maker:init` first.

### 1. Classify input and store

Determine which of the following the user's input is. If ambiguous, don't guess
— ask the user.

- **(a) Product-idea description** — an explanation of "I want to build this,"
  not yet a real user interview.
  → Store at `personas/research/idea-brief.md`. If the file already exists,
  confirm with the user before updating it.

- **(b) Interview notes** — a real transcript/memo from a participant.
  → Store at `personas/research/interview-NN-<participant-alias>.md`.
  - `NN` is the next 2-digit number after existing `interview-*.md` files (start
    at `01` if none exist).
  - Do not store the participant's real name (privacy protection). If no alias
    was given, ask the user.
  - Store the raw text **as-is**, without summarizing or refining — processing
    happens only in step 2's insight extraction.

### 2. Insight extraction

Read `${CLAUDE_PLUGIN_ROOT}/core/methodology/interview-analysis.md` and follow
its defined procedure to create or update `personas/research/insights.md`. Key
rule summary (the original document wins if they diverge):

- Extract evidence sentences verbatim (or with minimal edits) from the original
  utterances. Do not fabricate content not in the transcript.
- Attach an `[I-NN]` tag to each evidence sentence (`NN` = that interview file's
  number).
- Always distinguish **"evidence"** (explicitly stated) from **"inference"**
  (synthesized judgment). Do not mix the labels. Attach the source `[I-NN]` list
  to inference items.
- **Idea only** (0 interviews): since no evidence exists, label every item in
  `insights.md` "inference (idea-based assumption)." State
  `available_confidence: assumption` at the top of the file.
- **With interviews**: count the distinct participants (by alias) across all
  `personas/research/interview-*.md`. If **fewer than 3**, state the following
  verbatim at the top of `insights.md` (no paraphrasing/shortening):

  > Insufficient sample — validated grade not allowed (partial is the ceiling).

  Also record the interview count (participant count and file count can differ —
  the same participant may have been interviewed multiple times, so keep both).

Recommended `insights.md` structure:

```markdown
# Research insights
<!-- available_confidence: assumption | partial | validated -->
<!-- participants: N, interviews: M -->
(insufficient-sample warning — if applicable)

## Needs
- [evidence] "..." [I-01]
- [inference] ... (from: [I-01], [I-02])

## Frustrations
- [evidence] "..." [I-02]
- [inference] ...

## Behaviors
- [evidence] "..." [I-01]
- [inference] ...
```

### 3. Direct-execution principle

This step (classify input, store, extract insights) is performed **directly** by
the main session. Do not dispatch a subagent — evidence/inference distinction
and sample-size judgment are orchestration/judgment work, a different division
of labor from the bulk generation delegated in the `generate` step.

### 4. Completion report

When done, summarize:

- Stored file paths (`idea-brief.md` or `interview-NN-*.md`, `insights.md`)
- Number of extracted insights (evidence/inference counts by needs/frustrations/behaviors)
- Current participant count and interview count, and the resulting maximum
  possible confidence grade (the ceiling among `assumption`/`partial`/`validated`)

Finally, point to the next step:

- If `personas/cards/` has no cards yet: "Run `/persona-maker:generate` to
  generate personas."
- If `personas/cards/` already has cards: "Run `/persona-maker:generate --update`
  to update existing personas."
