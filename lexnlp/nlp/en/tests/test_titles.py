#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import requests
from nose.tools import assert_list_equal

from lexnlp import get_module_path
from lexnlp.nlp.en.segments.titles import get_titles

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_title_1():
    """
    Test first example title.
    :return:
    """
    # Setup URL
    url = "https://raw.githubusercontent.com/LexPredict/lexpredict-contraxsuite-samples/master/agreements/" + \
          "construction/1000694_2002-03-15_AGREEMENT%20OF%20LEASE-W.M.RICKMAN%20CONSTRUCTION%20CO..txt"

    # Download file
    file_text = requests.get(url).text

    assert_list_equal(list(get_titles(file_text)),
                      ["LEASE AGREEMENT"])


def test_title_2():
    """
    Test second example title.
    :return:
    """
    # Open file
    test_file_path = os.path.join(get_module_path(), "..", "test_data", "1100644_2016-11-21")
    with open(test_file_path, "rb") as file_handle:
        # Read and parse
        file_text = file_handle.read().decode("utf-8")
        assert_list_equal(list(get_titles(file_text)),
                          ["VALIDIAN SOFTWARE LICENSE AGREEMENT"])
