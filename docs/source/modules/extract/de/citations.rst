.. _extract_de_citations:

============
:mod:`lexnlp.extract.de.citations`: Extracting citations
============

The :mod:`lexnlp.extract.de.citations` module contains methods that allow for the extraction
of "BGBl" citations from text.  Sample citations that are covered by this module include:

 * BGBl. I S. 434
 * Artikel 2 des Gesetzes vom 20. Juli 2017 (BGBl. I S. 2789)
 * vom 2. Januar 2002 (BGBl. I S. 42, 2909; 2003 I S. 738)
 * Artikel 2 Absatz 1 Satz 1 Nr. 1 bis 3 Buchstabe b und c des Gesetzes v. 2. Januar 2002, BGBl. I S. 2477

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/de/tests/test_citations


.. currentmodule:: lexnlp.extract.de.citations

Extracting citations
----------------
.. autofunction:: get_citation_list

Example ::

    >>> import lexnlp.extract.de.citations
    >>> text = " vom 15. Mai 2007 (BGBl. I S. 733 (1967)), die ."
    >>> print(lexnlp.extract.de.citations.get_citation_list(text))
    [{'location_start': 0,
      'location_end': 41,
      'text': ' vom 15. Mai 2007 (BGBl. I S. 733 (1967))',
      'article': '',
      'number': '',
      'subparagraph': '',
      'sentence': '',
      'paragraph': '',
      'letter': '',
      'date': '15. Mai 2007',
      'part': 'I',
      'page': '733',
      'year': '1967'}]

