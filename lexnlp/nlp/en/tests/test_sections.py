#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Section segmentation unit tests for English.

This module implements unit tests for the section segmentation code in English.

Todo:
    * More pathological and difficult cases
"""

# Imports
import os
import codecs

# Project imports
from nose.tools import assert_equal
from unittest import TestCase

from lexnlp import get_module_path
from lexnlp.nlp.en.segments.sections import get_sections, get_section_spans
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_file_1():
    """
    Test using sample file #1.
    :return:
    """
    # Open file
    base_path = get_module_path()

    with codecs.open(os.path.join(base_path, "../test_data", "1582586_2015-08-31"), encoding='utf8') as test_file_handle:
        # Read buffer
        file_buffer = test_file_handle.read()

        # Parse and count
        sections = list(lexnlp_tests.benchmark('get_sections(file_buffer)', get_sections, file_buffer))
        num_sections = len(sections)

        assert_equal(num_sections, 23)


def test_file_2():
    """
    Test using sample file #2.
    :return:
    """
    # Open file
    base_path = get_module_path()

    with open(os.path.join(base_path, "../test_data", "1031296_2004-11-04"), "rb") as test_file_handle:
        # Read buffer
        file_buffer = test_file_handle.read().decode("utf-8")

        # Parse and count
        sections = list(lexnlp_tests.benchmark('get_sections(file_buffer)', get_sections, file_buffer))
        num_sections = len(sections)

        assert_equal(num_sections, 11)


def test_file_3():
    """
    Test using sample file #2.
    :return:
    """
    # Open file
    base_path = get_module_path()

    with open(os.path.join(base_path, "../test_data", "1100644_2016-11-21"), "rb") as test_file_handle:
        # Read buffer
        file_buffer = test_file_handle.read().decode("utf-8")

        # Parse and count
        sections = list(lexnlp_tests.benchmark('get_sections(file_buffer)', get_sections, file_buffer))
        num_sections = len(sections)

        assert_equal(num_sections, 72)


class TestSectionSpans(TestCase):

    @staticmethod
    def get_text(path):
        base_path = get_module_path()
        with open(os.path.join(base_path, "../test_data", path), "rb") as f:
            return f.read().decode("utf-8")

    def test_file_4_use_ml(self):
        text = self.get_text('test_get_section_spans_1.txt')

        # test all sections
        sections = list(get_section_spans(text))
        self.assertEqual(len(sections), 207)

        # test only sections with titles
        sections = list(get_section_spans(text, skip_empty_headers=True))
        self.assertEqual(len([i for i in sections if i['title'] is None]), 0)

        self.assertDictEqual(
            sections[1],
            {'start': 2280,
             'end': 2340,
             'title': 'SECTION 2',
             'title_start': 2280,
             'title_end': 2289,
             'level': 1,
             'abs_level': 3,
             'text': 'SECTION 2.  Letters of Credit........................... 15\n'})

    def test_file_4_use_regex(self):
        text = self.get_text('test_get_section_spans_1.txt')

        # test all sections
        sections = list(get_section_spans(text, use_ml=False))
        self.assertEqual(len(sections), 554)

        self.assertDictEqual(
            sections[2],
            {'start': 1378,
             'end': 1438,
             'title': 'SECTION 1',
             'title_start': 1378,
             'title_end': 1387,
             'level': 2,
             'abs_level': 3,
             'text': 'SECTION 1.  Amount and Terms of Credit..................  1\n'})

    def test_bad_text(self):
        text = 'text'
        sections = list(get_section_spans(text))
        self.assertEqual(sections, [])
