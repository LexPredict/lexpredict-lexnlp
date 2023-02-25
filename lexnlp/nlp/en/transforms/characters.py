"""Transforms related to characters for English
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import collections
import os

import nltk

from lexnlp.nlp.en.tokens import get_token_list, get_tokens


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_character_distribution(text, lowercase=False, stopword=False):
    """
    Get character distribution of text, potentially lowercasing and stopwording first.
    N.B. This method does not include or count blank spaces.

    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    # Iterate through tokens
    tokens = get_tokens(text, lowercase=lowercase, stopword=stopword)
    token_text = "".join(tokens)

    # Calculate distribution
    character_distribution = {c: token_text.count(c) for c in set(token_text)}

    return character_distribution


def get_character_ngram_distribution(text, n, lowercase=False, stopword=False):
    """
    Get character distribution of text, potentially lowercasing and stopwording first.
    N.B. This method does not include or count blank spaces.

    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    # Return structure
    character_ngram_distribution = collections.defaultdict(int)

    # Iterate through tokens
    for token in get_token_list(text, lowercase=lowercase, stopword=stopword):
        for char_seq in nltk.ngrams(token, n):
            character_ngram_distribution[char_seq] += 1

    return character_ngram_distribution
