.. _extract_en_copyright:

===================================================================
:mod:`lexnlp.extract.en.copyright`: Extracting copyright references
===================================================================

The :mod:`lexnlp.extract.en.copyright` module extracts copyright statements
and can optionally retain their source text.

.. currentmodule:: lexnlp.extract.en.copyright

Extracting copyright references
-------------------------------

.. autofunction:: get_copyrights

.. code-block:: python

   from lexnlp.extract.en.copyright import get_copyrights

   notices = list(
       get_copyrights(
           "(C) Copyright 1993-1996 Hughes Information Systems Company"
       )
   )
