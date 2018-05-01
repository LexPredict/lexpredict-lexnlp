#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Section segmentation unit tests for English.

This module implements unit tests for the section segmentation code in English.

Todo:
    * More pathological and difficult cases
"""

# Imports
import os

# Project imports
from nose.tools import assert_equal

from lexnlp import get_module_path
from lexnlp.nlp.en.segments.sections import get_sections
from lexnlp.tests import lexnlp_tests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_file_1():
    """
    Test using sample file #1.
    :return:
    """
    # Open file
    base_path = get_module_path()

    with open(os.path.join(base_path, "../test_data", "1582586_2015-08-31")) as test_file_handle:
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
