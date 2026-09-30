.. _installation:

Installation and validation
===========================

LexNLP supports Python 3.10 through 3.13. The default development and
documentation interpreter is Python 3.12. Python 3.14 is excluded while the
required Gensim extension lacks compatible wheels/source support.

Reproducible development setup
------------------------------

From a checkout of this repository, install the locked dependency set with
`uv <https://docs.astral.sh/uv/>`_::

    uv python install 3.12
    uv sync --frozen --python 3.12 --extra dev --extra test
    uv pip check --python .venv/bin/python

This creates ``.venv`` and installs LexNLP editable. Omit the ``dev`` and
``test`` extras for a minimal runtime environment. ``uv`` does not require pip
inside the virtual environment. Dependency changes belong in
``pyproject.toml`` followed by ``uv lock``; do not hand-edit ``uv.lock``.

Bundled models and external data
--------------------------------

Bundled segmentation and extraction models ship in the distribution. The
complete base suite also needs verified NLTK data and pipeline classifiers::

    .venv/bin/python scripts/bootstrap_assets.py \
        --nltk --contract-model --contract-type-model

The bootstrap checks the pinned artifact digests and installs atomically.
NLTK corpora use a separate pinned catalog from model/corpus release assets.
Only load pickle/joblib model files from trusted releases or producers.

Optional Stanford NLP
---------------------

Stanford integrations require Java 11 or newer and verified legacy assets::

    .venv/bin/python scripts/bootstrap_assets.py --stanford

The default destination is ``stanford_nlp/`` under NLTK's selected data
directory. Runtime discovery searches ``nltk.data.path`` and supported legacy
locations. Custom destinations chosen with ``--stanford-dir`` must be covered
by the trusted ``NLTK_DATA`` path before use; installing files does not expand
that trust path automatically. Existing legacy jar locations also need explicit
coverage in ``NLTK_DATA``.

After provisioning the assets, enable and test the integrations explicitly::

    LEXNLP_USE_STANFORD=true .venv/bin/pytest \
        lexnlp/nlp/en/tests/test_stanford.py \
        lexnlp/extract/en/entities/tests/test_stanford_ner.py

Optional Apache Tika
--------------------

Tika runs as a separate Java service. Install its Python client only when the
integration is needed, retaining any other desired extras in the same sync::

    uv sync --frozen --python 3.12 --extra dev --extra test --extra tika
    .venv/bin/python scripts/bootstrap_assets.py --tika
    LEXNLP_USE_TIKA=true scripts/run_tika.sh

The launcher verifies Apache Tika 3.3.2 and binds to loopback. It does not
replace an unrelated process already occupying the selected port.

Required checks
---------------

Run the complete runtime and repository-tool suites after bootstrap::

    .venv/bin/ruff check lexnlp scripts ci --select E4,E7,E9,F
    .venv/bin/python ci/skip_audit.py
    .venv/bin/python scripts/reexport_bundled_sklearn_models.py --check-current
    .venv/bin/pytest lexnlp scripts/tests

CI is configured for the supported Python matrix, minimum dependency bounds,
quality gates, optional Stanford integration, and wheel/sdist validation.
Assess the workflow results for the candidate commit rather than assuming
the configuration establishes success.

The dependency audit retains a known NLTK 3.10.3 vulnerability with a reviewed
exception for affected persistence APIs that the shipped LexNLP call paths do
not reach. The exception does not cover downstream direct use of those NLTK
APIs. The raw finding remains visible; ``ci/dependency_audit_exceptions.json``
and ``MIGRATION_RUNBOOK.md`` describe the exact scope and expiry.

Build this documentation with warnings fatal::

    uv sync --frozen --python 3.12 --extra dev --extra test --extra docs
    .venv/bin/sphinx-build -W --keep-going \
        -b html documentation/docs/source documentation/docs/build/html

``uv sync`` removes packages outside the selected set, so request every extra
you intend to keep. Read the Docs uses the locked ``docs`` extra.

See ``MIGRATION_RUNBOOK.md`` in the repository for clean distribution installs,
the exact Python 3.12.13 model-producer ABI, strict quality thresholds, custom
asset locations, and model migration. The runtime dependency stack and
model-producer stack have separate purposes; never produce release model
bytes under an arbitrary newer numerical ABI.
