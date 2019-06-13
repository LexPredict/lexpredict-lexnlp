.. _extract_es_dates:

============
:mod:`lexnlp.extract.es.dates`: Extracting date references
============

The :mod:`lexnlp.extract.es.dates` module contains methods that allow for the extraction
of dates from text.  Sample formats that are handled by this module include:

 * 1ºde enero de 1999
 * 10.05.2001

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/common/tests/test_dates


.. currentmodule:: lexnlp.extract.es.dates


Extracting dates
----------------
.. autofunction:: get_date_list

Example ::

    >>> import lexnlp.extract.es.dates
    >>> text = "1ºde enero de 1999"
    >>> print(lexnlp.extract.es.dates.get_date_list(text))
    [{'location_start': 0,
      'location_end': 18,
      'value': datetime.datetime(1999, 6, 1, 0, 0),
      'source': '1ºde enero de 1999'}]

    >>> text = "10.05.2001"
    >>> print(lexnlp.extract.es.dates.get_date_list(text))
    [{'location_start': 0,
      'location_end': 10,
      'value': datetime.datetime(2001, 5, 10, 0, 0),
      'source': '10.05.2001'}]

.. autofunction:: get_dates

Example ::

    >>> import lexnlp.extract.es.dates
    >>> text = " 15 de febrero"
    >>> print(list(lexnlp.extract.es.dates.get_dates(text)))
    [{'location_start': 1,
      'location_end': 14,
      'value': datetime.datetime(2019, 2, 15, 0, 0),
      'source': '15 de febrero'}]

