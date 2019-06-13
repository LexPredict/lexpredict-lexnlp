.. _extract_de_durations:

============
:mod:`lexnlp.extract.de.durations`: Extracting durations
============

The :mod:`lexnlp.extract.de.durations` module contains methods that allow for the extraction
of durations from text for "DE" locale.  Sample durations that are covered by this module include:

 * 14. Lebensjahr
 * 25. Lebensjahres
 * Kalenderjahr
 * fünfundzwanzig Jahren
 * zwei Monate
 * 3 Wochen
 * zwanzig tage

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/de/tests/test_durations

.. currentmodule:: lexnlp.extract.de.durations

Extracting durations
----------------
.. autofunction:: get_duration_list

Example ::

    >>> import lexnlp.extract.de.durations
    >>> text = "zwanzig tage"
    >>> print(lexnlp.extract.de.durations.get_duration_list(text))
    [{'location_start': 0,
      'location_end': 12,
      'source_text': 'zwanzig tage',
      'unit_name_local': 'tage',
      'unit_name': 'day',
      'unit_prefix': '',
      'amount': 20,
      'amount_days': 20}]

.. autofunction:: get_durations

Example ::

    >>> import lexnlp.extract.de.durations
    >>> text = "3 Wochen"
    >>> print(list(lexnlp.extract.de.durations.get_durations(text)))
    [{'location_start': 0,
      'location_end': 8,
      'source_text': '3 Wochen',
      'unit_name_local': 'wochen',
      'unit_name': 'week',
      'unit_prefix': '',
      'amount': 3.0,
      'amount_days': 21.0}]
