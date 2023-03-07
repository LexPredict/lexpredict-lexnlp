"""Page segmentation for English.

This module implements page segmentation in English using simple
machine learning classifiers.

Todo:
  * Standardize model (re-)generation
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import string
import unicodedata

from typing import Generator

# Packages
import pandas
import joblib

# Project imports
from lexnlp.nlp.en.segments.utils import build_document_distribution


# Setup module path


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
PAGE_SEGMENTER_MODEL = joblib.load(os.path.join(MODULE_PATH, "./page_segmenter.pickle"))


def build_page_break_features(lines, 
                              line_id, 
                              line_window_pre, 
                              line_window_post, 
                              characters=string.printable,
                              include_doc=None):
    """
    Build a feature vector for a given line ID with given parameters.
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
    line_stripped = line.strip()
    len_line_stripped = len(line_stripped)
    feature_vector["page"] = 1 if "page" in line else 0
    feature_vector["PAGE"] = 1 if "PAGE" in line else 0
    feature_vector["Page"] = 1 if "Page" in line else 0
    feature_vector["sw_page"] = 1 if line_stripped.lower().startswith("page") else 0
    feature_vector["sw_pg"] = 1 if line_stripped.lower().startswith("pg") else 0
    feature_vector["first_char_punct"] = (line_stripped[0] in string.punctuation) if len_line_stripped > 0 else False
    feature_vector["last_char_punct"] = (line_stripped[-1] in string.punctuation) if len_line_stripped > 0 else False
    feature_vector["first_char_number"] = (line_stripped[0] in string.digits) if len_line_stripped > 0 else False
    feature_vector["last_char_number"] = (line_stripped[-1] in string.digits) if len_line_stripped > 0 else False

    # Build character vector
    for character in characters:
        feature_vector["char_{0}".format(character)] = lines[line_id].count(character)

    # Add doc if requested
    if include_doc:
        feature_vector.update(include_doc)

    return feature_vector


def get_page_break_feature_names(lines_count: int,
                                 line_window_pre: int,
                                 line_window_post: int,
                                 characters=string.printable,
                                 include_doc=None):
    """
    Build a feature vector for a given line ID with given parameters.
    """
    # Feature vector
    feature_vector = {
        'page',
        'PAGE',
        'Page',
        'sw_page',
        'sw_pg',
        'first_char_punct',
        'last_char_punct',
        'first_char_number',
        'last_char_number'
    }

    # Check start offset
    if lines_count - 1 < line_window_pre:
        line_window_pre = lines_count - 1

    # Check final offset
    if line_window_post >= lines_count:
        line_window_post = lines_count - line_window_post - 1

    # Iterate through window
    for i in range(-line_window_pre, line_window_post + 1):

        # Count length
        feature_vector.add(f'line_len_{i}')
        # Count characters
        feature_vector.add(f'line_n_alpha_{i}')
        feature_vector.add(f'line_n_number_{i}')
        feature_vector.add(f'line_n_punct_{i}')
        feature_vector.add(f'line_n_whitespace_{i}')

    # Build character vector
    for character in characters:
        feature_vector.add(f'char_{character}')

    # Add doc if requested
    if include_doc:
        feature_vector.update(set(include_doc.keys()))

    return feature_vector


def get_pages(text, window_pre=3, window_post=3, score_threshold=0.5) -> Generator:
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
            build_page_break_features(lines, line_id, window_pre, window_post,
                                      include_doc=doc_distribution))

    # Predict page breaks
    column_names = list(get_page_break_feature_names(len(lines), window_pre, window_post,
                                                     include_doc=doc_distribution))
    column_names.sort()
    test_feature_df = pandas.DataFrame(test_feature_data, columns=column_names).fillna(-1)
    test_predicted_lines = PAGE_SEGMENTER_MODEL.predict_proba(test_feature_df)
    predicted_df = pandas.DataFrame(test_predicted_lines, columns=['prob_false', 'prob_true'])
    page_breaks = predicted_df.loc[predicted_df['prob_true'] >= score_threshold, :].index.tolist()

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
