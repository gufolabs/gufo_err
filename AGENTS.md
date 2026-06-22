# Gufo Err - Agent Guidelines

## Project overview

Gufo Err is a Python error handling framework providing structured exception processing, fingerprinting, and human-readable error reporting. It supports Python 3.9-3.14 (current version 0.6.0).

Package name: `gufo_err`, importable as `from gufo.err import ...`.

## Code style

- Line length: 79 chars
- Docstring format: Google style
- Quotes: double quotes everywhere
- No f-string shorthand for empty dicts/lists (keep readability)
- Copyright headers: always preserve existing format block on the first lines of every edited file
- Comments: use `# noqa: RULE` comments sparingly; never add new ones without checking the file's existing ignores in pyproject.toml

## Linting and typing

Run all three checks before considering any PR ready:

1. Formatting: `ruff format examples/ src/ tests/`
2. ruff check: `ruff check -q examples/ src/ tests/`
3. Typing: `mypy --strict src/`

Install dev deps first: `pip install -e ".[lint,test,extras]"`

Ruff ignores in this project (defined in pyproject.toml):
- D203, D212, D107, A002, A003, PLR0911, PLR0913, PLC0415 (global)
- F401 and E402 in __init__.py files
- ANN*, D1*, S1*, S307, S603, PLR2004, PT011 in tests

## Testing

Run with: `pytest -v tests/`

For coverage: `pytest -v --cov --cov-branch --cov-report=xml tests/`

Tests are in `tests/`. Test files use pytest-benchmark and pytest-cov.

## Project structure (src layout)

```
src/gufo/err/
  __init__.py          # Public API exports: Err, err, ErrorInfo, BaseMiddleware, etc.
  err.py               # Core: Err singleton class and error processing pipeline
  types.py             # Dataclasses: Anchor, CodePosition, SourceInfo, FrameInfo, ErrorInfo, ExceptionStub
  frame.py             # Stack frame extraction from Python tracebacks
  compressor.py        # GZip/BZ2/XZ compression for error info files
  codec.py             # JSON serialization/deserialization for ErrorInfo
  cli.py               # 'err' command-line tool (list/view/clear/version)
  logger.py            # logging.getLogger('gufo.err') singleton
  abc/
    middleware.py      # BaseMiddleware abstract interface
    formatter.py       # BaseFormatter abstract interface
    failfast.py        # BaseFailFast abstract interface
  middleware/
    traceback.py       # TracebackMiddleware: dumps formatted traceback to logger
    errorinfo.py       # ErrorInfoMiddleware: writes error info to JSON files
    sentry.py          # SentryMiddleware: sends errors to Sentry (optional extra)
  formatter/
    terse.py           # TerseFormatter: condensed output with caret highlights
    extend.py          # ExtendFormatter: extended output with locals
    loader.py          # Formatter factory: get_formatter(name) -> BaseFormatter
  failfast/
    types.py           # TypesFailFast: trigger on specific exception types
    typematch.py       # TypeMatchFailFast: type + optional message substring matching, chainable add_match()
    always.py          # AlwaysFailFast: unconditional fail-fast (os._exit)
    never.py           # NeverFailFast: always allow processing to continue
```

## Core API usage patterns

The main entry point is the singleton `err`:

```python
from gufo.err import err

err.setup(
    name="my_service",
    version="1.0.0",
    catch_all=True,              # Install sys.excepthook globally
    format="terse",              # terse or extend (or None)
    middleware=[...],            # custom middlewares in addition to defaults
    error_info_path="/var/err",  # write errors to JSON files
    fail_fast=[TypesFailFast([ValueError])],  # optional fail-fast rules
)

# Later, in exception handlers:
try:
    do_something()
except Exception:
    err.process()  # collects and dispatches the current exception
```

When called twice, `err.setup()` raises `RuntimeError`. The singleton is not re-entrant.

## Key constraints to preserve

1. `Err` is a singleton — do not instantiate outside of setup(). Always use `from gufo.err import err`.
2. `err.setup()` must only be called once per process. Detect duplicates via the `__initialized` flag.
3. The fail-fast chain uses `os._exit()`, NOT `sys.exit()`. Adding print/log statements in __must_die__ is intentional (logger before exit).
4. ErrorInfo files are written with `open(path, "xb")` (exclusive create) to prevent duplicates; FileExistsError means the error was already recorded.
5. The fingerprint algorithm uses SHA-1 default, produces UUID v5 from 16 bytes of hash digest. Different hash function names are passed to hashlib directly — validate against `hashlib.algorithms_available`.
6. Fingerprint generation uses `iter_fingerprint_parts()` which can be overridden in subclasses for custom hashing logic. When modifying fingerprinting, check this method too.
7. System exceptions (`SystemExit`, `KeyboardInterrupt`) are always re-raised through the original hook — never processed by gufo.err.

## CLI tool

The `err` command is installed as an entry point (`gufo_err -> err`). Subcommands:

- `err version` -- prints package version
- `err list <dir>` -- lists recorded errors (fingerprint, exception, service, time, place)
- `err view <dir> <expression> [-f terse|extend]` -- shows details for a fingerprint
- `err clear <dir> <expression>` -- removes error info files matching expressions

Fingerprint expressions support UUID strings, `all`, and `*`. Directory path via `-p/--prefix` or `GUFO_ERR_PREFIX` env var. Exit codes: 0=OK, 1=path not exists, 2=not accessible, 3=cannot read, 4=invalid args, 5=syntax error.

## Adding features - what to touch

Adding a new formatter: create a class in `src/gufo/err/formatter/`, implement `iter_format()`, register it in the `loader.py` factory.

Adding a new failfast strategy: create a class in `src/gufo/err/failfast/`, extend `BaseFailFast`, implement `must_die()`.

Adding a new middleware: add to `src/gufo/err/middleware/`, extend `BaseMiddleware`, implement `process()`. Optionally make it an extra in pyproject.toml if it has external deps.

## Documentation

The project uses MkDocs Material with mkdocstrings for auto-generated API Reference docs.

### Build

```bash
pip install -e ".[docs]"
mkdocs build        # static output to site/
mkdocs serve        # dev server on localhost:8000
```

### Reference pages are auto-generated -- do not write manually

API Reference lives under `docs/reference/` but is populated by
`docs/gen_doc_stubs.py` via mkdocs-gen-files. Do NOT create or edit files
in `docs/reference/` — they will be overwritten on next build. If the output
is wrong, fix the source docstrings in `src/`.

The stub generator iterates every `.py` file under `src/`, creates page
`docs/reference/<relative_path>.md` with a `::: module.identifier` marker,
and builds a literate-nav SUMMARY.md. `__init__.py` maps to `index.md`.

### Docs tree layout

```
docs/
├── index.md             # MkDocs home (hero template)
├── installation.md      # Installation / upgrade / uninstall
├── faq.md               # FAQ
├── reference/           # Auto-generated by gen_doc_stubs.py — do not touch
├── examples/            # Hand-written example guides
│   ├── global.md        # Global exception hook (terse)
│   ├── globalextend.md  # Global exception hook (extended with locals)
│   ├── process.md       # Explicit err.process() in try/except
│   └── failfast.md      # Custom fail-fast handler
├── man/                 # Man page documentation
│   ├── err.md           # CLI "err" tool manual
│   └── index.md
└── dev/                 # Developer docs
    ├── index.md         # Dev section index
    ├── codebase.md      # Project structure overview
    ├── testing.md       # Build, test, lint, coverage commands
    ├── codequality.md   # Code quality standards
    ├── environment.md   # Dev container setup
    └── standards.md     # Standards (PEP8, PEP561)
```

### CLI tool exit codes (from AGENTS.md → man page sync)

Keep `docs/man/err.md` in sync with AGENTS.md:

- Exit code 0 = success
- Exit code 1 = path not exists
- Exit code 2 = not accessible
- Exit code 3 = cannot read
- Exit code 4 = invalid args
- Exit code 5 = syntax error

The `man/err.md` file fills the "Exit Status" section explicitly — keep it up to date.

### Documentation style notes

- Use British English consistently.
- Avoid marketing/promotional text in technical docs; reserve it for README/docs/index only.
- Example output in man pages uses hardcoded paths from tests (`/workspaces/gufo_err/...`). These are acceptable as placeholders but note they may confuse users reading the manual as live documentation.
- All code snippets follow `ruff` formatting: 79-char line length, double quotes.

## CI pipeline

The project runs GitHub Actions (ubuntu-24.04, Python 3.14 for linting, matrix of 3.9-3.14 for tests). Lint job must pass before test job. Publish triggers on git tags. Codecov integration enabled.

Workflow files live in `.github/workflows/` -- py-tests.yml is the critical one.

## Notable dependencies

- Core: stdlib only (hashlib, logging, uuid, dataclasses, typing)
- Optional extras: `sentry_sdk >= 2.8.0, < 3.0`, `ipython==9.6.0`
- Dev deps: ruff 0.15.x, mypy 2.1.0 (strict mode), pytest 8.4.x, coverage

## Common pitfalls

- modifiying ErrorInfo fields directly -- the codec expects exact dataclass structure during serialization; changing field names breaks cross-version compatibility
- removing `__all__` exports in __init__.py -- the project explicitly whitelists public API
- using `except Exception` in tests without PT011 suppression -- ruff requires match parameter for specificity
- forgetting to update `__all__` when adding new public exports
