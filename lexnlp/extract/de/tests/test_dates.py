#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Unit tests for Dates.
"""

import datetime
from unittest import TestCase

from typing import List

from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.de.dates import get_date_list, get_date_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestDeDatesPlain(TestCase):

    def test_dates(self):
        text = """
        Ausfertigungsdatum: 23.05.1975 Vollzitat: \
        "Gesetz über vermögenswirksame Leistungen für Beamte, Richter, Berufssoldaten und \
        Soldaten auf Zeit in der Fassung der Bekanntmachung vom 16. Mai 2002 (BGBl. I S. 1778), \
        das zuletzt durch Artikel 39 des Gesetzes vom 29. März 2017 (BGBl. I S. 626) geändert worden ist" \
        Stand:        Neugefasst durch Bek. v. 16.5.2002 I 1778; \
        zuletzt geändert durch Art. 39 G v. 29.3.2017 I 626""".strip()

        ds = get_date_list(text=text, language='de')
        self.assertEqual(5, len(ds))
        ds.sort(key=lambda d:d['location_start'])

        self.assertEqual((20, 30), (ds[0]['location_start'], ds[0]['location_end']))
        self.assertEqual((196, 208), (ds[1]['location_start'], ds[1]['location_end']))
        self.assertEqual((282, 295), (ds[2]['location_start'], ds[2]['location_end']))
        self.assertEqual((381, 390), (ds[3]['location_start'], ds[3]['location_end']))
        self.assertEqual((443, 452), (ds[4]['location_start'], ds[4]['location_end']))

        self.assertEqual(datetime.datetime(1975, 5, 23, 0, 0), ds[0]['value'])
        self.assertEqual(datetime.datetime(2002, 5, 16, 0, 0), ds[1]['value'])
        self.assertEqual(datetime.datetime(2017, 3, 29, 0, 0), ds[2]['value'])
        self.assertEqual(datetime.datetime(2002, 5, 16, 0, 0), ds[3]['value'])
        self.assertEqual(datetime.datetime(2017, 3, 29, 0, 0), ds[4]['value'])

        self.assertEqual('23.05.1975', ds[0]['source'])
        self.assertEqual('16. Mai 2002', ds[1]['source'])
        self.assertEqual('29. März 2017', ds[2]['source'])
        self.assertEqual('16.5.2002', ds[3]['source'])
        self.assertEqual('29.3.2017', ds[4]['source'])

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_dates_ordered,
            'lexnlp/typed_annotations/de/date/dates.txt',
            DateAnnotation)


def get_dates_ordered(text: str) -> List[DateAnnotation]:
    dates = list(get_date_annotations(text))
    dates.sort(key=lambda d: d.coords[0])
    return dates
