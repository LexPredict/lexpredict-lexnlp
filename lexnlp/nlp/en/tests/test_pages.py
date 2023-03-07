#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from unittest import TestCase

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.nlp.en.segments.pages import get_pages
from lexnlp.tests import lexnlp_tests


class TestPages(TestCase):
    TEST_PATH = os.path.join(lexnlp_test_path, 'lexnlp/nlp/en/tests/test_pages/')

    def test_page_examples(self):
        file_path = os.path.join(self.TEST_PATH, 'test_page_examples.csv')
        for (_i, text, _input_args, expected) in lexnlp_tests.iter_test_data_text_and_tuple(
                file_name=file_path):
            def remove_blankspace(r):
                return r.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

            # Get list of pages
            page_list = list(lexnlp_tests.benchmark_extraction_func(get_pages, text))
            assert len(page_list) == len(expected)
            clean_result = [remove_blankspace(p) for p in expected]
            for page in page_list:
                assert remove_blankspace(page) in clean_result
