#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Import and set false
from nose import with_setup

# Test Stanford import
from lexnlp import disable_stanford, enable_stanford
from lexnlp.nlp.en.stanford import get_tokens

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def setup_module():
    """
    Setup environment pre-tests
    :return:
    """
    disable_stanford()


def teardown_module():
    """
    Setup environment post-tests.
    :return:
    """
    enable_stanford()


@with_setup(setup_module, teardown_module)
def test_stanford_method():
    """
    Ensure method fails.
    :return:
    """
    try:
        _ = get_tokens("This should throw an exception.")
        assert False
    except RuntimeError:
        assert True
