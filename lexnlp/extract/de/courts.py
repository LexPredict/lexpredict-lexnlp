# pylint: disable=unused-argument

import os
import re
from typing import Generator, List
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def setup_de_parser():
    def preproc_func(text):
        return re.sub('e$', '[e]?', text)

    ptrs = ParserInitParams()
    ptrs.key_word_preproc_func = preproc_func
    ptrs.court_pattern_checker = re.compile('gericht')
    ptrs.split_ptrs = LineSplitParams()
    ptrs.split_ptrs.line_breaks = {'\n', '.', ';', ','}.union(set(DeLanguageTokens.conjunctions))
    ptrs.split_ptrs.abbreviations = DeLanguageTokens.abbreviations
    ptrs.split_ptrs.abbr_ignore_case = True

    ptrs.column_names = {'type': 'Court Type (de-DE)',
                         'name': 'Court Name (de-DE)',
                         'jurisdiction': 'Jurisdiction',
                         'alias': 'Alias (de-DE)'}

    path = os.path.join(os.path.dirname(__file__), "../../config/de/de_courts.csv")
    ptrs.dataframe_paths = [path]
    return UniversalCourtsParser(ptrs)


parser = setup_de_parser()


def get_courts(text: str, language=None) -> Generator[dict, None, None]:
    courts = parser.parse(text, language if language else 'de')
    for c in courts:
        yield c.to_dictionary()


def get_court_list(text: str, language=None) -> List[CourtAnnotation]:
    return parser.parse(text, language if language else 'de')
