#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Multi-language unit tests for Dates.
"""

# Project imports
import datetime
from unittest import TestCase

from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.es.dates import get_date_list, get_date_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def _sort(v):
    return sorted(v, key=lambda i: i['location_start'])


class TestParseEsDates(TestCase):
    def test_es_dates(self):
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
        self.assertEqual(expected_dates, extracted_dates)

        ants = list(get_date_annotations(text=text, language='es'))
        self.assertEqual(4, len(ants))

    def test_annotations(self):
        text = "Some dummy sample with Spanish date like 15 de febrero, 28 " +\
               "de abril y 17 de noviembre de 1995, 1ºde enero de 1999 "
        ants = list(get_date_annotations(text=text, language='es'))
        self.assertEqual(4, len(ants))
        ants.sort(key=lambda d:d.coords[0])

        self.assertEqual((41, 54), ants[0].coords)
        self.assertEqual((56, 67), ants[1].coords)
        self.assertEqual((70, 93), ants[2].coords)
        self.assertEqual((95, 113), ants[3].coords)

        self.assertEqual(datetime.datetime(1995, 2, 15, 0, 0), ants[0].date)
        self.assertEqual(datetime.datetime(1995, 4, 28, 0, 0), ants[1].date)
        self.assertEqual(datetime.datetime(1995, 11, 17, 0, 0), ants[2].date)
        self.assertEqual(datetime.datetime(1999, 1, 1, 0, 0), ants[3].date)

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_date_annotations,
            'lexnlp/typed_annotations/es/date/dates.txt',
            DateAnnotation)
