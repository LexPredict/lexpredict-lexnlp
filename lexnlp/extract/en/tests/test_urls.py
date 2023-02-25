#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Urls unit tests for English.

This module implements unit tests for the urls extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# Project imports
from lexnlp.extract.en.urls import get_urls
from lexnlp.tests import lexnlp_tests


def test_urls():
    lexnlp_tests.test_extraction_func_on_test_data(get_urls)
