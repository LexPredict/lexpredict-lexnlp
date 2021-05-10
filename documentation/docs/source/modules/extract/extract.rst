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
 * German: :mod:`lexnlp.extract.de`
 * Spanish: :mod:`lexnlp.extract.es`

Extraction methods follow a simple `get_X` pattern as demonstrated below::

    >>> import lexnlp.extract.en.amounts
    >>> text = "There are ten cows in the 2 acre pasture."
    >>> print(list(lexnlp.extract.en.amounts.get_amounts(text)))
    [10, 2.0]

Pattern-based extraction methods
----------------
The full list of supported pattern-based structured data types is below:
  * "EN" locale:

    * :ref:`acts <extract_en_acts>`, e.g., "section 1 of the Advancing Hope Act, 1986"
    * :ref:`amounts <extract_en_amounts>`, e.g., "ten pounds" or "5.8 megawatts"
    * :ref:`citations <extract_en_citations>`, e.g., "10 U.S. 100" or "1998 S. Ct. 1"
    * :ref:`companies <extract_en_companies>`, e.g., "Lexpredict LLC"
    * :ref:`conditions <extract_en_conditions>`, e.g., "subject to ..." or "unless and until ..."
    * :ref:`constraints <extract_en_constraints>`, e.g., "no more than" or "
    * :ref:`copyright <extract_en_copyright>`, e.g., "(C) Copyright 2000 Acme"
    * :ref:`courts <extract_en_courts>`, e.g., "Supreme Court of New York"
    * :ref:`CUSIP <extract_en_cusip>`, e.g., "392690QT3"
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
    * :ref:`URLs <extract_en_urls>`, e.g., "http://acme.com/"

  * "DE" locale:

    * :ref:`amounts <extract_de_amounts>`, e.g., "1 tausend" or "eine halbe Million Dollar"
    * :ref:`citations <extract_de_citations>`, e.g., "BGBl. I S. 434"
    * :ref:`copyrights <extract_de_copyrights>`, e.g., "siemens.com globale Website Siemens © 1996 – 2019"
    * :ref:`court citations <extract_de_court_citations>`, e.g., "BStBl I 2003, 240"
    * :ref:`courts <extract_de_courts>`, e.g., "Amtsgerichte"
    * :ref:`dates <extract_de_dates>`, e.g., "vom 29. März 2017"
    * :ref:`definitions <extract_de_definitions>`
    * :ref:`durations <extract_de_durations>`, e.g., "14. Lebensjahr" or "fünfundzwanzig Jahren"
    * :ref:`geographic and geopolitical entities <extract_de_geoentities>`, e.g., "Albanien"
    * :ref:`percents <extract_de_percents>`, e.g., "15 Volumenprozent"

  * "ES" locale:

    * :ref:`copyrights <extract_es_copyrights>`, e.g., ""Website BBC Mundo © 1996 – 2019"
    * :ref:`courts <extract_es_courts>`, e.g., "Tribunal Superior de Justicia de Madrid"
    * :ref:`dates <extract_es_dates>`, e.g., "15 de febrero" or "1ºde enero de 1999"
    * :ref:`definitions <extract_es_definitions>`, e.g., ""El ser humano": una anatomía moderna humana"
    * :ref:`regulations <extract_es_regulations>`, e.g., "Comisión Nacional Bancaria y de Valores"

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
These modules allow to extract data types like:
 * :ref:`addresses`, e.g., "1999 Mount Read Blvd, Rochester, NY, USA, 14615"
 * :ref:`companies`, e.g., "Lexpredict LLC"
 * :ref:`persons`, e.g., "John Doe"