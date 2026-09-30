# Dependency upgrade guide

This guide covers the setup and compatibility checks needed for the maintenance
upgrade. Run commands from the repository root.

## Supported runtime

- Python 3.10–3.13; Python 3.12 is the default development/docs interpreter.
- Python 3.9 and older are retired because they are outside Python security
  support and constrain upgrades to the numerical and packaging dependencies.
- Python 3.14 is excluded because Gensim 4.4.0 lacks compatible wheels and its
  extension source fails against removed CPython/NumPy internals.
- scikit-learn stays at 1.7.2 to retain Python 3.10 and persisted-model support.
- `pyproject.toml` and `uv.lock` replace Pipenv and split requirements files.

CI is configured for the supported Python matrix and minimum/latest dependency
checks. Assess the candidate commit's results rather than assuming the matrix
configuration establishes success. Gensim Linux wheels require `manylinux_2_28`.

## Setup and data

```bash
uv python install 3.12
uv sync --frozen --python 3.12 --extra dev --extra test
uv pip check --python .venv/bin/python
.venv/bin/python scripts/bootstrap_assets.py \
  --nltk --contract-model --contract-type-model
```

`uv sync` creates an editable `.venv`; it does not require pip. Include every
extra you want to keep in the same sync command. After changing dependencies,
run `uv lock`, `uv lock --check`, and the frozen sync again; never hand-edit
`uv.lock`.

Bundled models ship in the distribution. NLTK resources use an official,
revision-pinned SHA-256 catalog. Release models/corpora, Stanford, and Tika also
require pinned verification before atomic installation. Only load pickle/joblib
artifacts from trusted releases or producers.

The is-contract bootstrap downloads `pipeline/is-contract/0.2` when available;
otherwise it re-exports the pinned `0.1` source for the local runtime.
The contract-type bootstrap builds or reuses
`pipeline/contract-type/0.2-runtime` from its pinned corpus. These local migration
fallbacks preserve the upgraded runtime without requiring a new model release.
Generated candidates use local catalog paths and must not replace the exact
bytes of manifest-pinned release artifacts. Source checksum and trust failures
remain errors.

For a trusted mirror, configure `LEXNLP_MODELS_REPO_SLUG` and a locally reviewed
`LEXNLP_ASSET_MANIFEST` whose repository, tags, sizes, and digests match it.
Changing only the repository is insufficient; the manifest is a local trust root.

Optional Java integrations:

```bash
.venv/bin/python scripts/bootstrap_assets.py --stanford
.venv/bin/python scripts/bootstrap_assets.py --tika
LEXNLP_USE_TIKA=true scripts/run_tika.sh
```

Stanford defaults to `stanford_nlp/` below NLTK's selected data directory.
Runtime discovery searches `nltk.data.path`, then legacy locations. A custom
`--stanford-dir` or legacy jar location must be explicitly covered by
`NLTK_DATA`; bootstrap never adds a trust path. For example, set `NLTK_DATA` to
`/path/to/trusted-nlp-data` and install with
`--stanford-dir /path/to/trusted-nlp-data/stanford_nlp`. Tika 3.3.2 binds to
loopback and requires Java 11+; add the `tika` extra when its Python client is used.

## Persisted-model migration

Use Python 3.12.13 with `constraints/model-artifact-abi.txt`: joblib 1.5.0,
NumPy 1.26.4, pandas 2.2.0, scikit-learn 1.7.2, SciPy 1.13.0, and threadpoolctl
3.6.0. Model bytes produced only under NumPy 2.x can fail at the supported lower
bound. Every re-export must load and preserve fixed-fixture predictions/quality
under both this producer ABI and the latest locked runtime.

```bash
uv python install 3.12.13
uv venv /tmp/lexnlp-model-producer --python 3.12.13
uv pip install --python /tmp/lexnlp-model-producer/bin/python \
  --constraint constraints/model-artifact-abi.txt -e .
/tmp/lexnlp-model-producer/bin/python scripts/reexport_bundled_sklearn_models.py
/tmp/lexnlp-model-producer/bin/python scripts/reexport_contract_model.py \
  --source-tag pipeline/is-contract/0.1 --target-tag pipeline/is-contract/0.2 \
  --baseline-metrics-json test_data/model_quality/is_contract_baseline_metrics.json
```

Review the generated provenance and artifact digests before committing model
bytes. Keep every allowed quality regression at `0.0`; never rewrite baselines
or add skip/xfail markers to conceal a failure. Run the fixed-fixture gates:

```bash
.venv/bin/python scripts/model_quality_gate.py \
  --baseline-tag pipeline/is-contract/0.1 --candidate-tag pipeline/is-contract/0.2 \
  --baseline-metrics-json test_data/model_quality/is_contract_baseline_metrics.json
.venv/bin/python scripts/contract_type_quality_gate.py \
  --baseline-tag pipeline/contract-type/0.2-runtime \
  --candidate-tag pipeline/contract-type/0.2-runtime \
  --baseline-metrics-json test_data/model_quality/contract_type_baseline_metrics.json
```

## Validation and distributions

```bash
.venv/bin/ruff check lexnlp scripts ci --select E4,E7,E9,F
.venv/bin/python ci/skip_audit.py
.venv/bin/python scripts/reexport_bundled_sklearn_models.py --check-current
.venv/bin/pytest lexnlp scripts/tests
uv sync --frozen --python 3.12 --extra dev --extra test --extra docs
.venv/bin/sphinx-build -W --keep-going \
  -b html documentation/docs/source documentation/docs/build/html
uv build
.venv/bin/python ci/check_dist_contents.py
```

After verified Stanford bootstrap, run its optional suite:

```bash
LEXNLP_USE_STANFORD=true .venv/bin/pytest \
  lexnlp/nlp/en/tests/test_stanford.py lexnlp/extract/en/entities/tests/test_stanford_ner.py
```

Install wheel and sdist independently in clean environments:

```bash
uv venv /tmp/lexnlp-wheel --python 3.12
uv pip install --python /tmp/lexnlp-wheel/bin/python dist/*.whl
uv venv /tmp/lexnlp-sdist --python 3.12
uv pip install --python /tmp/lexnlp-sdist/bin/python dist/*.tar.gz
/tmp/lexnlp-wheel/bin/python -I ci/check_dist_contents.py --installed
/tmp/lexnlp-sdist/bin/python -I ci/check_dist_contents.py --installed
```

Smoke-import from outside the checkout with `python -I` so an editable source
or `PYTHONPATH` cannot mask missing distribution resources. Missing NLTK/Stanford
assets require the matching verified bootstrap and trusted data path; model
quality or distribution failures require fixing the cause, not weakening checks.

## Known NLTK dependency finding

NLTK 3.10.3 remains vulnerable to **GHSA-8mgp-746c-j5xp** (aliases
**CVE-2026-81726**, **PYSEC-2026-3740**). The reviewed applicability exception in
`ci/dependency_audit_exceptions.json` expires **30 October 2026**. The affected
persistence APIs (`TransitionParser.train/parse`, `AveragedPerceptron.save/load`,
`PerceptronTagger.save_to_json`, and `save_maxent_params`) are not reached by the
reviewed LexNLP inference/training paths. Downstream direct use of those NLTK
APIs or untrusted model paths is outside this assessment and remains vulnerable.

The raw strict `pip-audit` report stays visible. `ci/check_dependency_audit.py`
rejects incomplete reports, other findings, and changes to the reviewed version,
source fingerprint, advisory description, or expiry. Adopt a patched upstream
release when available, rerun compatibility checks, and remove the exception.
