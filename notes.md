# LexNLP Dependency Modernization Notes

Date: February 14, 2026
Repo: `/Users/jackeames/Downloads/LexNLP`

## Objective

Modernize dependency and test tooling so LexNLP is reproducible with `uv`, Python 3.11, and a strict no-test-bypass policy while keeping behavior stable.

## What was required

1. Move install/runtime metadata to `pyproject.toml` and lock with `uv.lock`.
2. Align dependency versions to combinations that build and run on modern Python.
3. Make optional runtime assets deterministic (NLTK, contract model, Stanford, optional Tika).
4. Enforce test integrity (no new skip/xfail bypasses).
5. Verify packaging artifacts are clean and installable.

## Issues encountered and how they were fixed

### 1) Legacy dependency pins were not viable on current interpreters/toolchains
- Problem: historical pins were brittle on newer Python/packaging tooling.
- Fix: standardized on Python 3.11 and curated compatible ranges in `pyproject.toml`, then generated and used `uv.lock` in CI/local runs.

### 2) Serialized sklearn artifacts were loaded under newer sklearn
- Problem: older serialized models triggered compatibility warnings and runtime attribute mismatches (notably GaussianNB legacy attributes).
- Fix: pinned to `scikit-learn>=1.2.2,<1.3` and added compatibility handling in `lexnlp/ml/predictor.py` for legacy `sigma_` data.

### 3) Pandas API drift broke a parser path
- Problem: deprecated `error_bad_lines` behavior caused incompatibility on modern pandas.
- Fix: updated `lexnlp/extract/es/regulations.py` to use `on_bad_lines='skip'` with backward-compatible fallback.

### 4) Test reliability depended on non-Python assets
- Problem: failing/skipped tests when corpora/models/Stanford jars were missing.
- Fix: introduced `scripts/bootstrap_assets.py` with deterministic flags for:
  - NLTK corpora
  - contract model artifact
  - Stanford jars/models (plus Java requirement)
  - optional Tika

### 5) Skips/xfails could hide regressions
- Problem: policy needed to prevent making builds green by bypassing tests.
- Fix: added `ci/skip_audit.py`, wired into CI to enforce inline `skip-audit:` annotations on any `skip`/`skipif`/`xfail`. `ci/skip_audit_allowlist.txt` remains available for rare cases, and now supports stable (non-line-number-based) keys.

### 6) Packaging artifacts included unwanted content risk
- Problem: release artifacts could unintentionally include local runtime blobs (`libs/stanford_nlp`), bytecode caches, and deprecated manifest files.
- Fix:
  - tightened `MANIFEST.in`
  - added `ci/check_dist_contents.py`
  - enforced artifact content audit in CI packaging job

### 7) Legacy `nose` usage in tests
- Problem: a handful of tests depended on `nose.tools`, pulling in an obsolete dependency.
- Fix: migrated assertions to `pytest`/plain `assert` and removed `nose` from dependency groups.

## Final validation results

- Skip audit: `skip-audit: OK (markers=11, allowlisted=0, annotated_new=11)`
- Base suite (no Stanford assets provisioned): `511 passed, 11 skipped, 0 failed`
- Stanford-gated suite (`LEXNLP_USE_STANFORD=true` targeted files): `11 passed, 0 failed`
- Skipped tests in base suite were exclusively Stanford-gated tests (`Stanford is disabled.`).
- Net demonstrated pass count (two-phase, fully provisioned): `522/522`
- Packaging:
  - `uv build` succeeds
  - `python3 ci/check_dist_contents.py` succeeds
- wheel install smoke test succeeds and imports `lexnlp==2.3.0`

## Follow-up completed (quality gate in CI)

- Added committed baseline metrics fixture:
  - `test_data/model_quality/is_contract_baseline_metrics.json`
- Extended `scripts/model_quality_gate.py` to:
  - consume baseline metrics JSON directly
  - validate fixture/min-probability alignment
  - optionally write canonical baseline metrics JSON
- Added a dedicated GitHub Actions job `model-quality` in
  - `.github/workflows/ci.yml`
  - This runs the contract-model quality gate and uploads the JSON result as an artifact.

## Follow-up completed (model artifact refresh workflow)

- Added `scripts/reexport_contract_model.py` to support deterministic re-serialization
  of `pipeline/is-contract/0.1` into a new local catalog tag (for example
  `pipeline/is-contract/0.2`) under the current runtime.
- The script writes per-tag metadata JSON and runs `scripts/model_quality_gate.py`
  automatically unless `--skip-quality-gate` is passed.
- The script also compares legacy sklearn warning counts between source and
  candidate artifacts to ensure warning behavior does not regress.

## Follow-up completed (bundled sklearn artifact refresh)

- Added `scripts/reexport_bundled_sklearn_models.py` and re-exported bundled
  sklearn/joblib artifacts under Python 3.11 + sklearn 1.2 runtime to eliminate
  legacy unpickle warnings for packaged models.
- Notable refreshed artifacts include:
  - `lexnlp/extract/de/date_model.pickle`
  - `lexnlp/extract/de/model.pickle`
  - `lexnlp/extract/en/addresses/addresses_clf.pickle` (kept plain pickle for `renamed_load`)
  - `lexnlp/nlp/en/segments/page_segmenter.pickle`
  - `lexnlp/nlp/en/segments/paragraph_segmenter.pickle`
  - `lexnlp/nlp/en/segments/section_segmenter.pickle`
  - `lexnlp/nlp/en/segments/title_locator.pickle`

## Final CI stabilization (post-migration)

While validating the migrated stack on GitHub Actions, one base-suite run still failed
with two environment-sensitive issues. Both were fixed without adding skips/xfails.

### 1) German money parsing on locale-limited runners
- Symptom: `lexnlp/extract/de/tests/test_money.py::TestMoneyPlain::test_symmetrical_money`
  returned `Decimal('10.800')` instead of `Decimal('10800')` in CI.
- Root cause: `de_DE.UTF-8` was not always available; locale resolution could fall back
  to non-German numeric conventions.
- Fix: hardened `lexnlp/utils/amount_delimiting.py` to enforce canonical `de_DE`
  delimiters when locale resolution does not match `de_DE` conventions.

### 2) Paragraph segmentation edge case for single-line input
- Symptom: `lexnlp/nlp/en/tests/test_paragraphs.py::TestParagraphs::test_date_text`
  intermittently returned `'6'` instead of the full timestamp text.
- Root cause: `splitlines_with_spans()` initialized `last_line_end` to `-1`, so
  no-newline input could be sliced from the final character depending on model output.
- Fix: updated `lexnlp/nlp/en/segments/paragraphs.py` to initialize `last_line_end`
  at `0`, preserving full single-line input spans.

### CI verification after these fixes
- Commit: `b07b9b6`
- Run: `https://github.com/5pence5/lexpredict-lexnlp_fixed/actions/runs/22010774834`
- Result: all jobs green
  - `Base Tests`
  - `Stanford Tests`
  - `Model Quality Gate`
  - `Packaging Smoke`

## Operational guidance

Reliable full-validation flow on this machine:

```bash
cd /Users/jackeames/Downloads/LexNLP

# env
uv venv --python 3.11 .venv
uv sync --frozen --python .venv/bin/python --extra dev --extra test

# assets
./.venv/bin/python scripts/bootstrap_assets.py --nltk --contract-model
./.venv/bin/python scripts/bootstrap_assets.py --stanford

# base tests
./.venv/bin/pytest -q

# stanford-only tests
PATH=/opt/homebrew/opt/openjdk@11/bin:$PATH \
LEXNLP_USE_STANFORD=true \
./.venv/bin/pytest -q \
  lexnlp/nlp/en/tests/test_stanford.py \
  lexnlp/extract/en/entities/tests/test_stanford_ner.py

# policy + packaging
python3 ci/skip_audit.py
uv build
python3 ci/check_dist_contents.py
```

## Follow-up completed (contract-type runtime compatibility)

- Problem: legacy `pipeline/contract-type/0.1` could fail to unpickle on Python
  3.11 (`TypeError: code() argument 13 must be str, not int`), making
  contract-type prediction unreliable on modern runtimes.
- Fix:
  - Added runtime model utilities in
    `/Users/jackeames/Downloads/LexNLP/lexnlp/extract/en/contracts/runtime_model.py`
    to train/store a deterministic fallback model from
    `corpus/contract-types/0.1`.
  - Added
    `/Users/jackeames/Downloads/LexNLP/scripts/train_contract_type_model.py`
    for explicit training/report generation.
  - Updated `ProbabilityPredictorContractType` to auto-fallback to
    `pipeline/contract-type/0.2-runtime` when legacy default loading fails and
    no explicit override is configured.
  - Extended bootstrap workflow with `--contract-type-model`.
  - Added CI `Contract Type Smoke` job to ensure this path remains working.
  - Added a fixed contract-type fixture + baseline metrics file and a dedicated
    quality gate script:
    - Fixture: `test_data/lexnlp/extract/en/contracts/tests/test_contracts/test_contract_type.csv`
    - Baseline: `test_data/model_quality/contract_type_baseline_metrics.json`
    - Gate: `scripts/contract_type_quality_gate.py`
  - Note: because the runtime tag is currently trained from corpora when the
    GitHub Release asset is missing, Linux vs macOS training can yield slightly
    different scores on the small fixture. The committed baseline metrics file
    is intentionally conservative so the gate remains stable across runners.
  - Added a GitHub Actions workflow to publish the runtime artifact as a GitHub
    Release asset:
    - `.github/workflows/publish-contract-type-runtime-model.yml`

## Follow-up completed (catalog path robustness)

- Problem: `lexnlp.ml.catalog` historically used `nltk.data.find('')` to locate
  the NLTK data root. On fresh CI runners with no existing NLTK data
  directories, this could raise during import and break bootstrap/model tasks.
- Fix: `lexnlp.ml.catalog` now resolves a writable directory from
  `nltk.data.path` (creating it if needed) and falls back to `~/nltk_data`.
  The resolved `CATALOG` directory is now created on import, so catalog scans
  are safe on fresh environments.
