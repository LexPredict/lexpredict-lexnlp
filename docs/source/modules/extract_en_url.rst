.. _extract_en_urls:

============
:mod:`lexnlp.extract.en.url`: Extracting URLs
============

The :mod:`lexnlp.extract.en.urls` module contains methods that allow for the extraction
of URLs from text.

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_urls

.. currentmodule:: lexnlp.extract.en.urls

Extracting constraints
----------------
.. autofunction:: get_urls

Example ::

    >>> import lexnlp.extract.en.urls
    >>> text = "A copy of the terms can be found at www.acme.com/terms"
    >>> print(list(lexnlp.extract.en.urls.get_urls(text)))
    ['www.acme.com/terms']
