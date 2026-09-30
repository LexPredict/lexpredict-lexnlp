# Working on LexNLP

LexNLP is a Python library in `lexnlp/`. Dependencies and packaging are defined
by `pyproject.toml` and `uv.lock`; supported Python versions are 3.10–3.13,
with 3.12 used for development and documentation. CI runs in `.github/workflows/`.

## Setup

Run from the repository root:

```bash
uv sync --frozen --python 3.12 --extra dev --extra test
uv pip check --python .venv/bin/python
.venv/bin/python scripts/bootstrap_assets.py --nltk --contract-model --contract-type-model
```

Use `uv lock` after intentional dependency changes; do not hand-edit the lock
or recreate the retired Pipenv/Travis/requirements snapshots.

NLTK data and pipeline classifiers are external resources. Bootstrap verifies
pinned sources before use. Bundled sklearn models are package data and need no
download. Stanford is optional and requires Java: bootstrap with `--stanford`
and explicitly configure a trusted `NLTK_DATA` location for custom paths.
Never disable TLS, checksums, or runtime path protection, or commit downloaded
third-party asset trees.

## Changes and validation

Preserve public signatures, return shapes, source offsets, and extraction
quality. Add focused regressions for behavior changes and use existing helpers.

Run targeted tests while iterating, then the required checks:

```bash
.venv/bin/ruff check lexnlp scripts ci --select E4,E7,E9,F
.venv/bin/python ci/skip_audit.py
.venv/bin/python scripts/reexport_bundled_sklearn_models.py --check-current
.venv/bin/python -m pytest lexnlp scripts/tests
uv build
.venv/bin/python ci/check_dist_contents.py
```

Install wheel and sdist independently outside the checkout when changing
packaging; verify runtime resource parity. Validate the supported Python matrix
and minimum dependencies when changing dependency or model compatibility.

Build documentation with warnings fatal:

```bash
uv sync --frozen --python 3.12 --extra dev --extra test --extra docs
.venv/bin/sphinx-build -W --keep-going -b html documentation/docs/source documentation/docs/build/html
```

After installing verified Stanford assets and Java, run its optional integration
suite with `LEXNLP_USE_STANFORD=true`:

```bash
.venv/bin/python -m pytest lexnlp/nlp/en/tests/test_stanford.py lexnlp/extract/en/entities/tests/test_stanford_ner.py
```

Do not add, remove, or alter skips/xfails, fixtures, or metric baselines to hide
failures. Necessary markers require an inline
`skip-audit: issue=<link-or-id> expires=YYYY-MM-DD` annotation; the allowlist is
reserved for cases that cannot be annotated.

## Models and dependency audit

Pickle/joblib artifacts are executable data: use only verified trusted sources.
Serialize models with the exact producer stack in
`constraints/model-artifact-abi.txt`, including Python 3.12.13. All artifacts
must direct-load and pass fixed-fixture quality gates under minimum and latest
dependencies, with every permitted regression set to `0.0`. Do not replace
baseline metrics to make weaker models pass. The gate commands are documented
in `MIGRATION_RUNBOOK.md` and CI.

Retain raw dependency-audit findings. Applicability dispositions must pass
`ci/check_dependency_audit.py` against `ci/dependency_audit_exceptions.json`.
Dependency/source/advisory changes or expiry require review; a disposition is
not remediation of the vulnerable dependency and does not cover downstream
exposure of affected APIs.
