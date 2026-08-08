# deepl-cli — Agent Instructions

DeepL Translator CLI using Playwright browser automation (no API key required).
See [README.md](README.md) for usage and [pyproject.toml](pyproject.toml) for dependencies.

## Build & Test Commands

```bash
uv run pytest                    # run tests
uv run pytest --cov=deepl tests/ # run tests with coverage
uvx ty check --respect-ignore-files  # type check (ty, not mypy)
uv run ruff check .              # lint
uv run ruff format .             # format
uv run pymarkdown fix --list-files . # lint markdown
```

Or via mise task runner:

```bash
mise run pytest
mise run ty
mise run ruff
mise run pymarkdown
```

## Architecture

| File | Purpose |
|------|---------|
| `deepl/deepl.py` | Core `DeepLCLI` class — Playwright scraping logic |
| `deepl/main.py` | CLI entry point (argparse), registered as `deepl` script |
| `deepl/languages.py` | `FR_LANGS` / `TO_LANGS` sets of valid language codes |
| `deepl/__init__.py` | Public exports: `DeepLCLI`, `DeepLCLIError`, `DeepLCLIPageLoadError` |
| `tests/test_deepl.py` | pytest + pytest-asyncio tests |

## Key Conventions

- **Python 3.10+** required; use modern union syntax (`X | Y`) over `Optional`/`Union`
- **Line length**: 120 characters (ruff config)
- **Docstrings**: Google convention (`Args:`, `Returns:`, `Raises:`)
- **Formatter**: `ruff format` (double quotes, 4-space indent)
- **Linter**: `ruff` with `ALL` rules; see per-file ignores in `pyproject.toml`
- **Package manager**: `uv` — use `uv add` / `uv run`, never bare `pip`
- **Versioning**: dynamic via `uv-dynamic-versioning` (git tags) — do not set `version` manually

## Translation Limits & Behavior

- Max input: **1500 characters** (`DeepLCLI.max_length`)
- The language pair is set via the **URL fragment**
  (`…/translator#<fr>/<to>/`), not by clicking the dropdowns: DeepL covers the
  translator card with an anti-bot overlay, and the dropdowns only respond
  after the client-side app hydrates — clicking them was slow and flaky
- DeepL **streams** the output, so `deepl.py` polls until the text stops
  changing and the `[...]` pending marker is gone, and checks the `lang`
  attributes to confirm the requested pair was actually applied
- `auto` source detection does **not** work via URL path param (tests for it
  are `@pytest.mark.skip`); `auto` is not in `FR_LANGS`, so `DeepLCLI.__init__`
  currently rejects it
- Language updates: scrape the DeepL language dropdown and run the JS snippet in `deepl.py` docstring to regenerate `languages.py`

## Testing Notes

- Tests make **real network requests** to deepl.com via Playwright — no mocking
- Async tests use `@pytest.mark.asyncio` (pytest-asyncio)
- Timeout should be set high in tests (e.g. `100000` ms) to avoid flakiness
