# pylint: disable=W0212

"""Sentence segmentation for English.

This module implements sentence segmentation in English using simple
machine learning classifiers.

Todo:
  * Standardize model (re-)generation
"""

# Imports
import os
import typing

# Packages
from nltk.tokenize.punkt import PunktTrainer, PunktSentenceTokenizer
from sklearn.externals import joblib

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Setup module path
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
SENTENCE_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./sentence_segmenter.pickle"))
extra_abbreviations = ['no', 'l']
SENTENCE_SEGMENTER_MODEL._params.abbrev_types.update(extra_abbreviations)


def get_sentence_list(text):
    """
    Get sentences from text.
    :param text:
    :return:
    """
    return SENTENCE_SEGMENTER_MODEL.tokenize(text)


def get_sentence_span_list(text) -> typing.List[typing.Tuple[int, int]]:
    """
    Given a text, returns a list of the (start, end) spans of sentences
    in the text.
    """
    return list(SENTENCE_SEGMENTER_MODEL.span_tokenize(text))


def build_sentence_model(text, extra_abbrevs=None):
    """
    Build a sentence model from text with optional
    extra abbreviations to include.
    :param text:
    :param extra_abbrevs:
    :return:
    """

    # Setup Punkt trainer
    punkt_trainer = PunktTrainer()
    punkt_trainer.train(text, verbose=False, finalize=False)
    punkt_trainer.finalize_training(verbose=False)

    # Extract parameters from trainer
    punkt_params = punkt_trainer.get_params()

    # Add any extras if passed
    if extra_abbrevs is not None:
        for abbrev in extra_abbrevs:
            punkt_params.abbrev_types.add(abbrev.strip(".").lower())

    # Return model instantiated with new parameters
    return PunktSentenceTokenizer(punkt_params)
