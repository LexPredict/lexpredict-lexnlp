# pylint: disable=unused-argument

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import re
from typing import Generator, List
from lexnlp.extract.common.annotations.court_annotation import CourtAnnotation
from lexnlp.extract.common.universal_court_parser import UniversalCourtsParser, ParserInitParams
from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams


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


def get_court_annotations(text: str, language: str = 'de') -> Generator[CourtAnnotation, None, None]:
    yield from parser.parse(text, language)


def get_court_annotation_list(text: str, language: str = 'de') -> List[CourtAnnotation]:
    return list(get_court_annotations(text, language))


def get_courts(text: str, language: str = 'de') -> Generator[dict, None, None]:
    for court_annotation in parser.parse(text, language):
        yield court_annotation.to_dictionary()


def get_court_list(text: str, language: str = 'de') -> List[dict]:
    return list(get_courts(text, language))
