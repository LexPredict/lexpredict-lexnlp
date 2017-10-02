"""Sentence segmentation for English.

This module implements sentence segmentation in English using simple
machine learning classifiers.

Todo:
  * Standardize model (re-)generation
"""

# Imports
import os

# Packages
from sklearn.externals import joblib

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Setup module path
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
SENTENCE_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./sentence_segmenter.pickle"))


def get_sentences(text):
    """
    Get sentences from text.
    :param text:
    :return:
    """
    return SENTENCE_SEGMENTER_MODEL.tokenize(text)
