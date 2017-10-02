"""Extraction utilities for English.
"""
# Imports
import unicodedata

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Default punctuation to whitelist
VALID_PUNCTUATION = [".", ",", "'", "-", "&"]


def strip_unicode_punctuation(text, valid_punctuation=None):
    """
    This method strips all unicode punctuation that is not whitelisted.
    :param text: text to strip
    :param valid_punctuation: valid punctuation to whitelist
    :return:
    """
    if valid_punctuation is None:
        valid_punctuation = VALID_PUNCTUATION

    return "".join(c for c in text if (c in valid_punctuation) or not unicodedata.category(c).startswith("P"))
