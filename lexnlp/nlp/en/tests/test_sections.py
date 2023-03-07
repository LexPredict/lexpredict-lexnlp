#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Section segmentation unit tests for English.

This module implements unit tests for the section segmentation code in English.

Todo:
    * More pathological and difficult cases
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os

# Project imports
from nose.tools import assert_equal
from unittest import TestCase

from lexnlp import get_module_path
from lexnlp.nlp.en.segments.sections import get_sections, get_section_spans, DocumentSection, find_section_titles
from lexnlp.nlp.en.segments.sentences import get_sentence_span_list
from lexnlp.tests import lexnlp_tests


class TestSectionSpans(TestCase):

    @staticmethod
    def get_text(path):
        base_path = get_module_path()
        with open(os.path.join(base_path, "../test_data", path), "rb") as f:
            return f.read().decode("utf-8")

    def test_file_1(self):
        text = self.get_text('1582586_2015-08-31')
        sections = list(lexnlp_tests.benchmark('get_sections(text)', get_sections, text))
        num_sections = len(sections)
        assert_equal(num_sections, 23)

    def test_file_2(self):
        text = self.get_text('1031296_2004-11-04')
        sections = list(lexnlp_tests.benchmark('get_sections(text)', get_sections, text))
        num_sections = len(sections)
        assert_equal(num_sections, 11)

    def test_file_3(self):
        text = self.get_text('1100644_2016-11-21')
        sections = list(lexnlp_tests.benchmark('get_sections(text)', get_sections, text))
        num_sections = len(sections)
        assert_equal(num_sections, 72)

    def test_file_4_use_ml(self):
        text = self.get_text('test_get_section_spans_1.txt')

        # test all sections
        sections = list(get_section_spans(text))
        print(f'{len(sections)} sections are found')
        for s in sections:
            print(f'Section #{s.start}, "{s.title}"')
        self.assertEqual(len(sections), 207)

        # test only sections with titles
        sections = list(get_section_spans(text, skip_empty_headers=True))
        self.assertEqual(len([i for i in sections if i.title is None]), 0)

        self.assertEqual(
            sections[1],
            DocumentSection(
                start=2280,
                end=2340,
                title='SECTION 2',
                title_start=2280,
                title_end=2289,
                level=1,
                abs_level=3,
                text='SECTION 2.  Letters of Credit........................... 15\n'))

    def test_file_4_use_regex(self):
        text = self.get_text('test_get_section_spans_1.txt')

        # test all sections
        sections = list(get_section_spans(text, use_ml=False))
        self.assertEqual(len(sections), 554)

        self.assertEqual(
            sections[2],
            DocumentSection(
                start=1378,
                end=1438,
                title='SECTION 1',
                title_start=1378,
                title_end=1387,
                level=2,
                abs_level=3,
                text='SECTION 1.  Amount and Terms of Credit..................  1\n'))

    def test_bad_text(self):
        text = 'text'
        sections = list(get_section_spans(text))
        self.assertEqual(sections, [])

    def test_title_start_end(self):
        text = self.get_text('lexnlp/nlp/en/tests/test_sections/skewed_document.txt')
        sentence_spans = get_sentence_span_list(text)
        sections = list(get_section_spans(
            text, use_ml=False, return_text=False, skip_empty_headers=True))
        self.assertGreater(len(sections), 3)
        # test title coordinates before enhancing titles ...
        for sect in sections:
            title = text[sect.title_start: sect.title_end]
            self.assertEqual(sect.title, title)

        # ... and after enhancing
        find_section_titles(sections, sentence_spans, text)
        for sect in sections:
            title = text[sect.title_start: sect.title_end]
            self.assertEqual(sect.title, title)
