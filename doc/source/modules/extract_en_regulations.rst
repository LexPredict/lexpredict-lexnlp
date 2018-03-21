.. _extract_en_regulations:

============
:mod:`lexnlp.extract.en.regulations`: Extracting regulatory references
============

The :mod:`lexnlp.extract.en.regulations` module contains methods that allow for the extraction
of regulations references from text.  Examples include:

 * 55 CFR 77a-22B
 * 123 U.S.C § 456
 * Pub. L. 123-456


The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_regulations


.. currentmodule:: lexnlp.extract.en.regulations


Extracting constraints
----------------
.. autofunction:: get_regulations

Example ::

    >>> import lexnlp.extract.en.regulations
    >>> text = "Pursuant to 123 CFR 456, Provider shall"
    >>> print(list(lexnlp.extract.en.regulations.get_regulations(text)))
    [('Code of Federal Regulations', '123 CFR 456')]
    >>> text = "As enacted in Pub. L. 555-666"
    >>> print(list(lexnlp.extract.en.regulations.get_regulations(text)))
    [('no less than', 'the rate shall be', '')]



Customizing regulation extraction
----------------

.. note::
    The LexPredict Legal Dictionary repository contains a large number of additional regulatory citations
    and resources.  See, for example, the file below for a list of US State code citations, e.g., Ill. Comp. Stat.
    or 	Mo. Rev. Stat:
    https://github.com/LexPredict/lexpredict-legal-dictionary/blob/master/en/legal/us_state_code_citations.csv
