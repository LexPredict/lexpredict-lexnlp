#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Multi-language unit tests for Dates.
"""

import datetime
from lexnlp.extract.common.dates import get_date_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _sort(v):
    return sorted(v, key=lambda i: i['location_start'])


def test_en_dates():
    text = "Some date like February 26, 2018 and this one 10-11-2017"
    extracted_dates = _sort(get_date_list(text=text, language='en'))
    expected_dates = _sort([{'location_start': 46,
                             'location_end': 56,
                             'value': datetime.datetime(2017, 10, 11, 0, 0),
                             'source': '10-11-2017'},
                            {'location_start': 15,
                             'location_end': 36,
                             'value': datetime.datetime(2018, 2, 26, 0, 0),
                             'source': 'February 26, 2018 and'}])
    assert extracted_dates == expected_dates


def test_de_dates():
    text = """
Ausfertigungsdatum: 23.05.1975 Vollzitat: \
"Gesetz über vermögenswirksame Leistungen für Beamte, Richter, Berufssoldaten und \
Soldaten auf Zeit in der Fassung der Bekanntmachung vom 16. Mai 2002 (BGBl. I S. 1778), \
das zuletzt durch Artikel 39 des Gesetzes vom 29. März 2017 (BGBl. I S. 626) geändert worden ist" \
Stand:        Neugefasst durch Bek. v. 16.5.2002 I 1778; \
zuletzt geändert durch Art. 39 G v. 29.3.2017 I 626"""

    extracted_dates = _sort(get_date_list(text=text, language='de'))
    expected_dates = _sort([{'location_start': 21,
                             'location_end': 31,
                             'value': datetime.datetime(1975, 5, 23, 0, 0),
                             'source': '23.05.1975'},
                            {'location_start': 181,
                             'location_end': 193,
                             'value': datetime.datetime(2002, 5, 16, 0, 0),
                             'source': '16. Mai 2002'},
                            {'location_start': 259,
                             'location_end': 272,
                             'value': datetime.datetime(2017, 3, 29, 0, 0),
                             'source': '29. März 2017'},
                            {'location_start': 350,
                             'location_end': 359,
                             'value': datetime.datetime(2002, 5, 16, 0, 0),
                             'source': '16.5.2002'},
                            {'location_start': 404,
                             'location_end': 413,
                             'value': datetime.datetime(2017, 3, 29, 0, 0),
                             'source': '29.3.2017'}])
    assert extracted_dates == expected_dates
