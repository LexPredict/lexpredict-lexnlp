#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Definition unit tests for English.

This module implements unit tests for the definition extraction functionality in English.

Todo:
    * Better testing for exact test in return sources
    * More pathological and difficult cases
"""

# Project imports
from lexnlp.extract.en.definitions import get_definitions, get_definitions_in_sentence
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_definition_fixed():
    lexnlp_tests.test_extraction_func_on_test_data(get_definitions)


def test_definition_in_sentences():
    lexnlp_tests.test_extraction_func_on_test_data(get_definitions_in_sentence)


def test_definitions_simple():
    sentence = '''Visual Networks Operations, Inc., a Delaware corporation with offices at 2092 Gaither 
                             Road, Rockville, Maryland 20850("Licensor.") and is made retroactive to December 3, 2002 
                             ("Effective Date").'''
    definitions = list(get_definitions(sentence))
    print(definitions)
