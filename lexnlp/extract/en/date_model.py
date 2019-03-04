"""Date extraction for English.

This module implements date extraction functionality in English.
"""
# pylint: disable=bare-except

# Standard imports
import itertools
import os
import string

from sklearn.externals import joblib


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Setup path
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load model
MODEL_DATE = joblib.load(os.path.join(MODULE_PATH, "./date_model.pickle"))

DATE_MODEL_CHARS = []
DATE_MODEL_CHARS.extend(string.ascii_letters)
DATE_MODEL_CHARS.extend(string.digits)
DATE_MODEL_CHARS.extend(["-", "/", " ", "%", "#", "$"])


def get_date_features(text, start_index, end_index, include_bigrams=True, window=5, characters=None,
                      norm=True):
    """
    Get features to use for classification of date as false positive.
    :param text: raw text around potential date
    :param start_index: date start index
    :param end_index: date end index
    :param include_bigrams: whether to include bigram/bicharacter features
    :param window: window around match
    :param characters: characters to use for feature generation, e.g., digits only, alpha only
    :param norm: whether to norm, i.e., transform to proportion
    :return:
    """
    # Check chars
    if not characters:
        characters = DATE_MODEL_CHARS

    # Get text window
    window_start = max(0, start_index - window)
    window_end = min(len(text), end_index + window)
    feature_text = text[window_start:window_end].strip()

    # Build character vector
    char_vec = {}
    char_keys = []
    bigram_keys = {}
    for character in characters:
        key = "char_{0}".format(character)
        char_vec[key] = feature_text.count(character)
        char_keys.append(key)

    # Build character bigram vector
    if include_bigrams:
        bigram_set = ["".join(s) for s in itertools.permutations(characters, 2)]
        bigram_keys = []
        for character in bigram_set:
            key = "bigram_{0}".format(character)
            char_vec[key] = feature_text.count(character)
            bigram_keys.append(key)

    # Norm if requested
    if norm:
        # Norm by characters
        char_sum = sum([char_vec[k] for k in char_keys])
        if char_sum > 0:
            for key in char_keys:
                char_vec[key] /= float(char_sum)

        # Norm by bigrams
        if include_bigrams:
            bigram_sum = sum([char_vec[k] for k in bigram_keys])
            if bigram_sum > 0:
                for key in bigram_keys:
                    char_vec[key] /= float(bigram_sum)

    return char_vec
