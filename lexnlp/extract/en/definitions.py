"""Definition extraction for English.

This module implements basic definition extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

# Imports
import regex as re
import unidecode as unidecode
from typing import Generator
from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.nlp.en.tokens import get_token_list

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Constraints for matching
MAX_TERM_TOKENS = 3
MAX_TERM_CHARS = 64

# Primary pattern triggers
TRIGGER_LIST = ["shall have the meaning", "includes?", "as including",
                "shall mean", "means?", r"shall (?:not\s+)?include",
                "shall for purposes", "have meaning",
                "refers to", "shall refer to", "as used",
                "for purpose[sd]", "shall be deemed to",
                r"[\(\)]", "may be used", "is hereby changed to",
                "in ", "is defined", "shall be interpreted"]
TRIGGER_LIST.sort(key=len, reverse=True)

# Case 1: Term in quotes, is preceded by word|term|phrase or :,.^
# and has item from TRIGGER_LIST after itself.
# Fetch term along with quotes to be able to extract multiple terms,
# e.g.: the words "person" and "whoever" include
TRIGGER_WORDS_PTN = r"""
(?:(?:word|term|phrase)s?\s+|[:,\.]\s*|^)
['"“].{{1,{max_term_chars}}}['"”]\s*
(?:{trigger_list})[\s,]""".format(
    max_term_chars=MAX_TERM_CHARS,
    trigger_list="|".join([w.replace(" ", r"\s+") for w in TRIGGER_LIST]))
TRIGGER_WORDS_PTN_RE = re.compile(TRIGGER_WORDS_PTN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)
EXTRACT_PTN = r"""['"“](.+?)['"”\.]"""
EXTRACT_PTN_RE = re.compile(EXTRACT_PTN, re.UNICODE | re.DOTALL | re.MULTILINE)

# Case 2. Term inside quotes and brackets (the "Term") or ("Term")
PAREN_PTN = r"""\((?:the\s+)?['"“](.{{1,{max_term_chars}}}?)\.?['"”]\)""".format(max_term_chars=MAX_TERM_CHARS)
PAREN_PTN_RE = re.compile(PAREN_PTN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

# Case 3. Term is without quotes, is preceded by word|term|phrase or :,.^
# and has TRIGGER_LIST item after itself.
# e.g.: "Revolving Loan Commitment means…"; "LIBOR Rate shall mean…"
# false positive: "This Borrower Joiner Agreement to the extent signed signed and delivered by means of a facsimile..."
NOUN_PTN = r"""
^((?:[A-Z][-A-Za-z']*(?:\s*[A-Z][-A-Za-z']*){{0,{max_term_tokens}}})\b|\b(?:[A-Z][-A-Za-z']))\b\s*(?={trigger_list})"""\
    .format(max_term_tokens=MAX_TERM_TOKENS, trigger_list="|".join([w.replace(" ", r"\s+") for w in TRIGGER_LIST]))
NOUN_PTN_RE = re.compile(NOUN_PTN, re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

# Case 4: Term inside quotes is preceded by word|term|phrase or :,.^
# and has a colon after itself.
#e.g.: "'Term': definition"
COLON_PTN = r"""['"“](.{{1,{max_term_chars}}})['"”]:[\s]""".format(max_term_chars=MAX_TERM_CHARS)
COLON_PTN_RE = re.compile(COLON_PTN, re.UNICODE | re.DOTALL | re.MULTILINE)


def get_definitions_in_sentence(sentence: str, return_sources=False, decode_unicode=True) -> Generator:
    """
        Find possible definitions in natural language in a single sentence.
        :param decode_unicode:
        :param return_sources: returns a tuple with the extracted term and the source sentence
        :param sentence: an input sentence
        :return:
        """

    result = set()
    case1_terms = set()

    if decode_unicode:
        sentence = unidecode.unidecode(sentence)

    # case 1
    for item in TRIGGER_WORDS_PTN_RE.findall(sentence):
        result.update(EXTRACT_PTN_RE.findall(item))
        case1_terms.update(EXTRACT_PTN_RE.findall(item))

    # case 2
    result.update(PAREN_PTN_RE.findall(sentence))

    # case 3
    result.update(NOUN_PTN_RE.findall(sentence))

    # case 4
    result.update(COLON_PTN_RE.findall(sentence))

    # return result
    for term in result:
        if term not in case1_terms and len(get_token_list(term)) > MAX_TERM_TOKENS:
            continue
        if return_sources:
            yield (term, sentence)
        else:
            yield term


def get_definitions(text, return_sources=False, decode_unicode=True) -> Generator:
    """
    Find possible definitions in natural language in text.
    The text will be split to sentences first.
    :param decode_unicode:
    :param return_sources: returns a tuple with the extracted term and the source sentence
    :param text: the input text
    :return:
    """

    for sentence in get_sentence_list(text):
        yield from get_definitions_in_sentence(sentence, return_sources, decode_unicode)
