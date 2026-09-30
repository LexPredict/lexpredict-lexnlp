|CI| |Documentation|

LexNLP by LexPredict
====================

LexNLP is a Python library for working with real, unstructured legal text,
including contracts, plans, policies, and procedures.

It provides:

* legal-aware sentence, paragraph, page, section, and title segmentation;
* extraction of amounts, money, percentages, ratios, dates, durations,
  conditions, constraints, courts, regulations, citations, and other facts;
* English, German, and Spanish extraction components;
* pre-trained segmentation and classification models; and
* utilities for building legal-text clustering and classification workflows.

Requirements
------------

* Python 3.10, 3.11, 3.12, or 3.13
* `uv <https://docs.astral.sh/uv/>`__ for the reproducible development workflow
* Java 11 or newer only when using the optional Stanford or Apache Tika
  integrations

Quick start
-----------

.. code-block:: bash

   git clone https://github.com/LexPredict/lexpredict-lexnlp.git
   cd lexpredict-lexnlp
   uv python install 3.12
   uv sync --frozen --python 3.12 --extra dev --extra test

``uv sync`` creates ``.venv`` and installs LexNLP in editable mode. For a
minimal runtime environment, omit the ``dev`` and ``test`` extras.

Check the installed dependency graph without adding pip to the environment:

.. code-block:: bash

   uv pip check --python .venv/bin/python

Data, models, and optional services
-----------------------------------

LexNLP deliberately keeps four kinds of supporting resources distinct:

1. **Bundled models** ship inside the Python distribution. No download is
   required.
2. **NLTK data** is not bundled. Install the exact resource set used by
   LexNLP:

   .. code-block:: bash

      .venv/bin/python scripts/bootstrap_assets.py --nltk

3. **Pipeline classifiers** are downloaded or migrated from pinned, trusted
   release/corpus inputs for the upgraded runtime:

   .. code-block:: bash

      .venv/bin/python scripts/bootstrap_assets.py \
        --contract-model \
        --contract-type-model

4. **Stanford NLP and Apache Tika are optional Java integrations.** They are
   not needed for LexNLP's core extractors:

   .. code-block:: bash

      .venv/bin/python scripts/bootstrap_assets.py --stanford
      .venv/bin/python scripts/bootstrap_assets.py --tika
      LEXNLP_USE_TIKA=true scripts/run_tika.sh

Stanford assets default to ``stanford_nlp/`` inside NLTK's selected data
directory, so installed packages can find them outside a source checkout.
If you choose ``--stanford-dir``, include that directory or its containing NLTK
data root in ``NLTK_DATA`` before using the integration. Existing legacy Stanford
locations remain supported and also need explicit ``NLTK_DATA`` coverage. See
the runbook for a custom-path example.

The bootstrap verifies and atomically installs the pinned Stanford, Tika,
model, and corpus assets. NLTK resources come from the official ``nltk_data``
repository, are verified against LexNLP's pinned SHA-256 catalog, and are
installed in NLTK-compatible directories. The catalog includes both
``omw-1.4`` and ``omw-2.0``.
Persisted Python model files use pickle/joblib formats and must only be loaded
from trusted LexNLP releases or another trusted producer.

Validation
----------

.. code-block:: bash

   .venv/bin/ruff check lexnlp scripts ci --select E4,E7,E9,F
   .venv/bin/python ci/skip_audit.py
   .venv/bin/python scripts/reexport_bundled_sklearn_models.py --check-current
   .venv/bin/pytest lexnlp scripts/tests

Stanford-gated tests are a separate, explicitly provisioned suite:

.. code-block:: bash

   LEXNLP_USE_STANFORD=true .venv/bin/pytest \
     lexnlp/nlp/en/tests/test_stanford.py \
     lexnlp/extract/en/entities/tests/test_stanford_ner.py

See `MIGRATION_RUNBOOK.md
<https://github.com/LexPredict/lexpredict-lexnlp/blob/master/MIGRATION_RUNBOOK.md>`__
for clean-environment, packaging, model migration, and quality checks.

Dependency auditing retains a known NLTK 3.10.3 vulnerability under a scoped,
time-limited applicability exception. The runbook documents the affected APIs,
applicability assessment, and expiry.

Project links
-------------

* `Documentation <https://lexpredict-lexnlp.readthedocs.io/en/latest/>`__
* `Source and release history
  <https://github.com/LexPredict/lexpredict-lexnlp>`__
* `ContraxSuite <https://github.com/LexPredict/lexpredict-contraxsuite>`__
* `LexPredict <https://lexpredict.com/>`__

License
-------

LexNLP is available under the AGPL-3.0-or-later terms in ``LICENSE``. Contact
``support@contraxsuite.com`` about alternative commercial licensing.

.. |CI| image:: https://github.com/LexPredict/lexpredict-lexnlp/actions/workflows/ci.yml/badge.svg?branch=master
   :target: https://github.com/LexPredict/lexpredict-lexnlp/actions/workflows/ci.yml
   :alt: CI
.. |Documentation| image:: https://readthedocs.org/projects/lexpredict-lexnlp/badge/?version=latest
   :target: https://lexpredict-lexnlp.readthedocs.io/en/latest/
   :alt: Documentation
