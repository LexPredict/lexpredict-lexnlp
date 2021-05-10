.. _extract_en_cusip:

============
:mod:`lexnlp.extract.en.cusip`: Extracting CUSIP
============

The :mod:`lexnlp.extract.en.cusip` module contains methods that allow for the extraction
of CUSIP code from text.  Example statements that are covered by default in this module include:

 * 837649128
 * 392690QT3
 * 39298#QT5
 * 12F123454

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/lexnlp/extract/en/tests/test_cusip


.. currentmodule:: lexnlp.extract.en.cusip


Extracting conditions
----------------
.. autofunction:: get_cusip_list

Example ::

    >>> import lexnlp.extract.en.cusip
    >>> text = "This is 39298#QT5 code"
    >>> print(lexnlp.extract.en.cusip.get_cusip(text))
    [{'location_start': 8,
      'location_end': 17,
      'text': '39298#QT5',
      'issuer_id': '39298#',
      'issue_id': 'QT',
      'checksum': 5,
      'ppn': True,
      'tba': None,
      'internal': False}]

    >>> text = "This is TBA 12F123454 code"
    >>> print(lexnlp.extract.en.cusip.get_cusip(text))
    [{'location_start': 12,
      'location_end': 21,
      'text': '12F123454',
      'issuer_id': '12F123',
      'issue_id': '45',
      'checksum': 4,
      'internal': False,
      'tba': {'product_code': '12',
              'mortgage_type': 'F',
              'coupon': '123',
              'maturity': '4',
              'settlement_month': '5',
              'checksum': '4',
              'settlement_month_name': 'May'},
      'ppn': False}]

