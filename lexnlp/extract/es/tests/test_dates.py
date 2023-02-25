#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Multi-language unit tests for Dates.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
from unittest import TestCase
from functools import partial

from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.es.dates import get_date_annotations
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestParseEsDates(TestCase):
    def test_es_dates(self):
        text = "Some dummy sample with Spanish date like 15 de febrero, " + \
               "28 de abril y 17 de noviembre de 1995, 1ºde enero de 1999 "
        ants = list(get_date_annotations(text=text, strict=False))
        self.assertEqual(4, len(ants))
        ants.sort(key=lambda ant: ant.coords[0])
        self.assertEqual(4, len(ants))

        a = ants[0]
        self.assertEqual((41, 54), a.coords)
        self.assertEqual(datetime.datetime(1995, 2, 15, 0, 0), a.date)
        self.assertEqual('15 de febrero', a.text)

        a = ants[1]
        self.assertEqual((56, 67), a.coords)
        self.assertEqual(datetime.datetime(1995, 4, 28, 0, 0), a.date)
        self.assertEqual('28 de abril', a.text)

        a = ants[2]
        self.assertEqual((70, 93), a.coords)
        self.assertEqual(datetime.datetime(1995, 11, 17, 0, 0), a.date)
        self.assertEqual('17 de noviembre de 1995', a.text)

        a = ants[3]
        self.assertEqual((95, 113), a.coords)
        self.assertEqual(datetime.datetime(1999, 1, 1, 0, 0), a.date)
        self.assertEqual('1ºde enero de 1999', a.text)

    def test_more_dates(self):
        text = "Some dummy sample with Spanish date like 15 de febrero, 28 " +\
               "de abril y 17 de noviembre de 1995, 1ºde enero de 1999 "
        ants = list(get_date_annotations(text=text, strict=False))
        self.assertEqual(4, len(ants))
        ants.sort(key=lambda ant: ant.coords[0])

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
            partial(get_date_annotations, strict=False),
            'lexnlp/typed_annotations/es/date/dates.txt',
            DateAnnotation)
