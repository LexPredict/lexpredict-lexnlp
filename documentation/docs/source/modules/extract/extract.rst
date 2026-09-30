.. _extract:

========================================================================
:mod:`lexnlp.extract`: Extracting structured data from unstructured text
========================================================================

The :mod:`lexnlp.extract` package contains legal-text extractors grouped by
ISO two-character locale. English, German, and Spanish components share common
annotation and parsing infrastructure while preserving locale-specific rules.

Extraction methods generally follow a ``get_X`` generator pattern:

.. code-block:: python

   import lexnlp.extract.en.amounts

   text = "There are ten cows in the 2 acre pasture."
   print(list(lexnlp.extract.en.amounts.get_amounts(text)))

Pattern-based extraction
------------------------

English documentation covers:

* :ref:`acts <extract_en_acts>`
* :ref:`amounts <extract_en_amounts>`
* :ref:`citations <extract_en_citations>`
* :ref:`companies <extract_en_companies>`
* :ref:`conditions <extract_en_conditions>`
* :ref:`constraints <extract_en_constraints>`
* :ref:`copyright references <extract_en_copyright>`
* :ref:`courts <extract_en_courts>`
* :ref:`CUSIP identifiers <extract_en_cusip>`
* :ref:`dates <extract_en_dates>`
* :ref:`definitions <extract_en_definitions>`
* :ref:`distances <extract_en_distances>`
* :ref:`durations <extract_en_durations>`
* :ref:`geographic entities <extract_en_geoentities>`
* :ref:`money <extract_en_money>`
* :ref:`percentages <extract_en_percents>`
* :ref:`personally identifiable information <extract_en_pii>`
* :ref:`ratios <extract_en_ratios>`
* :ref:`regulations <extract_en_regulations>`
* :ref:`trademarks <extract_en_trademarks>`
* :ref:`URLs <extract_en_urls>`

German documentation covers:

* :ref:`amounts <extract_de_amounts>`
* :ref:`citations <extract_de_citations>`
* :ref:`dates <extract_de_dates>`
* :ref:`durations <extract_de_durations>`
* :ref:`percentages <extract_de_percents>`

Spanish date extraction is described under :ref:`extract_es_dates`. The
package also contains Spanish courts, definitions, and regulations extractors.

NLP-assisted extraction
-----------------------

Named-entity extraction is available through NLTK maximum-entropy models,
legal-domain regular expressions, and the optional Stanford NER integration.
The Stanford path requires separately bootstrapped, verified assets and Java;
it is not required by core pattern extractors.

Some extractors can use bundled classifiers to reject false positives.
Pipeline classifiers are reproducibly built or re-exported from pinned model
and corpus inputs; see the repository migration runbook for provisioning and
compatibility policy.

.. toctree::
   :hidden:
   :glob:

   de/*
   en/*
   es/*
