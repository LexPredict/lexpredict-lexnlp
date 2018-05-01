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

from typing import Generator

# Packages
import pandas
from sklearn.externals import joblib

from lexnlp.nlp.en.segments.utils import build_document_line_distribution

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Setup module path
MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
PARAGRAPH_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./paragraph_segmenter.pickle"))


def build_paragraph_break_features(lines, line_id, line_window_pre, line_window_post, characters=string.printable,
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
        feature_vector["line_lenstrip_{0}".format(i)] = len(line.strip())
        feature_vector["line_title_case_{0}".format(i)] = line == line.title()
        feature_vector["line_upper_case_{0}".format(i)] = line == line.upper()

        # Count characters
        feature_vector["line_n_alpha_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("L")])
        feature_vector["line_n_number_{0}".format(i)] = sum(
            [1 for c in line if unicodedata.category(c).startswith("N")])
        feature_vector["line_n_punct_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("P")])
        feature_vector["line_n_whitespace_{0}".format(i)] = sum(
            [1 for c in line if unicodedata.category(c).startswith("Z")])

    # Simple checks
    line = lines[line_id]
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


def get_paragraphs(text, window_pre=3, window_post=3, score_threshold=0.5) -> Generator:
    """
    Get paragraphs.
    """
    # Get document character distribution
    doc_distribution = build_document_line_distribution(text)
    lines = text.splitlines()
    feature_data = []

    for line_id in range(len(lines)):
        feature_data.append(
            build_paragraph_break_features(lines, line_id, window_pre, window_post, include_doc=doc_distribution))

    # Predict page breaks
    feature_df = pandas.DataFrame(feature_data).fillna(-1).astype(int)
    predicted_lines = PARAGRAPH_SEGMENTER_MODEL.predict_proba(feature_df)
    predicted_df = pandas.DataFrame(predicted_lines, columns=["prob_false", "prob_true"])
    paragraph_breaks = predicted_df.loc[predicted_df["prob_true"] >= score_threshold, :].index.tolist()

    if len(paragraph_breaks) > 0:
        # Get first break
        pos0 = 0
        pos1 = paragraph_breaks[0]
        paragraph = "\n".join(lines[pos0:pos1])
        if len(paragraph.strip()) > 0:
            yield paragraph

        # Iterate through section breaks
        for i in range(len(paragraph_breaks) - 1):
            # Get breaks
            pos0 = paragraph_breaks[i]
            pos1 = paragraph_breaks[i + 1]
            # Get text
            paragraph = "\n".join(lines[pos0:pos1])
            if len(paragraph.strip()) > 0:
                yield paragraph

        # Yield final section
        paragraph = "\n".join(lines[paragraph_breaks[-1]:])
        if len(paragraph.strip()) > 0:
            yield paragraph.strip()
