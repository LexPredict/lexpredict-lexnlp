"""Transforms related to tokens for English
"""
# Imports
import collections
import os

import nltk

from lexnlp.nlp.en.tokens import get_tokens

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_token_distribution(text, lowercase=False, stopword=False):
    """
    Get token distribution of text, potentially lowercasing and stopwording first.

    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    # Iterate through tokens
    tokens = list(get_tokens(text, lowercase=lowercase, stopword=stopword))

    # Calculate distribution
    token_distribution = dict([(t, tokens.count(t)) for t in set(tokens)])
    return token_distribution


def get_ngram_distribution(text, n, lowercase=False, stopword=False):
    """
    Get n-gram distribution of text, potentially lowercasing and stopwording first.

    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """

    # Return structure
    token_ngram_distribution = collections.defaultdict(int)

    # Iterate through tokens
    tokens = get_tokens(text, lowercase=lowercase, stopword=stopword)
    for ngram in nltk.ngrams(tokens, n):
        token_ngram_distribution[ngram] += 1

    # Calculate distribution
    return token_ngram_distribution


def get_bigram_distribution(text, lowercase=False, stopword=False):
    """
    Get bigram distribution from text.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    return get_ngram_distribution(text, 2, lowercase=lowercase, stopword=stopword)


def get_trigram_distribution(text, lowercase=False, stopword=False):
    """
    Get trigram distribution from text.
    :param text:
    :param lowercase:
    :param stopword:
    :return:
    """
    return get_ngram_distribution(text, 3, lowercase=lowercase, stopword=stopword)


def get_skipgram_distribution(text, n, k, lowercase=False, stopword=False):
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
