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
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Constraints for matching
MAX_TERM_TOKENS = 4
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

# Case #1. Term in quotes, has item from TRIGGER_LIST after itself
#  and word|term|phrase or :,.^ before
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

# Case #2. Term inside quotes and brackets (the "Term") or ("Term")
PAREN_PTN = r"""\((?:the\s+)?['"“](.{{1,{max_term_chars}}}?)\.?['"”]\)""".format(max_term_chars=MAX_TERM_CHARS)
PAREN_PTN_RE = re.compile(PAREN_PTN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)


# Case #3. Term without quotes has TRIGGER_LIST item after itself
#  and word|term|phrase or :,.^ before
# TODO


def get_definitions(text, return_sources=False, decode_unicode=True) -> Generator:
    """
    Find possible definitions in natural language.
    :param decode_unicode:
    :param return_sources:
    :param text:
    :return:
    """

    for sentence in get_sentence_list(text):
        result = set()

        if decode_unicode:
            sentence = unidecode.unidecode(sentence)

        for item in TRIGGER_WORDS_PTN_RE.findall(sentence):
            result.update(EXTRACT_PTN_RE.findall(item))

        # case #2
        result.update(PAREN_PTN_RE.findall(sentence))

        for term in result:
            if len(get_token_list(term)) <= MAX_TERM_TOKENS:
                if return_sources:
                    yield (term, sentence)
                else:
                    yield term
