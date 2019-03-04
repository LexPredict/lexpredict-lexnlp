# pylint: disable=unused-import
from typing import Pattern, List, Generator
# pylint: enable=unused-import

from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.common.copyrights.copyright_parser import CopyrightParser
from lexnlp.extract.common.copyrights.copyright_parsing_methods import CopyrightParsingMethods
from lexnlp.extract.es.language_tokens import EsLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams


class SpanishCopyrightParsingMethods(CopyrightParsingMethods):
    def __init__(self):
        super(SpanishCopyrightParsingMethods, self).__init__()
        self.trigger_words = ''
        self.reg_trigger_words = None  # type: Pattern
        self.reg_word_c_years = None  # type: List[Pattern]
        self.reg_c_years_word = None  # type: List[Pattern]
        self.init_trigger_words()
        self.init_regexes()

    def init_trigger_words(self):
        self.trigger_words = r'copyright|©|\(c\)'


def make_es_copyrights_parser():
    split_params = LineSplitParams()
    split_params.line_breaks = {'\n', '.', ';', '!', '?'}
    split_params.abbreviations = EsLanguageTokens.abbreviations
    split_params.abbr_ignore_case = True
    methods = SpanishCopyrightParsingMethods()

    functions = [methods.match_word_c_years,
                 methods.match_c_years_word]

    p = CopyrightParser(functions, split_params)
    p.prohibited_words = {w for w in EsLanguageTokens.articles + EsLanguageTokens.conjunctions}
    return p


parser = make_es_copyrights_parser()


def get_copyrights(text: str, language: str = None) -> Generator[dict, None, None]:
    ants = parser.parse(text, language if language else 'es')
    for ant in ants:
        yield ant.to_dictionary()


def get_copyright_list(text: str, language: str = None) -> List[CopyrightAnnotation]:
    return parser.parse(text, language if language else 'es')  # type: List[CopyrightAnnotation]
