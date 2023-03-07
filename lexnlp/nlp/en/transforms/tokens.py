"""Transforms related to tokens for English
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import collections
import os
from typing import Dict

import nltk

from lexnlp.nlp.en.tokens import get_tokens, get_stems


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_token_distribution(text: str, lowercase=False, stopword=False) -> Dict[str, int]:
    """
    Get token distribution of text, potentially lowercasing and stopwording first.
    """
    # Iterate through tokens
    tokens = list(get_tokens(text, lowercase=lowercase, stopword=stopword))

    # Calculate distribution
    token_distribution = {t: tokens.count(t) for t in set(tokens)}
    return token_distribution


def get_stem_distribution(text: str, lowercase=False, stopword=False) -> Dict[str, int]:
    """
    Get stemmed token distribution of text, potentially lowercasing and stopwording first.
    """
    # Iterate through token stems
    tokens = list(get_stems(text, lowercase=lowercase, stopword=stopword))

    # Calculate distribution
    token_distribution = {t: tokens.count(t) for t in set(tokens)}
    return token_distribution


def get_ngram_distribution(text: str, n: int,
                           lowercase=False, stopword=False) -> Dict[str, int]:
    """
    Get n-gram distribution of text, potentially lowercasing and stopwording first.
    """

    # Return structure
    token_ngram_distribution = collections.defaultdict(int)

    # Iterate through tokens
    tokens = get_tokens(text, lowercase=lowercase, stopword=stopword)
    for ngram in nltk.ngrams(tokens, n):
        token_ngram_distribution[ngram] += 1

    # Calculate distribution
    return token_ngram_distribution


def get_bigram_distribution(text: str, lowercase=False, stopword=False) -> Dict[str, int]:
    """
    Get bigram distribution from text.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    return get_ngram_distribution(text, 2, lowercase=lowercase, stopword=stopword)


def get_trigram_distribution(text: str, lowercase=False, stopword=False) -> Dict[str, int]:
    """
    Get trigram distribution from text.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    return get_ngram_distribution(text, 3, lowercase=lowercase, stopword=stopword)


def get_skipgram_distribution(text: str, n: int, k: int,
                              lowercase=False, stopword=False) -> Dict[str, int]:
    """
    Get skipgram distribution from text.

    :param text:
    :param n:
    :param k:
    :param lowercase:
    :param stopword:
    :return:
    """
    # Get tokens
    tokens = get_tokens(text, lowercase=lowercase, stopword=stopword)

    # Return NLTK method results
    return nltk.util.skipgrams(tokens, n, k)
