"""Utility methods for segmentation classifiers

This module implements utility methods for segmentation, such as shared methods to generate
document character distributions.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import string
from typing import Dict, Union
from lexnlp.utils.decorators import handle_invalid_text


@handle_invalid_text(return_value={})
def build_document_distribution(
    text: str,
    characters=string.printable,
    norm=True
) -> Dict[str, Union[int, float]]:
    """
    Build document character distribution based on fixed character, optionally norming.
    :param text:
    :param characters:
    :param norm:
    :return:
    """
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


@handle_invalid_text(return_value={})
def build_document_line_distribution(
    text: str,
    characters=string.printable,
    norm=True
) -> Dict[str, Union[int, float]]:
    """
    Build document and line character distribution for section segmenting based
    on fixed character, optionally normalizing vector.
    """

    # Build character vector
    feature_vector = {}
    for character in characters:
        feature_vector[f"doc_char_{character}"] = text.count(character)
        feature_vector[f"doc_startchar_{character}"] = 0
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
                feature_vector[character] = feature_vector[character] / total_startchar if total_startchar != 0.0 else 0.0

    return feature_vector
