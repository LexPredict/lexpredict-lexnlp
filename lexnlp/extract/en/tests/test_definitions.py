#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Definition unit tests for English.

This module implements unit tests for the definition extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Project imports
from lexnlp.extract.en.definitions import get_definitions
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_definition_fixed():
    lexnlp_tests.test_extraction_func_on_test_data(get_definitions)
