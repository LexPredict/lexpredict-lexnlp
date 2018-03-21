.. _extract_en_geoentities:

============
:mod:`lexnlp.extract.en.geoentities`: Extracting geographic and geopolitical entities
============

The :mod:`lexnlp.extract.en.geoentities` module contains methods that allow for the extraction
of geopolitical or geographic references from text.

.. attention::
    The methods in this module rely heavily on data from the LexPredict Legal Dictionary repository:
    https://github.com/LexPredict/lexpredict-legal-dictionary

    This data is governed by a separate Creative Commons Attribution Share Alike 4.0 license here:
    https://github.com/LexPredict/lexpredict-legal-dictionary/blob/master/LICENSE


The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_geoentities


.. currentmodule:: lexnlp.extract.en.geoentities


Extracting courts
----------------
.. autofunction:: get_geoentities

.. note::
    For examples of loading and using entities from the LexPredict Legal Dictionary repository,
    please refer to this source code examples here:
    https://github.com/LexPredict/lexpredict-lexnlp/blob/master/lexnlp/extract/en/tests/test_geoentities.py