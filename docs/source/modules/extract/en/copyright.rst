.. _extract_en_copyright:

============
:mod:`lexnlp.extract.en.copyright`: Extracting copyright references
============

The :mod:`lexnlp.extract.en.copyright` module contains methods that allow for the extraction
of copyright references from text.


The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_copyright


.. currentmodule:: lexnlp.extract.en.copyright


Extracting copyrights
----------------
.. autofunction:: get_copyright

Example ::

    >>> import lexnlp.extract.en.copyright
    >>> text = "(C) Copyright 1993-1996 Hughes Information Systems Company"
    >>> print(list(lexnlp.extract.en.copyright.get_copyright(text)))
    [('Copyright', '1993-1996', 'Hughes Information Systems Company')]

    >>> text = "Test copyrigh symbol © 2017, SIGN LLC"
    >>> print(list(lexnlp.extract.en.conditions.get_conditions(text)))
    print(list(lexnlp.extract.en.copyright.get_copyright(text)))
    [('©', '2017', 'SIGN LLC')]

