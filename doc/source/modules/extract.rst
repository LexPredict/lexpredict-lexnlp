.. _extract:

============
:mod:`lexnlp.extract`: Extracting structured data from unstructured text
============

The :mod:`lexnlp.extract` module contains methods that allow for the extraction
of structured data from unstructured textual sources.  Supported data types include a
wide range of facts relevant to contract or document analysis, including dates, amounts,
proper noun types, and conditional statements.

This module is structured along ISO 2-character language codes.  Currently, the following languages are stable:
 * English: :mod:`lexnlp.extract.en`

Extraction methods follow a simple `get_X` pattern as demonstrated below::

    >>> import lexnlp.extract.en.amounts
    >>> text = "There are ten cows in the 2 acre pasture."
    >>> print(list(lexnlp.extract.en.amounts.get_amounts(text)))
    [10, 2.0]

Pattern-based extraction methods
----------------
The full list of supported pattern-based structured data types is below:
 * :ref:`amounts <extract_en_amounts>`, e.g., "ten pounds" or "5.8 megawatts"
 * :ref:`citations <extract_en_citations>`, e.g., "10 U.S. 100" or "1998 S. Ct. 1"
 * :ref:`conditions <extract_en_conditions>`, e.g., "subject to ..." or "unless and until ..."
 * :ref:`constraints <extract_en_constraints>`, e.g., "no more than" or "
 * :ref:`copyright <extract_en_copyright>`, e.g., "(C) Copyright 2000 Acme"
 * :ref:`courts <extract_en_courts>`, e.g., "Supreme Court of New York"
 * :ref:`dates <extract_en_dates>`, e.g., "June 1, 2017" or "2018-01-01"
 * :ref:`definitions <extract_en_definitions>`, e.g., "Term shall mean ..."
 * :ref:`distances <extract_en_distances>`, e.g., "fifteen miles"
 * :ref:`durations <extract_en_durations>`, e.g., "ten years" or "thirty days"
 * :ref:`geographic and geopolitical entities <extract_en_geoentities>`, e.g., "New York" or "Norway"
 * :ref:`money and currency usages <extract_en_money>`, e.g., "$5" or "10 Euro"
 * :ref:`percents and rates <extract_en_percents>`, e.g., "10%" or "50 bps"
 * :ref:`PII <extract_en_pii>`, e.g., "212-212-2121" or "999-999-9999"
 * :ref:`ratios <extract_en_ratios>`, e.g.," 3:1" or "four to three"
 * :ref:`regulations <extract_en_regulations>`, e.g., "32 CFR 170"
 * :ref:`trademarks <extract_en_trademarks>`, e.g., "MyApp (TM)"
 * :ref:`URLs <extract_en_url>`, e.g., "http://acme.com/"

.. note:
    The `lexnlp.extract.en.dates` module optionally relies on machine learning classifiers
    to identify and remove false positives.

NLP-based extraction methods
----------------
In addition to pattern-based structured data types, the `lexnlp.extract` module also supports
NLP methods based on tagged part-of-speech classifiers.  These classifiers are based on
NLTK and, optionally, Stanford NLP libraries.  The list of these modules is below:
 * :ref:`named entity extraction with NLTK maximum entropy classifier`
 * :ref:`named entity extraction with NLTK and regular expressions`
 * :ref:`named entity extraction with Stanford Named Entity Recognition (NER) models`