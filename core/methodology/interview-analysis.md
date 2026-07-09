# interview-analysis.md — Interview → Insight Extraction Procedure

> **Audience:** This document is the procedure the `research` skill (performed
> directly by the main-session model) follows verbatim when organizing interview
> notes into `research/insights.md`. Mixing speculation with direct evidence
> collapses the entire confidence-grading system in `confidence-levels.md`. This
> document strictly defines "what counts as evidence."

## 1. Input format

Store interview notes at the following path.

```
research/interview-NN-<participant-alias>.md
```

- `NN` is a 2-digit sequence number (`01`, `02`, …).
- Use an alias instead of the participant's real name (privacy protection).
- The raw text **may be pasted as-is** — store the original notes in this file
  without summarizing or refining. Processing/cleanup happens separately in the
  §2 procedure; the original file itself is never touched.

## 2. Extraction procedure

Perform the following 3 steps in order.

### ① Extract evidence sentences

From the interview transcript, find and extract (verbatim, or with minimal
editing) utterances falling into these three categories.

- **Needs**: things the participant said they want or need
- **Frustrations**: things the participant pointed to as inconvenient/problematic
- **Behaviors**: concrete actions the participant said they actually do (real
  behavior, not aspirations)

Do not invent anything not in the transcript. What the participant did not say
is not evidence.

### ② Tag

Attach an `[I-NN]` tag to each extracted evidence sentence (`NN` matches the
sequence number of that interview file). Example:

> "Just before the meeting, I can't find the rationale for a decision so I ask a
> colleague on Slack." `[I-03]`

All evidence from the same interview uses the same `[I-NN]`. Do not number
sentences individually.

### ③ Map to persona attributes

Map the tagged evidence sentences to persona fields
(`goals`/`frustrations`/`behaviors`, etc.) and organize them in
`research/insights.md`. Here you must always distinguish two labels.

- **Evidence**: exactly what the participant said explicitly. Attach the
  `[I-NN]` tag.
- **Inference**: what the analyst judged by synthesizing multiple pieces of
  evidence (not said directly by the participant). Note which `[I-NN]` evidence
  the inference is based on.

Do not mix the two labels. Marking inference as evidence is the main cause of
positivity bias / over-interpretation. When writing persona cards in the
`generate` step, only link "evidence"-labeled items to `sources` — "inference"
items may be reflected in the card but are not citation targets.

## 3. Bias warning: insufficient sample

Every time you write/update `insights.md`, count the number of distinct
participants (by alias) across the whole project (`research/interview-*.md`).

**If there are fewer than 3 participants, state the following verbatim at the
top of `insights.md`:**

> Insufficient sample — validated grade not allowed (partial is the ceiling).

- This warning is a **project-wide cap** that applies regardless of any
  individual persona's `sources` count. A narrow respondent pool means a few
  responses risk being over-interpreted across many persona attributes, so even
  if a specific attribute technically meets the `partial` condition (1–2
  interviews) in `confidence-levels.md` §1, no persona may exceed `partial` to
  reach `validated` while total participants are fewer than 3.
- Once there are 3 or more participants, remove this warning text and apply the
  §1–§2 rules of `confidence-levels.md` normally from then on.

## 4. Pre-generation final checklist

- [ ] Are the interview notes stored as `research/interview-NN-<alias>.md`?
- [ ] Did the evidence sentences come from the original utterances (no fabrication/exaggeration)?
- [ ] Does every evidence sentence have an `[I-NN]` tag?
- [ ] Are "evidence" and "inference" clearly distinguished by label?
- [ ] If fewer than 3 participants, is the "Insufficient sample — validated grade not allowed (partial is the ceiling)" text in `insights.md`?
- [ ] Were `sources` links for the `generate` step made only from "evidence"-labeled items?
