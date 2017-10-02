"""Paragraph segmentation for English.

This module implements paragraph segmentation in English using simple
machine learning classifiers.

Todo:
  * Standardize model (re-)generation
"""

# Imports
import os
import string
import unicodedata

# Packages
import pandas
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
PARAGRAPH_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./paragraph_segmenter.pickle"))

# Setup standard paragraph break characters
PARAGRAPH_CHARACTERS = []
PARAGRAPH_CHARACTERS.extend(string.whitespace)
PARAGRAPH_CHARACTERS.extend(string.punctuation)


def build_paragraph_start_features(text, position, position_window_pre, position_window_post,
                                   characters=None):
    """
    Build a feature vector for a given line ID with given parameters.
    :param text:
    :param position:
    :param position_window_pre:
    :param position_window_post:
    :param characters:
    :return:
    """

    # Check characters
    if not characters:
        characters = PARAGRAPH_CHARACTERS

    # Feature vector
    feature_vector = {}

    # Check start offset
    if position < position_window_pre:
        position_window_pre = position

    # Iterate through window
    for i in range(-position_window_pre, position_window_post + 1):
        # Character
        try:
            pos_char = text[position + i]

            # Count characters
            feature_vector["char_is_alpha_{0}".format(i)] = 1 if unicodedata.category(pos_char).startswith("L") else 0
            feature_vector["char_is_number_{0}".format(i)] = 1 if unicodedata.category(pos_char).startswith("N") else 0
            feature_vector["char_is_punct_{0}".format(i)] = 1 if unicodedata.category(pos_char).startswith("P") else 0
            feature_vector["char_is_whitespace_{0}".format(i)] = 1 if unicodedata.category(pos_char).startswith(
                "Z") else 0

            # Build character vector
            for character in characters:
                feature_vector["char_{0}_{1}".format(character, i)] = 1 if pos_char == character else 0

        except IndexError:
            feature_vector["char_is_alpha_{0}".format(i)] = None
            feature_vector["char_is_number_{0}".format(i)] = None
            feature_vector["char_is_punct_{0}".format(i)] = None
            feature_vector["char_is_whitespace_{0}".format(i)] = None

            # Build character vector
            for character in characters:
                feature_vector["char_{0}_{1}".format(character, i)] = None

    # Build character vector
    for character in characters:
        feature_vector["char_{0}".format(character)] = 1 if text[position] == character else 0

    return feature_vector


def get_paragraphs(text, window_pre=5, window_post=5):
    """
    Get paragraphs from text.
    :param text:
    :param window_pre:
    :param window_post:
    :return:
    """
    # Model parameters
    test_feature_data = []
    for pos_id in range(len(text)):
        test_feature_data.append(build_paragraph_start_features(text, pos_id, window_pre, window_post))

    # Calculate probabilities
    test_feature_df = pandas.DataFrame(test_feature_data).fillna(-1)
    test_predicted_breaks = PARAGRAPH_SEGMENTER_MODEL.predict_proba(test_feature_df)
    predicted_df = pandas.DataFrame(test_predicted_breaks, columns=["prob_false", "prob_true"])
    paragraph_breaks = predicted_df.loc[predicted_df["prob_true"] >= 0.5, :].index.tolist()

    # Return first group
    if len(paragraph_breaks) > 0:
        if paragraph_breaks[0] > 0:
            paragraph = text[0:paragraph_breaks[0]].strip().replace("\n", " ").replace("\r", " ").strip()
            if len(paragraph) > 0:
                yield paragraph

    # Iterate through paragraph breaks
    for i in range(len(paragraph_breaks) - 1):
        # Get breaks
        pos0 = paragraph_breaks[i]
        pos1 = paragraph_breaks[i + 1]
        # Get text
        paragraph = text[pos0:pos1].strip().replace("\n", " ").replace("\r", " ").strip()
        para_len = len(paragraph)
        if para_len > 0:
            yield paragraph

    # Yield final section
    paragraph = text[paragraph_breaks[-1]:].strip().replace("\n", " ").replace("\r", " ").strip()
    yield paragraph
