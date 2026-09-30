.. _extract_en_companies:

===================================================================
:mod:`lexnlp.extract.en.entities.nltk_maxent`: Extracting companies
===================================================================

The :mod:`lexnlp.extract.en.entities.nltk_maxent` module extracts company names
using LexNLP's legal-domain entity detector and NLTK tokenization.

Representative inputs include:

* ``Deutsche Bank Securities Inc.``
* ``ACME, INC.``
* ``Wells Fargo Bank Minnesota, National Association``
* ``LexPredict LLC``

.. currentmodule:: lexnlp.extract.en.entities.nltk_maxent

Extracting companies
--------------------

.. autofunction:: get_companies

.. code-block:: python

   from lexnlp.extract.en.entities.nltk_maxent import get_companies

   companies = list(get_companies("This is LexPredict LLC."))
