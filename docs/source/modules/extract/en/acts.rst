.. _extract_en_acts:

============
:mod:`lexnlp.extract.en.acts`: Extracting acts
============

The :mod:`lexnlp.extract.en.acts` module contains methods that allow for the extraction
of acts from text.  Sample acts that are covered by this module include:

 * Advancing Hope Act
 * AGOA Acceleration Act of 2004
 * section 12 of the Agricultural Act of 1954
 * sections 751(a)(1) and 777(i)(1) of the Act

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/en/tests/test_acts.py

.. currentmodule:: lexnlp.extract.en.acts

Extracting acts
----------------
.. autofunction:: get_act_list

Example ::

    >>> import lexnlp.extract.en.acts
    >>> text = "test section 12 of the VERY Important Act of 1954."
    >>> print(lexnlp.extract.en.acts.get_act_list(text))
    [{'location_start': 5,
      'location_end': 49,
      'section': '12',
      'year': '1954',
      'ambiguous': False,
      'act_name': 'VERY Important Act',
      'value': 'section 12 of the VERY Important Act of 1954'}]

    >>> import lexnlp.extract.en.acts
    >>> text = "accordance with sections 751(a)(1) and 777(i)(1) of the Act, and 19 CFR 351"
    >>> print(lexnlp.extract.en.acts.get_act_list(text))
    [{'location_start': 16,
      'location_end': 61,
      'act_name': 'Act',
      'section': '751(a)(1) and 777(i)(1)',
      'year': '',
      'ambiguous': True,
      'value': 'sections 751(a)(1) and 777(i)(1) of the Act, '}]

