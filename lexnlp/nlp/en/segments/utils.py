"""Utility methods for segmentation classifiers

This module implements utility methods for segmentation, such as shared methods to generate
document character distributions.

Todo:
"""

# Imports
import string

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def build_document_distribution(text, characters=string.printable, norm=True):
    """
    Build document character distribution based on fixed character, optionally norming.
    :param text:
    :param characters:
    :param norm:
    :return:
    """
    # Check for empty
    text_len = len(text)
    if text_len == 0:
        return {}

    # Build character vector
    char_vector = {}

    for character in characters:
        char_vector["doc_char_{0}".format(character)] = text.count(character)

    # Norm if requested
    if norm:
        total = float(sum(char_vector.values()))
        for key in char_vector:
            char_vector[key] = char_vector[key] / total

    return char_vector


def build_document_line_distribution(text, characters=string.printable, norm=True):
    """
    Build document and line character distribution for section segmenting based on fixed character, optionally
    normalizing vector.
    """

    # Build character vector
    feature_vector = {}
    for character in characters:
        feature_vector["doc_char_{0}".format(character)] = text.count(character)
        feature_vector["doc_startchar_{0}".format(character)] = 0
    feature_vector["doc_startchar_other"] = 0

    # Build line start vector
    for line in text.splitlines():
        if len(line.strip()) > 0:
            character = line.strip()[0]

            if character in characters:
                feature_vector["doc_startchar_{0}".format(character)] += 1
            else:
                feature_vector["doc_startchar_other"] += 1
        else:
            continue

    # Norm if requested
    if norm:
        total_char = float(sum([b for a, b in feature_vector.items() if a.startswith("doc_char")]))
        total_startchar = float(sum([b for a, b in feature_vector.items() if a.startswith("doc_startchar")]))

        for character in feature_vector.keys():
            if character.startswith("doc_char"):
                feature_vector[character] = feature_vector[character] / total_char
            elif character.startswith("doc_startchar"):
                feature_vector[character] = feature_vector[character] / total_startchar

    return feature_vector
