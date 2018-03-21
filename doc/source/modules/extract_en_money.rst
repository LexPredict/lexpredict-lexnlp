.. _extract_en_money:

============
:mod:`lexnlp.extract.en.money`: Extracting money and currency references
============

The :mod:`lexnlp.extract.en.money` module contains methods that allow for the extraction
of money and currency amounts from text.  Example references that are covered by default in this module include:

 * five dollars
 * 5 dollars
 * 5 USD
 * $5

Comprehensive ISO 4217 codes can be captured, but frequently result in false positive matches in real documents.
By default, only the following ISO 4217 codes and currency symbols are detected:
 * USD/$: US Dollars
 * EUR/€: Euros
 * GBP/£: Great British pounds
 * JPY/¥: Japanese Yen
 * CNY/RMB/元/¥: Chinese Yuan/Renminbi
 * INR/₨/₹: Indian Rupee

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_money


.. currentmodule:: lexnlp.extract.en.money


Extracting money and currency references
----------------
.. autofunction:: get_money

Example ::

    >>> import lexnlp.extract.en.money
    >>> text = "The price will be 5 million GBP."
    >>> print(list(lexnlp.extract.en.money.get_money(text)))
    [(5000000.0, 'GBP')]

    >>> import lexnlp.extract.en.money
    >>> text = "The price will be ¥250000000"
    >>> print(list(lexnlp.extract.en.money.get_money(text)))
    [(250000000.0, 'JPY')]


