#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Unit tests for Dates.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
from unittest import TestCase

from typing import List

import pytest

from lexnlp.extract.all_locales.languages import Locale
from lexnlp.extract.common.annotations.date_annotation import DateAnnotation
from lexnlp.extract.de.dates import get_date_list, get_date_annotations, parser
from lexnlp.extract.de.dates_de_classifier import train_default_model
from lexnlp.tests.typed_annotations_tests import TypedAnnotationsTester


class TestDeDatesPlain(TestCase):
    def test_de_general_check(self):
        self.assertTrue(parser.passed_general_check('der vierte Juli', datetime.date(2021, 8, 4)))
        self.assertFalse(parser.passed_general_check('der wierte Juli', datetime.date(2021, 8, 4)))
        self.assertFalse(parser.passed_general_check('der vierte Guli', datetime.date(2021, 8, 4)))

        self.assertFalse(parser.passed_general_check('21/2011', datetime.date(2011, 1, 21)))
        self.assertTrue(parser.passed_general_check('11/2011', datetime.date(2011, 11, 1)))

    def test_dates(self):
        text = """
        Ausfertigungsdatum: 23.05.1975 Vollzitat: \
        "Gesetz über vermögenswirksame Leistungen für Beamte, Richter, Berufssoldaten und \
        Soldaten auf Zeit in der Fassung der Bekanntmachung vom 16. Mai 2002 (BGBl. I S. 1778), \
        das zuletzt durch Artikel 39 des Gesetzes vom 29. März 2017 (BGBl. I S. 626) geändert worden ist" \
        Stand:        Neugefasst durch Bek. v. 16.5.2002 I 1778; \
        zuletzt geändert durch Art. 39 G v. 29.3.2017 I 626""".strip()

        ds = get_date_list(text=text, locale=Locale('de'))
        self.assertEqual(5, len(ds))
        ds.sort(key=lambda d: d['location_start'])

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

    def test_date_reverse_order(self):
        text = 'Commencement Date: 09/12/2022.'
        dates = list(get_date_annotations(text))
        self.assertEqual(1, len(dates))
        self.assertEqual(12, dates[0].date.month)

    def test_de_dates(self):
        text = """Ausfertigungsdatum: 23.05.1975 Vollzitat:
                "Gesetz über vermögenswirksame Leistungen für Beamte, Richter, Berufssoldaten und
                Soldaten auf Zeit in der Fassung der Bekanntmachung vom 16. Mai 2002 (BGBl. I S. 1778),
                das zuletzt durch Artikel 39 des Gesetzes vom 29. März 2017 (BGBl. I S. 626) geändert worden ist"
                Stand:        Neugefasst durch Bek. v. 16.5.2002 I 1778;
                zuletzt geändert durch Art. 39 G v. 29.3.2017 I 626"""

        extracted_dates = list(get_date_annotations(text=text, locale=Locale('de')))
        extracted_dates.sort(key=lambda a: a.coords[0])
        for d in extracted_dates:
            d.text = text[d.coords[0]: d.coords[1]].strip()
        expected_values = [
            (20, 30, datetime.datetime(1975, 5, 23), '23.05.1975'),
            (212, 224, datetime.datetime(2002, 5, 16), '16. Mai 2002'),
            (306, 319, datetime.datetime(2017, 3, 29), '29. März 2017'),
            (413, 422, datetime.datetime(2002, 5, 16), '16.5.2002'),
            (483, 492, datetime.datetime(2017, 3, 29), '29.3.2017')
        ]

        self.assertEqual(len(expected_values), len(extracted_dates))
        for i in range(len(expected_values)):
            act = extracted_dates[i]
            exp = expected_values[i]
            self.assertEqual((exp[0], exp[1]), act.coords)
            self.assertEqual(exp[2], act.date)

    def test_numeral(self):
        text = 'der vierte Juli'
        dates = list(get_date_annotations(text))
        # TODO: get a better date parser that can convert numerals to numbers
        self.assertEqual(0, len(dates))

    def test_negative(self):
        text = '''Leasing ohne Anzahlung: Monatliche Rate 300€, Laufzeit 36 Monaten, Gesamtkosten
        10.800€
        Leasing mit 2.500€ Anzahlung: Monatliche Rate 230,55€, Laufzeit 36 Monate,
        Gesamtkosten 10.800€
        Durch eine Sonderzahlung wird die monatliche Belastung gesenkt, das Risiko für
        den Leasinggeber sinkt.'''
        dates = list(get_date_annotations(text))
        for d in dates:
            d.text = text[d.coords[0]: d.coords[1]]

        self.assertEqual(0, len(dates))

    def test_negative_jahr(self):
        text = '''Der Vertrag beginnt mit dem Moment zu laufen, in dem der Vermieter / Mieter seine 
        Unterschriften darauf gemacht hat. Wenn die Mietdauer mehr als 1 Jahr beträgt, ist eine staatliche 
        Registrierung des Vertrags erforderlich.'''
        dates = list(get_date_annotations(text))
        for d in dates:
            d.text = text[d.coords[0]: d.coords[1]]
        self.assertEqual(0, len(dates))

    def test_point_inside(self):
        text = '''- Definitiver Leasing-Entscheid innert 24 Stunden 5. Oktober 2011.'''
        dates = list(get_date_annotations(text))
        self.assertEqual(1, len(dates))
        self.assertEqual(datetime.datetime(2011, 10, 5, 0, 0), dates[0].date)

    def test_point_inside_with_two_dates(self):
        text = '''zu den Übereinkommen vom 15. Februar 1972 und 29. Dezember 1972 zur'''
        dates = list(get_date_annotations(text))
        self.assertEqual(2, len(dates))
        self.assertEqual(datetime.datetime(1972, 2, 15, 0, 0), dates[0].date)
        self.assertEqual(datetime.datetime(1972, 12, 29, 0, 0), dates[1].date)

    def test_negative_stunden(self):
        text = '''- Definitiver Leasing-Entscheid innert 24 Stunden 5.'''
        dates = list(get_date_annotations(text))
        for d in dates:
            d.text = text[d.coords[0]: d.coords[1]]
        self.assertEqual(0, len(dates))

    def test_written_number(self):
        # TODO: our De parser presently can't read numerals
        text = '''am vierzehnten Juli'''
        dates = list(get_date_annotations(text))
        self.assertEqual(0, len(dates))

    def test_file_samples(self):
        tester = TypedAnnotationsTester()
        tester.test_and_raise_errors(
            get_dates_ordered,
            'lexnlp/typed_annotations/de/date/dates.txt',
            DateAnnotation)

    @pytest.mark.serial
    def debug_test_train_classifier(self):
        train_default_model(save=True, verbose=False, check_date_strings=True)


def get_dates_ordered(text: str) -> List[DateAnnotation]:
    dates = list(get_date_annotations(text))
    dates.sort(key=lambda d: d.coords[0])
    return dates
