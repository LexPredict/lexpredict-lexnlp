"""Definition extraction for English.

This module implements basic definition extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""
# pylint: disable=broad-except,bare-except


# Imports
import regex as re
import unidecode as unidecode
from collections import Counter
from typing import Generator, Pattern, List, Tuple
from lexnlp.nlp.en.segments.sentences import get_sentence__with_coords_list
from lexnlp.utils.lines_processing.line_processor import LineProcessor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
        if target.text in self.text:
            return 1
        if self.text in target.text:
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
STRONG_TRIGGER_LIST = ["shall have the meaning", "includes?", "as including",
                       "shall mean", "means?", r"shall (?:not\s+)?include",
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
['"“].{{1,{max_term_chars}}}['"”]\s*
(?:{trigger_list})[\s,]""".format(
    max_term_chars=MAX_TERM_CHARS,
    trigger_list=join_collection(ALL_TRIGGER_LIST))
TRIGGER_WORDS_PTN_RE = re.compile(TRIGGER_WORDS_PTN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)
EXTRACT_PTN = r"""['"“](.+?)['"”\.]"""
EXTRACT_PTN_RE = re.compile(EXTRACT_PTN, re.UNICODE | re.DOTALL | re.MULTILINE)

ARTICLES = ['the', 'a', 'an']

# Case 2. Term inside quotes and brackets (the "Term") or ("Term")
PAREN_PTN = r"""\((?:each(?:,)?\s+)?(?:(?:{articles})\s+)?['"“](.{{1,{max_term_chars}}}?)\.?['"”]\)""" \
    .format(articles=join_collection(ARTICLES), max_term_chars=MAX_TERM_CHARS)
PAREN_PTN_RE_OPTIONS = re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE

# Case 3. Term is without quotes, is preceded by word|term|phrase or :,.^
# and has TRIGGER_LIST item after itself.
# e.g.: "Revolving Loan Commitment means…"; "LIBOR Rate shall mean…"
# false positive: "This Borrower Joiner Agreement to the extent signed signed and delivered by means of a facsimile..."
NOUN_PTN = r"""
^((?:[A-Z][-A-Za-z']*(?:\s*[A-Z][-A-Za-z']*){{0,{max_term_tokens}}})\b|\b(?:[A-Z][-A-Za-z']))\b\s*(?={trigger_list})""" \
    .format(max_term_tokens=MAX_TERM_TOKENS, trigger_list="|".join([w.replace(" ", r"\s+") for
                                                                    w in STRONG_TRIGGER_LIST]))
NOUN_PTN_RE = re.compile(NOUN_PTN, re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

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

TRIGGER_QUOTED_DEFINITION_PATTERN = r"""['"“].{{1,{max_term_chars}}}['"”]""".format(max_term_chars=MAX_TERM_CHARS)
TRIGGER_QUOTED_DEFINITION_RE = re.compile(TRIGGER_QUOTED_DEFINITION_PATTERN, re.DOTALL)

QUOTED_DEFINITION_RE_PARAMS = [
    (PAREN_PTN, PAREN_PTN_RE_OPTIONS),
    (COLON_PTN, COLON_PTN_RE_OPTIONS),
    (ANCHOR_QUOTES_PTN, ANCHOR_QUOTE_RE_OPTIONS),
    (ANCHOR_SUBJECT_QUOTES_PTN, ANCHOR_SUBJECT_QUOTES_RE_OPTIONS)
]
QUOTED_DEFINITION_RE = [re.compile(template, options) for template, options in QUOTED_DEFINITION_RE_PARAMS]

QUOTED_TEXT_RE = re.compile("([\"'“„])(?:(?=(\\\\?))\\2.)+?\\1", re.UNICODE | re.IGNORECASE | re.DOTALL)

SPACES_RE = re.compile(r'\s')


def get_definition_list_in_sentence(sentence_coords: Tuple[str, int, int],
                                    decode_unicode=True) -> List[DefinitionCaught]:
    """
        Find possible definitions in natural language in a single sentence.
        :param decode_unicode:
        :param return_sources: returns a tuple with the extracted term and the source sentence
        :param sentence: an input sentence
        :return:
        """
    definitions = []  # type: List[DefinitionCaught]
    sentence = sentence_coords[0]
    sent_start = sentence_coords[1]
    result = set()

    if decode_unicode:
        sentence = unidecode.unidecode(sentence)

    # case 1
    for item in TRIGGER_WORDS_PTN_RE.finditer(sentence):
        result.update(regex_matches_to_word_coords(EXTRACT_PTN_RE, item.group(), item.start() + sent_start))

    # case 3
    mts = regex_matches_to_word_coords(NOUN_PTN_RE, sentence, sent_start)
    if len(mts) > 0:
        result.update(mts)

    # cases 2, 4, 5, 6
    for _ in TRIGGER_QUOTED_DEFINITION_RE.finditer(sentence):
        for quoted_definition_re in QUOTED_DEFINITION_RE:
            result.update(regex_matches_to_word_coords(quoted_definition_re, sentence, sent_start))
        break

    # make definitions out of entries
    for term_coords in result:
        term_processed = trim_defined_term(term_coords[0])
        term_clear = term_processed[0]
        term = term_clear if PICK_DEFINITION_FROM_QUOTES else term_coords[0]

        was_quoted = term_processed[1]
        # check the term is not empty
        if len(term.strip(''' []'"”().\t''')) == 0:
            continue

        # check the term is not too long
        max_words_per_definition = MAX_TERM_TOKENS
        if was_quoted:
            max_words_per_definition = MAX_QUOTED_TERM_TOKENS

        words_in_term = sum(1 for w in word_processor.split_text_on_words(term_clear)
                            if not w.is_separator)
        quotes_in_text = get_quotes_count_in_string(term_clear)
        possible_definitions = quotes_in_text // 2 if quotes_in_text > 1 else 1
        possible_tokens_count = max_words_per_definition * possible_definitions
        if words_in_term > possible_tokens_count:
            continue

        definitions.append(DefinitionCaught(term, sentence, (term_coords[1], term_coords[2])))

    return definitions


def trim_defined_term(term: str) -> Tuple[str, str]:
    """
    "trim" terms from definitions' keywords
    extract text from quotes
    :param term: 'referred to as a "Combined EBITDA Deficit"'
    :return: ('Combined EBITDA Deficit', 'quoted')
    """
    flags = ''

    # pick text from quotes
    quoted_parts = [m.group() for m in QUOTED_TEXT_RE.finditer(term)]
    if len(quoted_parts) == 1:
        term = quoted_parts[0].strip('''\"'“„''')
        flags = 'quoted'

    # rip off definition's keyword(s)
    term = SPACES_RE.sub(' ', term)
    return term, flags


def filter_definitions_for_self_repeating(definitions: List[DefinitionCaught]) -> List[DefinitionCaught]:
    """
    :param definitions:
    :return: excludes definitions that are "overlapped", leaves unique definitions only
    """
    for i in range(0, len(definitions)):
        a = definitions[i]
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


def get_definitions(text, return_sources=False, decode_unicode=True, return_coords=False) -> Generator:
    """
    Find possible definitions in natural language in text.
    The text will be split to sentences first.
    :param return_coords: returns a (x, y) tuple in each record. x - definition's text start, y - definition's text end
    :param decode_unicode:
    :param return_sources: returns a tuple with the extracted term and the source sentence
    :param text: the input text
    :return: Generator[name] or Generator[name, text] or Generator[name, text, coords]
    """

    definitions = get_definition_objects_list(text, decode_unicode)

    for df in definitions:
        if return_coords:
            yield (df.name, df.text, (df.coords[0], df.coords[1]))
        elif return_sources:
            yield (df.name, df.text)
        else:
            yield df.name


def get_definitions_in_sentence(sentence: str, return_sources=False,
                                decode_unicode=True) -> Generator:
    definitions = get_definition_list_in_sentence((sentence, 0, len(sentence)), decode_unicode)
    for df in definitions:
        if return_sources:
            yield (df.name, df.text)
        else:
            yield df.name


def get_definition_objects_list(text, decode_unicode=True) -> List[DefinitionCaught]:
    """
    :param text: text to search for definitions
    :param decode_unicode:
    :return: a list of found definitions - objects of class DefinitionCaught
    """
    definitions = []
    for sentence in get_sentence__with_coords_list(text):
        definitions += get_definition_list_in_sentence(sentence, decode_unicode)
    definitions = filter_definitions_for_self_repeating(definitions)
    return definitions


def get_definitions_explicit(text, decode_unicode=True) -> Generator:
    yield from get_definitions(text, return_sources=True, decode_unicode=decode_unicode, return_coords=True)
