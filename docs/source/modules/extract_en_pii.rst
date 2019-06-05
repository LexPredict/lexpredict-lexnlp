.. _extract_en_pii:

============
:mod:`lexnlp.extract.en.pii`: Extracting personally-identifiable information (PII)
============

The :mod:`lexnlp.extract.en.pii` module contains methods that allow for the extraction
of personally identifying information from text.  Examples include:

 * phone numbers
 * US social security numbers
 * names

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_pii


.. currentmodule:: lexnlp.extract.en.pii


Extracting PII
----------------
.. autofunction:: get_pii

Example ::

    >>> import lexnlp.extract.en.pii
    >>> text = "John Doe (999-12-3456)"
    >>> print(list(lexnlp.extract.en.pii.get_pii(text)))
    [('ssn', '999-12-3456')]
    >>> text = "Mary Doe (212-123-4567)"
    >>> print(list(lexnlp.extract.en.pii.get_pii(text)))
    [('us_phone', '(212) 123-4567')]


.. autofunction:: get_ssns

.. autofunction:: get_us_phones
