#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Multi-language unit tests for Dates.
"""

# Project imports
import datetime
from lexnlp.extract.es.dates import get_date_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _sort(v):
    return sorted(v, key=lambda i: i['location_start'])


def test_en_dates():
    text = """Some dummy sample with Spanish date like 15 de febrero, 28 de abril y 17 de noviembre de 1995, 1ºde enero de 1999 """
    extracted_dates = _sort(get_date_list(text=text, language='es'))
    expected_dates = _sort([{'location_start': 41,
                             'location_end': 54,
                             'value': datetime.datetime(1995, 2, 15, 0, 0),
                             'source': '15 de febrero'},
                            {'location_start': 70,
                             'location_end': 93,
                             'value': datetime.datetime(1995, 11, 17, 0, 0),
                             'source': '17 de noviembre de 1995'},
                            {'location_start': 56,
                             'location_end': 67,
                             'value': datetime.datetime(1995, 4, 28, 0, 0),
                             'source': '28 de abril'},
                            {'location_start': 95,
                             'location_end': 113,
                             'value': datetime.datetime(1999, 1, 1, 0, 0),
                             'source': '1ºde enero de 1999'}])
    assert extracted_dates == expected_dates
