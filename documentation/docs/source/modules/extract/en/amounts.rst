.. _extract_en_amounts:

============
:mod:`lexnlp.extract.en.amounts`: Extracting amounts
============

The :mod:`lexnlp.extract.en.amounts` module contains methods that allow for the extraction
of amounts from text.  Sample amounts that are covered by this module include:

 * THIRTY-SIX THOUSAND TWO-HUNDRED SIXTY-SIX AND 2/100
 * total 2 million people
 * total 2.035 billion tons of
 * fifteen cats
 * 20,000,000
 * thirty-five million units
 * 10K files
 * 1 trill

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_amounts

.. currentmodule:: lexnlp.extract.en.amounts

Extracting amounts
----------------
.. autofunction:: get_amounts

Example ::

    >>> import lexnlp.extract.en.amounts
    >>> text = "There are ten cows in the dozen acre pasture."
    >>> print(list(lexnlp.extract.en.amounts.get_amounts(text)))
    [10, 12]

    >>> text = "Twenty-seven days until the one-hundred and one dogs arrive."
    >>> print(list(lexnlp.extract.en.amounts.get_amounts(text)))
    [27, 101]

    >>> text = "There are 10K documents."
    >>> print(list(lexnlp.extract.en.amounts.get_amounts(text)))
    [10000.0]

    >>> text = "There is 10 trill Zimbabwean Paper Money for sale on eBay"
    >>> print(list(lexnlp.extract.en.amounts.get_amounts(text)))
    [10000000000000.0]

Converting text to numbers
----------------
.. autofunction:: text2num

Example ::

    >>> import lexnlp.extract.en.amounts
    >>> print(lexnlp.extract.en.amounts.text2num("seventy one"))
    71
    >>> print(lexnlp.extract.en.amounts.text2num("one billion and seventy"))
    1000000070

