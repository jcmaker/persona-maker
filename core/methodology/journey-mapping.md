# journey-mapping.md — Journey Map Generation Rules

> **Audience:** This document is the instruction set the persona-generator
> subagent follows verbatim when generating a single journey map. A journey map
> records what one persona experiences across 5 stages, from the moment they
> become aware of the product to the moment they advocate for (recommend) it.

## 1. Scope

- Generate a journey map only for `role: primary` or `role: secondary` personas.
- **Do not generate a journey map for a `role: anti` persona.** An anti-persona
  does not use the product, so a usage journey does not exist (see
  `persona-framework.md` §4). If the generating skill accidentally created a
  journey file for an anti-persona, delete it.

## 2. Fixed 5 stages

The `stages` field always uses the following 5 values **in this exact order**.
No adding, removing, or reordering.

1. `awareness` — becoming aware of the problem or first learning the product exists
2. `consideration` — comparing alternatives and evaluating
3. `decision` — actually deciding to use / not use it
4. `usage` — the experience during real use
5. `advocacy` — continuing, recommending, or churning

## 3. Per-stage recording items

Fill the following 5 columns in the body table for each stage.

| Item | Description |
|---|---|
| Action | What the persona actually does at this stage (observable behavior) |
| Thought | What runs through their mind at that moment (inner monologue, first person OK) |
| Emotion score | Integer -2 to +2. Must match the corresponding index of the `emotions` array. |
| Touchpoint | The channel/screen/person encountered at this stage (e.g., landing page, colleague referral, checkout screen) |
| Pain point | The friction at this stage. Always find one for every stage — do not leave it blank as "none." A stage with zero friction is unrealistic. |

## 4. Emotion score rules

- `emotions` is an array of 5 integers, corresponding 1:1 with `stages` in order
  (index 0 = awareness … 4 = advocacy).
- Each value must be one of `-2, -1, 0, 1, 2`.
- **All 5 stages being positive (+1 or +2) is forbidden.** That is unrealistic
  optimism and a hallmark symptom of positivity bias.
- **At least one stage must be 0 or below (0, -1, -2).** Scan the array before
  saving to confirm this. If violated, rewrite the journey map.
- A monotonically increasing curve (only ever improving) is discouraged. Real
  user experience often dips temporarily in the `usage` stage due to learning
  curves and errors, then recovers. Give the curve some texture.

## 5. Pre-save final checklist

- [ ] Is the target persona not an `anti`?
- [ ] Is `stages` exactly 5 items, in the §2 order?
- [ ] Is `emotions` 5 integers, indexed 1:1 with `stages`?
- [ ] Is `emotions` not all-positive (at least 1 is 0 or below)?
- [ ] Does every one of the 5 stages have a pain point?
- [ ] Do all emotion scores stay within the -2 to +2 range?
