# Contributing to persona-maker

Thanks for your interest! Issues and pull requests are welcome from everyone.

## Ground rules

- **Language:** the repository (code, docs, skills, methodology) is in **English**.
  Note the distinction: the plugin's *generated output* follows the user's
  language via `config.language`, but everything committed to this repo stays in
  English so contributors worldwide can read and review it.
- **Single source of truth:** the methodology under `core/methodology/` defines
  the persona/journey/confidence rules. The Claude plugin (`skills/`, `agents/`)
  and the Codex adapter (`codex-skill/`) only differ in how they dispatch models
  — they reference the same methodology. Change a rule in one place.
- Keep the visualization **self-contained**: `core/visualizer/template.html` must
  not reference any external URL, script, font, or image. `build.py` uses the
  Python standard library only (no third-party packages).

## Development setup

No install step for the plugin itself. For the tests and tooling:

```bash
# Python builder tests (pytest is the only dev dependency)
python -m pytest tests/ -v

# Template integrity check (needs Node)
node scripts/smoke_template.mjs

# Build a preview from the fixtures and serve it
python3 core/visualizer/build.py --personas-dir tests/fixtures/personas --output /tmp/preview.html
bash scripts/serve.sh tests/fixtures/personas
```

## Making changes

1. Fork and branch from `main` (`feat/…`, `fix/…`, `docs/…`).
2. If you touch `core/visualizer/build.py`, add or update a test in `tests/`.
   We follow TDD — write the failing test first.
3. If you touch `template.html`, run `node scripts/smoke_template.mjs` and open a
   build in the browser to confirm all four scenes render with zero console
   errors.
4. Keep commits focused; use [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`).
5. Open a PR using the template. Describe what changed and how you verified it.

## Good first areas

- **New visualization scenes** — the scene registry in `template.html` has a
  clean `{ enter, tick, onClick, exit }` interface.
- **Additional methodology checks** — e.g. more positivity-bias guards, or new
  diversity axes in `core/methodology/persona-framework.md`.
- **New runtime adapters** — the same `core/` can be driven by other agent tools;
  `codex-skill/SKILL.md` is a good reference for what an adapter needs.

## Reporting bugs & requesting features

Open an issue using the templates. For visualization bugs, please include your
browser, a screenshot, and any console errors.

By contributing, you agree that your contributions are licensed under the
project's [MIT License](LICENSE).
