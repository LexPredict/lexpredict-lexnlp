# pylint: disable=unused-import
from typing import Pattern, List, Generator
# pylint: enable=unused-import

from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.common.copyrights.copyright_parser import CopyrightParser
from lexnlp.extract.common.copyrights.copyright_parsing_methods import CopyrightParsingMethods
from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DeutscheCopyrightParsingMethods(CopyrightParsingMethods):
    def __init__(self):
        super(DeutscheCopyrightParsingMethods, self).__init__()
        self.trigger_words = ''
        self.reg_trigger_words = None # type: Pattern
        self.reg_word_c_years = None  # type: List[Pattern]
        self.reg_c_years_word = None  # type: List[Pattern]
        self.init_trigger_words()
        self.init_regexes()

    def init_trigger_words(self):
        self.trigger_words = r'urheberrechte|copyright|©|\(c\)'


def make_de_copyrights_parser():
    split_params = LineSplitParams()
    split_params.line_breaks = {'\n', '.', ';', '!', '?'}
    split_params.abbreviations = DeLanguageTokens.abbreviations
    split_params.abbr_ignore_case = True
    methods = DeutscheCopyrightParsingMethods()

    functions = [methods.match_word_c_years,
                 methods.match_c_years_word]

    prs = CopyrightParser(functions, split_params)
    prs.prohibited_words = {w for w in DeLanguageTokens.articles + DeLanguageTokens.conjunctions}
    return prs


parser = make_de_copyrights_parser()


def get_copyrights(text: str, language: str = None) -> Generator[dict, None, None]:
    ants = parser.parse(text, language if language else 'de')
    for ant in ants:
        yield ant.to_dictionary()


def get_copyright_list(text: str, language: str = None) -> List[CopyrightAnnotation]:
    return parser.parse(text, language if language else 'de')
