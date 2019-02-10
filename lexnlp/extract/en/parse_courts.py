from apps.document.parsers.common.line_processor import LineSplitParams
from apps.document.parsers.common.universal_court_parser import UniversalCourtsParser
from apps.document.parsers.en.en_language_tokens import EnLanguageTokens
import os
import re


def setup_en_parser():
    paths = [os.path.join(os.path.dirname(__file__), "data/us_state_courts.csv"),
             os.path.join(os.path.dirname(__file__), "data/us_courts.csv"),
             os.path.join(os.path.dirname(__file__), "data/ca_courts.csv"),
             os.path.join(os.path.dirname(__file__), "data/au_courts.csv")]
    phrase_split_ptrs = LineSplitParams()
    phrase_split_ptrs.line_breaks = {'\n', '.', ';', ','}.union(set(EnLanguageTokens.conjunctions))
    phrase_split_ptrs.abbreviations = EnLanguageTokens.abbreviations
    phrase_split_ptrs.abbr_ignore_case = True

    parser = UniversalCourtsParser(re.compile('court', re.IGNORECASE),
                                   "Court Type",
                                   "Court Name",
                                   "Jurisdiction",
                                   paths,
                                   phrase_split_ptrs)
    return parser


en_court_parser = setup_en_parser()


def parse(text: str, language=None):
    return en_court_parser.parse(text)
