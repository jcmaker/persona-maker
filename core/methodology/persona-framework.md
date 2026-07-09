# persona-framework.md — Persona Card Generation Rules

> **Audience:** This document is the instruction set that the persona-generator
> subagent (haiku/gpt-5-mini) follows verbatim when writing a single persona
> card. Read it as a checklist, not an essay. A card that breaks these rules is
> considered incomplete and must be rewritten.

## Why these rules exist

LLM-synthesized personas are known to suffer from **positivity bias** (skewed
toward more successful, agreeable people than reality) and **identity
flattening** (multiple personas collapsing into near-identical profiles). Both
failures are documented in the research literature. The rules below are
structural safeguards against them. The goal is not to write a "plausibly nice
person" but a "specific person who might actively oppose this decision."

---

## 1. Required card elements

Every card must contain all of the following fields. If any is empty, the card
is incomplete.

| Field | Rule |
|---|---|
| `name` | An invented name in the project's `language`. No real public figures. Give each card a distinct name. |
| `archetype` | A short role summary (e.g., "Time-strapped solo designer"). Capture an attitude/situation, not a list of job titles. |
| `goals` | 3–5 items. Write **concrete situations**, not abstract desires. |
| `frustrations` | 3–5 items. Same principle. |
| `behaviors` | 3–5 items. Same principle. |
| `quote` | One first-person sentence, as if the persona is speaking. No marketing slogans. |
| `demographics` | Use only the three keys `age`, `occupation`, `context`. Do not add other demographics (gender, location, income, education, family status, etc.) — excessive demographics reinforce stereotypes and are forbidden. |

**What "concrete situation" means:**
- Forbidden (abstract): "Values efficiency."
- Allowed (concrete): "Every Monday just before the sprint meeting, can't find the rationale for a decision and pings a colleague on Slack in a hurry."

Every item in goals/frustrations/behaviors must reach the "when / in what
situation / doing what" level of detail. Do not use single-adjective summaries
(fast, easy, reliable) alone.

---

## 2. Diversity rules (default 5-persona set)

The default headcount is 5, with a fixed composition:

- `primary` × 1
- `secondary` × 3
- `anti` × 1

### Differentiation among the 3 secondaries

The 3 secondaries must be distinct from one another. At least **2 of the
following 3 axes must differ** between them (identical values are a rule
violation):

1. **`tech_savviness`** (integer 1–5) — must differ by at least 2 points.
2. **Usage motivation** — the reason they use the product must differ (should
   surface in `goals`).
3. **Usage context** — `demographics.context` (when/where/in what situation
   they use it) must differ.

The slot-design step (main session) assigns these differentiation axes in
advance; the subagent reflects the assigned axis as-is. Do not change the axis
on your own.

### Additional diversity checks

- Not all 5 personas' `demographics.age` may fall within ±5 years of each other
  (i.e., all the same age bracket).
- Not all 5 personas' `demographics.occupation` may be the same job family.

---

## 3. Positivity-bias prevention

Do not homogenize synthetic personas into "successful, agreeable people."

- Not every persona may love the product, solve their own problems well, or
  agree with the team's decisions.
- The card body **must** include a `## Decisions this persona would push back on`
  section with **at least 3** items. Each item is "a product/feature decision
  this persona would have opposed + the concrete reason."
- At least 1 of the `frustrations` must be directed at the product/team itself
  (skepticism, distrust, indifference, or disappointment about a hypothetical
  feature). Not all frustrations may be external ("competitors are bad").
- Do not write only smooth success stories. Include at least 1 avoidance /
  abandonment / workaround behavior in `behaviors` (e.g., "Leaves the complex
  settings screen at defaults without reading to the end").

---

## 4. Anti-persona definition

`role: anti` is a user who does not use the product, or who will leave. The key
information is not their background but **why they don't use it**.

- Write `goals` as "what this person actually wants that this product does not
  solve."
- All `frustrations` must be "fundamental reasons for rejecting this
  product/category." Not minor UX friction but structural reasons (lack of
  trust, an existing alternative, value mismatch, budget/organizational
  constraints, etc.).
- The `## Decisions this persona would push back on` section must include at
  least 1 objection to "the core premise of the product itself."
- **Do not generate a journey map for an anti-persona** (see
  `core/methodology/journey-mapping.md`). A user who does not use the product
  has no usage journey.

---

## 5. Pre-save final checklist

Verify all of the following before saving a card.

- [ ] Are `goals`/`frustrations`/`behaviors` each 3–5 items, all concrete situations?
- [ ] Does `demographics` have only the `age`/`occupation`/`context` keys?
- [ ] Is `quote` first-person?
- [ ] Does `## Decisions this persona would push back on` have 3 or more items?
- [ ] Is at least 1 `frustrations` item directed at the product/team itself?
- [ ] Is at least 1 `behaviors` item an avoidance/abandonment/workaround behavior?
- [ ] (If not anti) Did you actually reflect the assigned differentiation axis (§2)?
- [ ] (If anti) Are all `frustrations` structural rejection reasons, and did you avoid creating a journey-map file?
