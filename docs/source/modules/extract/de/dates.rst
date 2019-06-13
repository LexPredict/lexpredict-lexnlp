.. _extract_de_dates:

============
:mod:`lexnlp.extract.de.dates`: Extracting date references
============

The :mod:`lexnlp.extract.de.dates` module contains methods that allow for the extraction
of dates from text.  Sample formats that are handled by this module include:

 * vom 29. März 2017
 * 16.5.2002

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/common/tests/test_dates


.. currentmodule:: lexnlp.extract.de.dates


Extracting dates
----------------
.. autofunction:: get_date_list

Example ::

    >>> import lexnlp.extract.de.dates
    >>> text = " Artikel 39 des Gesetzes vom 29. März 2017 (BGBl. I S. 626) geändert worden ist"
    >>> print((lexnlp.extract.de.dates.get_date_list(text))
    [{'location_start': 29,
     'location_end': 42,
     'value': datetime.datetime(2017, 3, 29, 0, 0),
     'source': '29. März 2017'}]

