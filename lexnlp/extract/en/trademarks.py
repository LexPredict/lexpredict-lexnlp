"""Trademark extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic Trademark extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.

Todo: -
"""

# Imports
import re
from typing import Generator

from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.extract.en.utils import NPExtractor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


TRADEMARK_PTN = r"[A-Z0-9][^\)]+(?:[a-z]TM|[ \(]TM(?:\W|$)|™|\s*\(R\)|Ⓡ|®)"
TRADEMARK_PTN_RE = re.compile(TRADEMARK_PTN)

grammar = r"""
    NBAR:
        {<NNP.*|JJ|\(|,>*<NNP.*|\)>}  # Nouns, Adj-s, brackets, terminated with Nouns or brackets
    IN:
        {<CC|IN>}   # &, and, of
    NP:
        {(<NBAR><IN>)*<NBAR>}
"""
np_extractor = NPExtractor(grammar=grammar)


def get_trademarks(text) -> Generator:
    """
    Find trademarks in text.
    :param text:
    :return:
    """
    # Iterate through sentences
    if TRADEMARK_PTN_RE.search(text):
        for sentence in get_sentence_list(text):
            for phrase in np_extractor.get_np(sentence):
                tms = TRADEMARK_PTN_RE.findall(phrase)
                for tm in tms:
                    yield tm
