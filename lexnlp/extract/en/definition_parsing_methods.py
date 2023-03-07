"""Definition extraction for English.

This module implements basic definition extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# pylint: disable=broad-except,bare-except


import regex as re
import unidecode
from collections import Counter
from typing import Pattern, List, Tuple, Set

from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder
from lexnlp.extract.common.text_beautifier import TextBeautifier
from lexnlp.extract.en.introductory_words_detector import IntroductoryWordsDetector
from lexnlp.extract.en.preprocessing.span_tokenizer import SpanTokenizer
from lexnlp.extract.common.special_characters import SpecialCharacters
from lexnlp.extract.en.en_language_tokens import EnLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineProcessor
from lexnlp.utils.iterating_helpers import count_sequence_matches


class DefinitionCaught:
    """
    Each definition is stored in this class with
    its name, full text and "coords" within the whole document
    """
    __slots__ = ['name', 'text', 'coords']

    def __init__(self, name: str, text: str, coords: Tuple[int, int]):
        self.name = name
        self.text = text
        self.coords = coords

    def __repr__(self):
        return '%s [%d, %d]' % (self.name, self.coords[0], self.coords[1])

    def does_consume_target(self, target) -> int:
        """
        :param target: a definition that is, probably, "consumed" by the current one
        :return: 1 if self consumes the target, -1 if the target consumes self, overwise 0
        """
        coords_spans = (target.coords[0] >= self.coords[0] and
            target.coords[0] <= self.coords[1]) or \
            (self.coords[0] >= target.coords[0] and
            self.coords[0] <= target.coords[1])
        if not coords_spans:
            return 0
        if (target.name or '') in (self.name or ''):
            return 1
        if (self.name or '') in (target.name or ''):
            return -1
        return 0


# when the following flag is True,
# the term defined got stripped off quotes:
# e.g., (any such excess being referred to as a "Combined EDITT Deficit Alpha Beta Gamma Cappa")
# will become just (Combined EDITT Deficit Alpha Beta Gamma Cappa)
PICK_DEFINITION_FROM_QUOTES = True

# Constraints for matching
MAX_TERM_TOKENS = 5
MAX_QUOTED_TERM_TOKENS = 7
MAX_TERM_CHARS = 64

# Primary pattern triggers
STRONG_TRIGGER_LIST = ["shall have the meaning", r"includes?", "as including",
                       "shall mean", r"means?", r"shall (?:not\s+)?include",
                       "shall for purposes", "have meaning",
                       "referred to", "known as",
                       "refers to", "shall refer to", "as used",
                       "for purpose[sd]", "shall be deemed to",
                       "may be used", "is hereby changed to",
                       "is defined", "shall be interpreted"]

WEAK_TRIGGER_LIST = [r"[\(\)]", "in "]
ALL_TRIGGER_LIST = STRONG_TRIGGER_LIST + WEAK_TRIGGER_LIST

STRONG_TRIGGER_LIST.sort(key=len, reverse=True)
WEAK_TRIGGER_LIST.sort(key=len, reverse=True)
ALL_TRIGGER_LIST.sort(key=len, reverse=True)


def join_collection(collection):
    return "|".join([w.replace(" ", r"\s+") for w in collection])


word_processor = LineProcessor()

# Case 1: Term in quotes, is preceded by word|term|phrase or :,.^
# and has item from TRIGGER_LIST after itself.
# Fetch term along with quotes to be able to extract multiple terms,
# e.g.: the words "person" and "whoever" include
TRIGGER_WORDS_PTN = r"""
(?:(?:word|term|phrase)s?\s+|[:,\.]\s*|^)
['"“].{{1,{max_term_chars}}}['"”]\w{{0,2}}\s*
(?:{trigger_list})[\s,]""".format(
    max_term_chars=MAX_TERM_CHARS,
    trigger_list=join_collection(ALL_TRIGGER_LIST))
TRIGGER_WORDS_PTN_RE = re.compile(TRIGGER_WORDS_PTN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

EXTRACT_PTN = r"""
“(.+?)“|
"(.+?)"|
'(.+?)'
"""
EXTRACT_PTN_RE = re.compile(EXTRACT_PTN, re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

ARTICLES = ['the', 'a', 'an']

# Case 2. Term inside quotes and brackets (the "Term") or ("Term")
PAREN_QUOTE_PTN = r"""\((?:each(?:,)?\s+)?(?:(?:{articles})\s+)?['"“](.{{1,{max_term_chars}}}?)\.?['"”]\)""" \
    .format(articles=join_collection(ARTICLES), max_term_chars=MAX_TERM_CHARS)
PAREN_QUOTE_PTN_RE_OPTIONS = re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE

# Case 2.5. Term inside brackets (TERM) or (Term), starts with uppercase
PAREN_PTN = r"""\((?:E|each(?:,)?\s+)?(?:(?:{articles})\s+)?([A-Z][^\)]{{1,{max_term_chars}}}?)\.?\)""" \
    .format(articles=join_collection(ARTICLES), max_term_chars=MAX_TERM_CHARS)
PAREN_PTN_RE_OPTIONS = re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE

# Case 3. Term is without quotes, is preceded by word|term|phrase or :,.^
# and has TRIGGER_LIST item after itself.
# e.g.: "Revolving Loan Commitment means…"; "LIBOR Rate shall mean…"
# false positive: "This Borrower Joiner Agreement to the extent signed signed and delivered by means of a facsimile..."
NOUN_PTN_BASE = r"""
(
    (?:[A-Z][-A-Za-z']*+(?:\s*[A-Z][-A-Za-z']*){{0,{max_term_tokens}}})
    |
    (?:[A-Z][-A-Za-z'])
)
""".format(max_term_tokens=MAX_TERM_TOKENS)
# NB: we use possessive quantifier (*+) here because this group
# ([A-Z][-A-Za-z']*) check shouldn't fail and track back


NOUN_PTN = r"""
(?:^|\s)
(?:
    {noun_ptn_base}
    |
    "{noun_ptn_base}"
    |
    “{noun_ptn_base}”
)
\s+(?=(?:{trigger_list})\W)
""".format(noun_ptn_base=NOUN_PTN_BASE,
           trigger_list="|".join([w.replace(" ", r"\s+") for w in STRONG_TRIGGER_LIST]))

NOUN_PTN_RE = re.compile(NOUN_PTN, re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

NOUN_ANTI_PTN = r"""the\s*"""
NOUN_ANTI_PTN_RE = re.compile(NOUN_ANTI_PTN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

# Case 4: Term inside quotes is preceded by word|term|phrase or :,.^
# and has a colon after itself.
# e.g.: "'Term': definition"
COLON_PTN = r"""((['](.{{1,{max_term_chars}}})['])|""" \
            r"""(["](.{{1,{max_term_chars}}})["])|""" \
            r"""([“](.{{1,{max_term_chars}}})[”]))""" \
            r""":[\s]""".format(max_term_chars=MAX_TERM_CHARS)

COLON_PTN_RE_OPTIONS = re.UNICODE | re.DOTALL | re.MULTILINE

# Case 5: phrase called|herein|herein as... + term in quotes
# e.g.: all of which are herein collectively called the "Insurances", any such bank being an "Approved Bank"
ANCHOR = ['called', 'herein', 'herein as', 'collectively(?:,)?', 'collectively as', 'individually(?:,)?',
          'individually as', 'together(?:,)?', 'together with', 'referred to as', 'being', 'shall be', 'definition as',
          'known as', 'designated as', 'hereinafter', 'hereinafter as', 'hereafter', 'hereafter as', 'its', 'our',
          'your', 'any of the foregoing,', 'in such capacity,', 'in this section,', 'in this paragraph,',
          r'in this \(noun\),', 'each such', 'this']
ANCHOR_QUOTES_PTN = r"""(?:(?:{anchor})\s+)(?:(?:{articles})\s+)?['"“](.{{1,{max_term_chars}}}?)['"”]""" \
    .format(anchor=join_collection(ANCHOR), articles=join_collection(ARTICLES), max_term_chars=MAX_TERM_CHARS)
ANCHOR_QUOTE_RE_OPTIONS = re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE

# Case 6: phrase such|any such|together + subject + term in quotes
# e.g.: such earlier date, the "End Date", any such event, an "Event of Default"
ANCHOR = ['such', 'any such', 'together']
ANCHOR_SUBJECT_QUOTES_PTN = r"(?:(?:{anchor})\s+?)(?:.{{1,{max_term_chars}}}\s+?)(?:(?:{articles})\s+)?" \
                            r"(('(.{{1,{max_term_chars}}}?)')|" \
                            r"(\"(.{{1,{max_term_chars}}}?)\")|" \
                            r"(“(.{{1,{max_term_chars}}}?)”))" \
    .format(anchor=join_collection(ANCHOR), articles=join_collection(ARTICLES), max_term_chars=MAX_TERM_CHARS)
ANCHOR_SUBJECT_QUOTES_RE_OPTIONS = re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE

TRIGGER_QUOTED_DEFINITION_PATTERN = r"""['"“][^'"“]{{1,{max_term_chars}}}['"”]""".format(max_term_chars=MAX_TERM_CHARS)
TRIGGER_QUOTED_DEFINITION_RE = re.compile(TRIGGER_QUOTED_DEFINITION_PATTERN, re.DOTALL)

QUOTED_DEFINITION_RE_PARAMS = [
    (PAREN_PTN, PAREN_PTN_RE_OPTIONS),
    (PAREN_QUOTE_PTN, PAREN_QUOTE_PTN_RE_OPTIONS),
    (COLON_PTN, COLON_PTN_RE_OPTIONS),
    (ANCHOR_QUOTES_PTN, ANCHOR_QUOTE_RE_OPTIONS),
    (ANCHOR_SUBJECT_QUOTES_PTN, ANCHOR_SUBJECT_QUOTES_RE_OPTIONS)
]

QUOTED_DEFINITION_RE = [re.compile(template, options) for template, options in QUOTED_DEFINITION_RE_PARAMS]

QUOTED_TEXT_RE = re.compile("([\"'“„])(?:(?=(\\\\?))\\2.)+?\\1", re.UNICODE | re.IGNORECASE | re.DOTALL)

# used for replacing multiple spaces by single ones
SPACES_RE = re.compile(r'\s+')

# non significant parts of speech
# if defined term consists on NON_SIG_POSes only - this is not
# a definition (like "as is", "this" etc)
NON_SIG_POS = {'CC', 'CD', 'DT', 'EX', 'IN', 'LS',
               'MD', 'PDT', 'POS', 'PRP$', 'RB', 'RBR',
               'RBS', 'RP', 'TO', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB',
               '.', ',', ':', '-', ';', ')', '(', ']', '{', '}'
               '[', '*', '/', '\\', '"', '\'', '!', '?', '%',
               '$', '^', '&', '@'}
# PDT predeterminer ‘all the kids’
# POS possessive ending parent’s
# RB adverb very, silently,
# RBR adverb, comparative better
# RBS adverb, superlative best

# punctuation POS that we have to skip while, e.g., removing introductory words
PUNCTUATION_POS = {'``', '\t'}.union(SpecialCharacters.punctuation)

# used for stripping strings
PUNCTUATION_STRIP_STR = ''.join(PUNCTUATION_POS)

# this punctuation should be removed from definition's name
STRIP_PUNCT_SYMBOLS = ',:-'


ABBREVIATION_PTRN = '|'.join([a.replace('.', '\\.') for a
                              in EnLanguageTokens.abbreviations])
# if the term ends with abbreviations, last dot won't be trimmed
ABBREVIATION_ENDING_RE = re.compile(f'({ABBREVIATION_PTRN})$')

# split one phrase containing several definitions into definitions
SPLIT_SUBDEFINITIONS_PTRN = r'''["“](?:[^"“]{{1,{max_term_chars}}})["“]'''.format(
    max_term_chars=MAX_TERM_CHARS)

SPLIT_SUBDEFINITIONS_RE = re.compile(SPLIT_SUBDEFINITIONS_PTRN, re.DOTALL)


def get_definition_list_in_sentence(sentence_coords: Tuple[int, int, str],
                                    decode_unicode=True) -> List[DefinitionCaught]:
    """
        Find possible definitions in natural language in a single sentence.
        :param sentence_coords: sentence, sentence start, end
        :param decode_unicode:
        :return:
        """
    definitions: List[DefinitionCaught] = []
    sentence = sentence_coords[2]
    # unify quotes and braces
    # replace excess braces with ' ' so the str length will remain the same
    sentence = TextBeautifier.unify_quotes_braces(sentence,
                                                  empty_replacement=' ')
    sent_start = sentence_coords[0]
    result = set()  # type: Set[Tuple[str, int, int]]

    # it really transforms string, e.g. replaces “ with "
    if decode_unicode:
        sentence = unidecode.unidecode(sentence)
        sentence_coords = sentence_coords[0], sentence_coords[1], sentence

    # case 1
    for item in TRIGGER_WORDS_PTN_RE.finditer(sentence):
        result.update(regex_matches_to_word_coords(EXTRACT_PTN_RE, item.group(), item.start() + sent_start))

    # case 3
    mts = regex_matches_to_word_coords(NOUN_PTN_RE, sentence, sent_start)
    mts = [i for i in mts if not NOUN_ANTI_PTN_RE.fullmatch(i[0])]
    mts = [m for m in mts if m[0].lower().strip(' ,;.') not in EnLanguageTokens.pronouns]
    if len(mts) > 0:
        result.update(mts)

    # cases 2, 4, 5, 6
    for _ in TRIGGER_QUOTED_DEFINITION_RE.finditer(sentence):
        for quoted_definition_re in QUOTED_DEFINITION_RE:
            result.update(regex_matches_to_word_coords(quoted_definition_re, sentence, sent_start))
        break

    # make definitions out of entries
    for term, start, end in result:
        term_cleared = TextBeautifier.strip_pair_symbols((term, start, end))
        term_cleared = trim_defined_term(term_cleared[0], term_cleared[1], term_cleared[2])
        was_quoted = term_cleared[3]

        if PICK_DEFINITION_FROM_QUOTES:
            term, start, end = term_cleared[0], term_cleared[1], term_cleared[2]

        if not term_cleared[0]:
            continue

        term, start, end = TextBeautifier.unify_quotes_braces_coords(
            term, start, end)

        # check the term is not empty
        if len(term.strip(PUNCTUATION_STRIP_STR)) == 0:
            continue

        # returns [('word', 'token', (word_start, word_end)), ...] ...
        term_pos = list(SpanTokenizer.get_token_spans(term))
        if does_term_are_service_words(term_pos):
            continue

        term_wo_intro = IntroductoryWordsDetector.remove_term_introduction(
            term, term_pos)
        if term_wo_intro != term:
            term = TextBeautifier.strip_pair_symbols(term_wo_intro)
        if not term:
            continue

        # check the term is not too long
        max_words_per_definition = MAX_TERM_TOKENS
        if was_quoted:
            max_words_per_definition = MAX_QUOTED_TERM_TOKENS

        words_in_term = sum(1 for w in word_processor.split_text_on_words(term_cleared[0])
                            if not w.is_separator)
        quotes_in_text = get_quotes_count_in_string(term_cleared[0])
        possible_definitions = quotes_in_text // 2 if quotes_in_text > 1 else 1
        possible_tokens_count = max_words_per_definition * possible_definitions
        if words_in_term > possible_tokens_count:
            continue

        split_definitions_lst = split_definitions_inside_term(
            term, sentence_coords, start, end)

        for definition, s, e in split_definitions_lst:
            definition, s, e = TextBeautifier.strip_pair_symbols((definition, s, e))
            definitions.append(DefinitionCaught(definition, sentence, (s, e)))

    return definitions


def split_definitions_inside_term(term: str,
                                  src_with_coords: Tuple[int, int, str],
                                  term_start: int,
                                  term_end: int) -> List[Tuple[str, int, int]]:
    """
    The whole phrase can be considered definition ("MSRB", "we", "us" or "our"),
    but in fact the phrase can be a collection of definitions.
    Here we split definition phrase to a list of definitions.

    Source string could be pre-processed, that's why we search for each
    sub-phrase's coordinates (PhrasePositionFinder)
    :param term: a definition or, probably, a set of definitions ("MSRB", "we", "us" or "our")
    :param src_with_coords: a sentence (probably), containing the term + its coords
    :param term_start: "term" start coordinate within the source sentence
    :param term_end: "term" end coordinate within the source sentence
    :return: [(definition, def_start, def_end), ...]
    """
    src_start = src_with_coords[0]
    src_text = src_with_coords[2]

    matches = [m.group() for m in SPLIT_SUBDEFINITIONS_RE.finditer(term)]
    if len(matches) < 2:
        matches = [term]

    match_coords = PhrasePositionFinder.find_phrase_in_source_text(
        src_text, matches, term_start - src_start, term_end - src_start)

    if len(match_coords) < len(matches):
        return [(term, term_start, term_end)]

    match_coords = [(m[0], m[1] + src_start, m[2] + src_start) for m in match_coords]

    return match_coords


def does_term_are_service_words(term_pos: List[Tuple[str, str, int, int]]) -> bool:
    """
    Does term consist of service words only?
    """
    for _, pos, _, _ in term_pos:
        if pos not in NON_SIG_POS:
            return False
    return True


def trim_defined_term(term: str, start: int, end: int) -> \
        Tuple[str, int, int, bool]:
    """
    Remove pair of quotes / brackets framing text
    Replace N-grams of spaces with single spaces
    Replace line breaks with spaces
    :param term: a phrase that may contain excess framing symbols
    :param start: original term's start position, may be changed
    :param end: original term's end position, may be changed
    :return: updated term, start, end and the flag indicating that the whole phrase was inside quotes
    """
    was_quoted = False

    # pick text from quotes
    # pick text from quotes
    quoted_parts = [m.group() for m in QUOTED_TEXT_RE.finditer(term)]
    if len(quoted_parts) == 1:
        term = quoted_parts[0].strip('''\"'“„''')
        was_quoted = True

    orig_term_len = len(term)
    orig_term_quotes = count_sequence_matches(term, lambda c: c in TextBeautifier.QUOTES)
    term, start, end = TextBeautifier.strip_pair_symbols((term, start, end))
    if len(term) < orig_term_len:
        # probably we removed quotes
        updated_term_quotes = count_sequence_matches(term, lambda c: c in TextBeautifier.QUOTES)
        was_quoted = was_quoted or orig_term_quotes - updated_term_quotes > 1

    term = term.replace('\n', ' ')
    term = SPACES_RE.sub(' ', term)

    term, start, end = TextBeautifier.strip_string_coords(
        term, start, end, STRIP_PUNCT_SYMBOLS)

    # strip all dots or just left one (if ends with abbreviation)
    ends_with_abbr = ABBREVIATION_ENDING_RE.search(term)
    if not ends_with_abbr:
        term, start, end = TextBeautifier.strip_string_coords(
            term, start, end, '.')
    else:
        term, start, end = TextBeautifier.lstrip_string_coords(
            term, start, end, '.')

    return term, start, end, was_quoted


def filter_definitions_for_self_repeating(definitions: List[DefinitionCaught]) -> List[DefinitionCaught]:
    """
    :param definitions:
    :return: excludes definitions that are "overlapped", leaves unique definitions only
    """
    for i, a in enumerate(definitions):
        if not a.name:
            continue
        for j in range(i + 1, len(definitions)):
            b = definitions[j]
            consumes = a.does_consume_target(b)
            if consumes == 1:
                b.name = None
            elif consumes == -1:
                a.name = None

    return [d for d in definitions if d.name is not None]


def get_quotes_count_in_string(text: str) -> int:
    """
    :param text: text to calculate quotes within
    :return: calculates count of quotes within the text passed
    """
    c = Counter(text)
    return sum(filter(None, [c['"'], c['”']]))


def regex_matches_to_word_coords(pattern: Pattern[str],
                                 text: str, phrase_start: int = 0) -> List[Tuple[str, int, int]]:
    """
    :param pattern: pattern for searching for matches within the text
    :param text: text to search for matches
    :param phrase_start: a value to be add to start / end
    :return: tuples of (match_text, start, end) out of the regex (pattern) matches in text
    """
    return [(m.group(), m.start() + phrase_start, m.end() + phrase_start)
            for m in pattern.finditer(text)]
