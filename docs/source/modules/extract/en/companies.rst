.. _extract_en_companies:

============
:mod:`lexnlp.extract.en.entities.nltk_re`: Extracting companies
============

The :mod:`lexnlp.extract.en.entities.nltk_re` module contains methods that allow for the extraction
of company names from text.  Example statements that are covered by default in this module include:

 * Deutsche Bank Securities Inc.
 * ACME, INC.
 * Wells Fargo Bank Minnesota, National Association
 * Lexpredict LLC

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/en/tests/test_entities.nltk_re


.. currentmodule:: lexnlp.extract.en.entities.nltk_re


Extracting conditions
----------------
.. autofunction:: get_companies

Example ::

    >>> import lexnlp.extract.en.entities.nltk_re

    >>> text = "This is Deutsche Bank Securities Inc."
    >>> print(list(lexnlp.extract.en.entities.nltk_re.get_entities.nltk_re.get_companies(text)))
    [('This is Deutsche Bank Securities', 'Inc', 'Bank')]

    >>> text = "This is Lexpredict LLC"
    >>> print(list(lexnlp.extract.en.entities.nltk_re.get_entities.nltk_re(text)))
    [('This is Lexpredict', 'LLC', None)]

