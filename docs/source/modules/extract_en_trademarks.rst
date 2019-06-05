.. _extract_en_trademarks:

============
:mod:`lexnlp.extract.en.trademarks`: Extracting trademark references
============

The :mod:`lexnlp.extract.en.trademarks` module contains methods that allow for the extraction
of trademarks references from text.  Examples include:

 * Widget™
 * Widget(TM)
 * Widget®
 * Widget(R)

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_trademarks


.. currentmodule:: lexnlp.extract.en.trademarks


Extracting conditions
----------------
.. autofunction:: get_trademarks

Example ::

    >>> import lexnlp.extract.en.trademarks
    >>> text = "Customer agrees to license HAL(TM)"
    >>> print(list(lexnlp.extract.en.trademarks.get_trademarks(text)))
    ['HAL (TM)']
    >>> text = "Customer agrees to purchase a minimum quantity of 1000 Widget® units"
    >>> print(list(lexnlp.extract.en.trademarks.get_trademarks(text)))
    ['Widget®']


