"""Page segmentation for English.

This module implements page segmentation in English using simple
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

# Project imports
from lexnlp.nlp.en.segments.utils import build_document_distribution

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Setup module path
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
PAGE_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./page_segmenter.pickle"))


def build_page_break_features(lines, line_id, line_window_pre, line_window_post, characters=string.printable,
                              include_doc=None):
    """
    Build a feature vector for a given line ID with given parameters.
    :param lines:
    :param line_id:
    :param line_window_pre:
    :param line_window_post:
    :param characters:
    :param include_doc:
    :return:
    """
    # Feature vector
    feature_vector = {}

    # Check start offset
    if line_id < line_window_pre:
        line_window_pre = line_id

    # Check final offset
    if (line_id + line_window_post) >= len(lines):
        line_window_post = len(lines) - line_window_post - 1

    # Iterate through window
    for i in range(-line_window_pre, line_window_post + 1):
        try:
            line = lines[line_id + i]
        except IndexError:
            continue

        # Count length
        feature_vector["line_len_{0}".format(i)] = len(line)

        # Count characters
        feature_vector["line_n_alpha_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("L")])
        feature_vector["line_n_number_{0}".format(i)] = sum(
            [1 for c in line if unicodedata.category(c).startswith("N")])
        feature_vector["line_n_punct_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("P")])
        feature_vector["line_n_whitespace_{0}".format(i)] = sum(
            [1 for c in line if unicodedata.category(c).startswith("Z")])

    # Simple checks
    line = lines[line_id]
    feature_vector["page"] = 1 if "page" in line else 0
    feature_vector["PAGE"] = 1 if "PAGE" in line else 0
    feature_vector["Page"] = 1 if "Page" in line else 0
    feature_vector["sw_page"] = 1 if line.strip().lower().startswith("page") else 0
    feature_vector["sw_pg"] = 1 if line.strip().lower().startswith("pg") else 0
    feature_vector["first_char_punct"] = (line.strip()[0] in string.punctuation) if len(line.strip()) > 0 else False
    feature_vector["last_char_punct"] = (line.strip()[-1] in string.punctuation) if len(line.strip()) > 0 else False
    feature_vector["first_char_number"] = (line.strip()[0] in string.digits) if len(line.strip()) > 0 else False
    feature_vector["last_char_number"] = (line.strip()[-1] in string.digits) if len(line.strip()) > 0 else False

    # Build character vector
    for character in characters:
        feature_vector["char_{0}".format(character)] = lines[line_id].count(character)

    # Add doc if requested
    if include_doc:
        feature_vector.update(include_doc)

    return feature_vector


def get_pages(text, window_pre=3, window_post=3, score_threshold=0.5):
    """
    Get pages from text.
    :param text:
    :param window_pre:
    :param window_post:
    :param score_threshold:
    :return:
    """

    # Get document character distribution
    doc_distribution = build_document_distribution(text)
    lines = text.splitlines()
    test_feature_data = []
    for line_id in range(len(lines)):
        test_feature_data.append(
            build_page_break_features(lines, line_id, window_pre, window_post, include_doc=doc_distribution))

    # Predict page breaks
    test_feature_df = pandas.DataFrame(test_feature_data).fillna(-1)
    test_predicted_lines = PAGE_SEGMENTER_MODEL.predict_proba(test_feature_df)
    predicted_df = pandas.DataFrame(test_predicted_lines, columns=["prob_false", "prob_true"])
    page_breaks = predicted_df.loc[predicted_df["prob_true"] >= score_threshold, :].index.tolist()

    if len(page_breaks) > 0:
        # Get first break
        pos0 = 0
        pos1 = page_breaks[0]
        yield "\n".join(lines[pos0:pos1])

        # Iterate through paragraph breaks
        for i in range(len(page_breaks) - 1):
            # Get breaks
            pos0 = page_breaks[i]
            pos1 = page_breaks[i + 1]
            # Get text
            page = "\n".join(lines[pos0:pos1])
            if len(page.strip()) > 1:
                yield page

        # Yield final page
        page = "\n".join(lines[page_breaks[-1]:])
        if len(page.strip()) > 1:
            yield page.strip()
