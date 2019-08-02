"""Trademark extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic Trademark extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.

Todo: -
"""

# Imports
import re
from typing import Generator

from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder
from lexnlp.extract.common.annotations.trademark_annotation import TrademarkAnnotation
from lexnlp.nlp.en.segments.sentences import get_sentence_span
from lexnlp.extract.en.utils import NPExtractor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
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


def get_trademarks(text: str) -> Generator[str, None, None]:
    """
    Find trademarks in text.
    """
    for ant in get_trademark_annotations(text):
        yield ant.trademark


def get_trademark_annotations(text: str) -> \
        Generator[TrademarkAnnotation, None, None]:
    """
    Find trademarks in text.
    """
    # Iterate through sentences
    if TRADEMARK_PTN_RE.search(text):
        for scd in get_sentence_span(text):
            sentence = scd[2]
            phrases = list(np_extractor.get_np(sentence))
            tagged_phrases = PhrasePositionFinder.find_phrase_int_source_text(
                sentence, phrases)
            for phrase in tagged_phrases:
                for tm in TRADEMARK_PTN_RE.finditer(phrase[0]):
                    coords = tm.span()
                    coords = (coords[0] + scd[0] + phrase[1],
                              coords[1] + scd[0] + phrase[1])
                    if coords[1] >= len(text):
                        coords = (coords[0], len(text) - 1)
                    ant = TrademarkAnnotation(coords=coords,
                                              trademark=tm.group())
                    yield ant
