.. _extract_en_citations:

============
:mod:`lexnlp.extract.en.citations`: Extracting citations
============

The :mod:`lexnlp.extract.en.citations` module contains methods that allow for the extraction
of citations from text.  Sample citations that are covered by this module include:

 * 1 F.2d 1, 2-5 (1982)
 * 100 U.S. 25
 * 1 Wash. 1, 25 (1795)
 * 1988 S. Ct. 100

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_citations

.. note::

    This module relies heavily on the `reporters_db` Python package developed by the
    `Free Law Project <https://free.law/>`_.  For more information about the supported
    citation formats or for pull releases or bug reports related to this package,
    please see their GitHub page: https://github.com/freelawproject/reporters-db


.. currentmodule:: lexnlp.extract.en.citations

Extracting citations
----------------
.. autofunction:: get_citations

Example ::

    >>> import lexnlp.extract.en.citations
    >>> text = "Based on the precedent set in Doe v.  Acme, 100 F.2d 234 (1999)"
    >>> print(list(lexnlp.extract.en.citations.get_citations(text)))
    [(100, 'F.2d', 'Federal Reporter', 234, None, None, 1999)]

