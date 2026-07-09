---
name: visualize
description: Build the persona artifacts into a particle-visualization HTML and open it in a local server — run when the user asks to "visualize", "show the personas", etc.
---

# visualize

Assemble `personas/cards/`, `personas/journeys/`, and `personas/consultations/`
into a particle-based visualization HTML (`personas/index.html`) and open it in a
local static server so the user can view it in a browser.

## Language

Converse with the user in their language. The visualization renders whatever
language the artifacts were written in (`config.language`).

## Instructions

### 0. Prerequisite check

If `personas/config.json` is missing, tell the user and stop:

> Run `/persona-maker:init` first.

If there are no cards in `personas/cards/`, tell the user and stop:

> Run `/persona-maker:generate` first.

### 1. Build

Run the following command as-is. Do not specify output/template paths — use
`build.py`'s defaults (output: `personas/index.html`, template: `template.html`
next to `build.py`).

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/core/visualizer/build.py --personas-dir personas
```

- stdout prints the path of the generated `index.html` (one line).
- stderr may print 0 or more warnings (broken frontmatter, missing fields, no
  directory, etc.). The command itself does not fail on warnings (check the exit
  code for success). If the exit code is nonzero, show the full stderr to the
  user and stop.

### 2. Relay warnings

If stderr printed one or more lines, summarize each warning to the user in this
form:

- Which file is the problem (the filename/path in the warning message)
- What is wrong (frontmatter parse failure / missing required field / no
  directory, etc.)
- Fix: edit the frontmatter of that card (or journey/consultation) file directly
  and re-run `/persona-maker:visualize`.

Warnings still produce `index.html` (skipping only the problem files and
assembling the rest), so continue to step 3.

### 3. Open the server

Run the helper script below. It reuses an already-serving server in the
8765–8775 range if one exists, otherwise starts `python3 -m http.server` on a
free port in the background and returns the access URL on stdout:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/serve.sh personas
```

- On exit code 0, give the user the URL from stdout
  (`http://localhost:<port>/index.html`) and go to step 4.
- On nonzero exit code, show the stderr message. All ports are in use, so tell
  the user to run `python3 -m http.server <port> --directory personas` directly
  and stop.

### 4. Wrap-up

Once the server is open, tell the user:

- Access URL: `http://localhost:<port>/index.html`
- A brief intro to the 4 scenes:
  - **Constellation** — an overview of all personas as particles
  - **Needs Landscape** — each persona's needs/frustrations spread across a space
  - **Journey Emotions** — the per-stage emotion curve from journey maps
  - **Decision Log** — accumulated `/persona-maker:consult` records
- "When you add interviews, re-run `/persona-maker:research` →
  `/persona-maker:generate --update` → `/persona-maker:visualize` to refresh the
  visualization."
- "To preview how personas would react to a specific feature/design decision,
  run `/persona-maker:consult`."
