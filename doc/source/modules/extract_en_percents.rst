.. _extract_en_percents:

============
:mod:`lexnlp.extract.en.percents`: Extracting percents and rates
============

The :mod:`lexnlp.extract.en.percents` module contains methods that allow for the extraction
of percent and rate statements from text.  Example statements that are covered by default in this module include:

 * one percent
 * 1%
 * 50 bps
 * fifty basis points

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_percents


.. currentmodule:: lexnlp.extract.en.percents


Extracting conditions
----------------
.. autofunction:: get_percents

Example ::

    >>> import lexnlp.extract.en.percents
    >>> text = "At a discount of 1%"
    >>> print(list(lexnlp.extract.en.percents.get_percents(text)))
    [('%', 1.0, 0.01)]
    >>> text = "At a discount of 10 basis points"
    >>> print(list(lexnlp.extract.en.percents.get_percents(text)))
    [('basis points', 10.0, 0.001)]

