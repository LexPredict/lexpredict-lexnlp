.. _extract_de_amounts:

============
:mod:`lexnlp.extract.de.amounts`: Extracting amounts
============

The :mod:`lexnlp.extract.de.amounts` module contains methods that allow for the extraction
of amounts from text for "DE" locale.  Sample amounts that are covered by this module include:

 * sechseinhalb
 * zwei Millionen vierhundertzweiundzwanzigtausendsiebenhundertdreieinhalb
 * 2.035 millionen
 * 20,000,000
 * 10K

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/de/tests/test_amounts

.. currentmodule:: lexnlp.extract.de.amounts

Extracting amounts
----------------
.. autofunction:: get_amount_list

Example ::

    >>> import lexnlp.extract.de.amounts
    >>> text = "tausendzweihundertvierunddreißig"
    >>> print(lexnlp.extract.de.amounts.get_amount_list(text))
    [1234]

    >>> text = "eine halbe Million Dollar"
    >>> print(lexnlp.extract.de.amounts.get_amount_list(text))
    [500000.0]

    >>> text = "drei viertel"
    >>> print(lexnlp.extract.de.amounts.get_amount_list(text))
    [0.75]



.. autofunction:: get_amounts

Example ::

    >>> import lexnlp.extract.de.amounts
    >>> print(list(lexnlp.extract.de.amounts.get_amounts("eine")))
    [1]
