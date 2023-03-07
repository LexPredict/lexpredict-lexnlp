# pylint: disable=W0212

"""Sentence segmentation for English.

This module implements sentence segmentation in English using simple
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
import re
from typing import Tuple, List, Generator, Any, Union

# Packages
from nltk.tokenize.punkt import PunktTrainer, PunktSentenceTokenizer
import joblib

from lexnlp.extract.en.en_language_tokens import EnLanguageTokens

# Setup module path


MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load segmenters
SENTENCE_SEGMENTER_MODEL: PunktSentenceTokenizer = \
    joblib.load(os.path.join(MODULE_PATH, "./sentence_segmenter.pickle"))
extra_abbreviations = [a.rstrip('.') for a in EnLanguageTokens.abbreviations]
SENTENCE_SEGMENTER_MODEL._params.abbrev_types.update(extra_abbreviations)
SENTENCE_SEGMENTER_MODEL._params.abbrev_types.update(['no', 'l'])


PRE_PROCESS_TEXT_REMOVE = re.compile(
    r'(?:^\s*\d+\s*$)'
    r'|(?:^\s*\<PAGE\>\s*(\d+)?\s*(\n|$))'
    r'|(?:^\s*(^.+)?[Pp][Aa][Gg][Ee]\s+\d+\s+[Oo][Ff]\s+\d+(.+)?$\s*(\n|$))'
    r'|(?:^\s+$)'
    r'|(?:^\s*i+\s*$)',
    re.MULTILINE
)

# '|'-separated templates of the sequences splitting sentences.
SENTENCE_SPLITTERS = re.compile(
    r'(?<=\n)\s*\n'  # Blank line - usually separates one sentence from another
    r'|(?<=\n)\S+.*[ \t.]{5,200}\S.+\S\s*(?=\n)'  # Something:       separated with spaces
)

SENTENCE_SPLITTERS_LOWER_EXCLUDE = re.compile(
    r'(?:\s*and\s*)'
)

NOT_SENTENCES = re.compile(
    r'\W+'  # OCR artifacts like some non-alphanumeric chars on separate lines
    r'|(\W*[^\W\d_]{1,2}(\W+[^\W\d_]{1,2})*\W*)|\W+'  # OCR artifacts like 'a bba af ag ah'
)

STRIP_GROUP = re.compile(r'^\s*(\S.*?)\s*$', re.DOTALL)


# are used in normalize_text for better splitting text on sentences
PRETOKENIZE_REPLACEMENTS = (('“', '"'), ('”', '"'))


def pre_process_document(text: str) -> str:
    """
    Pre-process text of the specified document before splitting it to the sentences.
    Removes obsolete formatting, page-splitting markers, page numbers e.t.c.
    :param text:
    :return:
    """
    if not text:
        return text
    return PRE_PROCESS_TEXT_REMOVE.sub('', text)


def _trim_span(span_text: str, span: Tuple[int, int]) -> Union[None, Tuple[int, int]]:
    m = STRIP_GROUP.search(span_text)
    if m:
        new_span = m.span(1)
        return span[0] + new_span[0], span[0] + new_span[1]

    return None


def post_process_sentence(text: str, sent_span: Tuple[int, int]) \
        -> Generator[Tuple[int, int], Any, Any]:
    """
    Post-process sentence span detected by PunktSentenceTokenizer by additionally extracting
    titles, table of contents entries and other short strings stayed separately between empty lines
    into separate sentences.
    :param text:
    :param sent_span:
    :return:
    """
    sent_start = sent_span[0]
    sent_end = sent_span[1]
    sent = text[sent_start:sent_end]

    prev_start = 0
    for m in SENTENCE_SPLITTERS.finditer(sent):
        full_match_start = m.start()
        if SENTENCE_SPLITTERS_LOWER_EXCLUDE.fullmatch(m.group().lower()):
            continue

        # If we found text splitter and there is some text between sentence start/prev splitter
        # and the new found splitter - yield it as a separate sentence.
        if full_match_start >= prev_start:
            span = (sent_start + prev_start, sent_start + full_match_start)
            span_text = text[span[0]: span[1]]
            if not NOT_SENTENCES.fullmatch(span_text):
                span = _trim_span(span_text, span)
                if span:
                    yield span
            # Set cursor to the end of the found sentence splitting sequence
            prev_start = full_match_start

    # Yield the last piece of the original sentence: from the end of the last found
    # splitter til the end of the original sentence.
    if prev_start < len(sent):
        span = (sent_start + prev_start, sent_start + len(sent))
        span_text = text[span[0]: span[1]]
        if not NOT_SENTENCES.fullmatch(span_text):
            span = _trim_span(span_text, span)
            if span:
                yield span


def normalize_text(text: str) -> str:
    """
    Simple text pre-processing: replacing "not-quite unicode" symbols
    by their common equivalents for better parsing sentences with
    get_sentence_span function.
    :param text: “U.S. Person” means any Person
    :return: "U.S. Person" means any Person
    """
    for orig, nc in PRETOKENIZE_REPLACEMENTS:
        text = text.replace(orig, nc)
    return text


def get_sentence_span(text: str) -> Generator[Tuple[int, int, str], Any, Any]:
    """
    Given a text, returns a list of the (start, end) spans of sentences
    in the text.
    """
    text_unified = normalize_text(text)
    for span in SENTENCE_SEGMENTER_MODEL.span_tokenize(text_unified, realign_boundaries=True):
        for start, end in post_process_sentence(text, span):
            substring = text[start:end]  # we take fragments from original text
            yield start, end, substring


def get_sentence_span_list(text) -> List[Tuple[int, int, str]]:
    """
    Given a text, generates (start, end) spans of sentences
    in the text.
    """
    return [*get_sentence_span(text)]


def get_sentences(text: str) -> Generator[str, None, None]:
    for _, _, sentence_span in get_sentence_span(text):
        yield sentence_span


def get_sentence_list(text: str) -> List[str]:
    """
    Get sentences from text.
    :param text:
    :return:
    """
    return [*get_sentences(text)]


def build_sentence_model(text, extra_abbrevs=None):
    """
    Build a sentence model from text with optional
    extra abbreviations to include.
    :param text:
    :param extra_abbrevs:
    :return:
    """

    # Setup Punkt trainer
    punkt_trainer = PunktTrainer()
    punkt_trainer.train(text, verbose=False, finalize=False)
    punkt_trainer.finalize_training(verbose=False)

    # Extract parameters from trainer
    punkt_params = punkt_trainer.get_params()

    # Add any extras if passed
    if extra_abbrevs is not None:
        for abbrev in extra_abbrevs:
            punkt_params.abbrev_types.add(abbrev.strip(".").lower())

    # Return model instantiated with new parameters
    return PunktSentenceTokenizer(punkt_params)
