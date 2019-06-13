.. _extract_en_ratios:

============
:mod:`lexnlp.extract.en.ratios`: Extracting ratios
============

The :mod:`lexnlp.extract.en.ratios` module contains methods that allow for the extraction
of ratio statements from text.  Example statements include:

 * 3:1
 * 3.0:1.0
 * three to one


The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_ratios


.. currentmodule:: lexnlp.extract.en.ratios


Extracting conditions
----------------
.. autofunction:: get_ratios

Example ::

    >>> import lexnlp.extract.en.ratios
    >>> text = "At a leverage ratio of no more than ten to one."
    >>> print(list(lexnlp.extract.en.ratios.get_ratios(text)))
    [(10, 1, 10.0)]
    >>> text = "At a leverage ratio of no more than 2.5:1."
    >>> print(list(lexnlp.extract.en.ratios.get_ratios(text)))
    [(2.5, 1.0, 2.5)]


