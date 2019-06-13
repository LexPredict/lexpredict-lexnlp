.. _extract_de_percents:

============
:mod:`lexnlp.extract.de.percents`: Extracting percents
============

The :mod:`lexnlp.extract.de.percents` module contains methods that allow for the extraction
of percents from text for "DE" locale.  Sample percents that are covered by this module include:

 * 15 Volumenprozent
 * zwanzig Prozent
 * zwanzig %
 * 20%

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/de/tests/test_percents

.. currentmodule:: lexnlp.extract.de.percents

Extracting percents
----------------
.. autofunction:: get_percent_list

Example ::

    >>> import lexnlp.extract.de.percents
    >>> text = "zwanzig Prozent"
    >>> print(lexnlp.extract.de.percents.get_percent_list(text))
    [{'location_start': 0,
      'location_end': 15,
      'source_text': 'zwanzig Prozent',
      'unit_name': 'prozent',
      'amount': 20,
      'real_amount': 20}]

.. autofunction:: get_percents

Example ::

    >>> import lexnlp.extract.de.percents
    >>> print(list(lexnlp.extract.de.percents.get_percents("1%")))
    [{'location_start': 0,
      'location_end': 2,
      'source_text': '1%',
      'unit_name': '%',
      'amount': 1.0,
      'real_amount': 1.0}]
