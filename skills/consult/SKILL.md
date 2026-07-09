---
name: consult
description: Review a feature/design decision from the personas' perspective — run when the user asks "what would users think of this decision", "ask the personas", "how would this feature land", etc.
---

# consult

"Ask" the personas in `personas/cards/` about a specific feature/design decision
via simulation, recording accept/neutral/reject reactions and their rationale as
a consultation record. Per-persona reaction judgment (bulk judgment generation)
is delegated to a subagent; question refinement, synthesis, and confidence
disclosure are done directly by the main session.

## Language

Converse with the user in their language. Write the consultation record in
`config.language` from `personas/config.json`.

## Instructions

### 0. Prerequisite check

If `personas/config.json` is missing, tell the user and stop:

> Run `/persona-maker:init` first.

If there are no cards in `personas/cards/`, tell the user and stop:

> Run `/persona-maker:generate` first.

### 1. Receive the question

Refine the decision question the user posed. If it is ambiguous (options unclear
or abstract like "what do you think of this?"), don't guess — ask back to clarify
the options. Example:

> "Should we force sign-up during onboarding, or offer a guest mode?"

If the question is already concrete (a clear either/or or single-decision
statement), proceed without asking back.

### 2. Load cards

Read all of `personas/cards/*.md`. Do not summarize or read only a subset — the
consultation must draw on the full goals/frustrations/behaviors/"Decisions this
persona would push back on" of each card.

### 3. Dispatch subagent

Dispatch one subagent using the `model` (default `haiku`) from
`personas/config.json`. Include in the prompt:

- The decision question refined in step 1 (with options)
- The full card contents read in step 2 (all personas, frontmatter + body)
- Instructions:
  - For every persona (including `role: anti`), individually judge
    `accept`/`neutral`/`reject` and write a 1–3 sentence reason.
  - **The reason must actually be quoted from that card's
    `goals`/`frustrations`/`behaviors` or "## Decisions this persona would push
    back on."** Do not invent a reason absent from the card — if there is no
    citable basis in the card, report that fact (do not force a reason).
  - A `role: anti` persona's reaction must reflect its stance on the product's
    **core premise**, not a like/dislike of the individual feature (e.g., it
    views this decision through "I don't use this category of product at all").
  - Output format: for each persona `id`, return `verdict: accept|neutral|reject`
    + `reason: "..."` clearly separated (so the main session can parse it
    directly).

### 4. Synthesis (done directly by the main session)

When the subagent's results arrive, the main session does this **directly** (not
delegated):

1. Separate agreements (where reactions overlap) from conflicts (where they
   directly clash). Even if everyone reacts the same, check whether their reasons
   are the same too; if they differ, log it under conflicts.
2. Write the confidence disclosure per
   `${CLAUDE_PLUGIN_ROOT}/core/methodology/confidence-levels.md`:
   - If any cited persona is `assumption`-grade, include exactly: "This
     conclusion is based on N assumption-grade personas — do not use as a basis
     for important decisions before validating with real users." (replace N with
     the actual count)
   - If the cited personas are only `partial`/`validated`, state that to make the
     confidence level clear (e.g., "This conclusion is based on N personas graded
     partial or higher").

### 5. Save

Follow the structure of
`${CLAUDE_PLUGIN_ROOT}/core/templates/consultation.md` to write the record.

- Save path: `personas/consultations/YYYY-MM-DD-<topic-slug>.md`
  - `YYYY-MM-DD` is today's date. Get the exact value with the `date +%F` command
    (it may differ from the ambient date context, so check in the shell).
  - `<topic-slug>` is a lowercase kebab-case romanized slug summarizing the
    question (e.g., "force sign-up" → `signup-required`).
  - If a file with the same date and topic already exists, append a `-2` suffix
    (then `-3`, etc.).
- Frontmatter:
  - `date`: today's date (a `"YYYY-MM-DD"` quoted string)
  - `topic`: the one-line decision question refined in step 1
  - `reactions: { p01: accept, p02: neutral, ... }` — include **every**
    participating persona id. Use only the YAML subset (scalars, `"quoted
    strings"`, one-line inline dict). Never use block-style nesting or inline
    `# comments` — they get folded into the value and break parsing.
- Body sections: "Question", "Per-persona reactions" (one subheading per persona
  with cited card evidence), "Agreements and conflicts", "Confidence
  disclosure" — fill in following the `consultation.md` example format.

### 6. Wrap-up

When done, summarize:

- Reaction summary: `accept N / neutral N / reject N`
- The key conflict in 1–2 lines
- Path to the saved consultation record

Finally:

> Re-run `/persona-maker:visualize` to reflect this consultation in the Decision
> Log scene.
