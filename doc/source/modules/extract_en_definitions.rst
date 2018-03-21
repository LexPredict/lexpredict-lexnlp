.. _extract_en_definitions:

============
:mod:`lexnlp.extract.en.definitions`: Extracting definition statements
============

The :mod:`lexnlp.extract.en.definitions` module contains methods that allow for the extraction
of definitional statements from text.  Example statements that are covered by default in this module are:

 * X shall [not] include ...
 * X shall have the meaning ...
 * X is hereby changed to ...
 * X shall be interpreted ...
 * X shall for purposes ...
 * X shall be deemed to ...
 * X shall refer to ...
 * X shall mean ...
 * X is defined ...
 * The word “X” includes every description of ...
 * The term “X” means ...
 * Description of term (the "x")

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_definitions


.. currentmodule:: lexnlp.extract.en.definitions


Extracting constraints
----------------
.. autofunction:: get_definitions

Example ::

    >>> import lexnlp.extract.en.definitions
    >>> text = 'and Acme, LLC ("Client")'
    >>> print(list(lexnlp.extract.en.definitions.get_definitions(text)))
    ['Client']
    >>> text = "“Advance” means a Revolving Credit Advance"
    >>> print(list(lexnlp.extract.en.definitions.get_definitions(text)))
    ['Advance']
