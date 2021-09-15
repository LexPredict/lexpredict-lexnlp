# pylint: disable=unused-import

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from typing import List, Generator, Tuple
import regex as re
from lexnlp.extract.common.copyrights.copyright_en_style_parser import CopyrightEnStyleParser
from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams, LineProcessor


class CopyrightDeParser(CopyrightEnStyleParser):
    line_processor = None  # LineProcessor
    copyright_words = ['Copyright', 'Urheberrechte', 'Urheberschutz', 'Eigentumsrecht']
    copyright_words_ptrn = r'\W\s*|'.join(copyright_words)

    copyright_ptn = fr"(({copyright_words_ptrn}|\(\s*[Cc]\s*\)\s*|©)+\s*{CopyrightEnStyleParser.year_ptn}?\s*(.+))"
    copyright_ptn_re = re.compile(copyright_ptn)

    @staticmethod
    def init_parser():
        split_params = LineSplitParams()
        split_params.line_breaks = {'\n', '.', ';', '!', '?'}
        split_params.abbreviations = DeLanguageTokens.abbreviations
        split_params.abbr_ignore_case = True
        CopyrightDeParser.line_processor = LineProcessor(line_split_params=split_params)

    @classmethod
    def extract_phrases_with_coords(cls, sentence: str) -> List[Tuple[str, int, int]]:
        return [(t.text, t.start, t.get_end()) for t in
                cls.line_processor.split_text_on_line_with_endings(sentence)]


CopyrightDeParser.init_parser()


def get_copyright_annotations(text: str, return_sources=False) -> \
        Generator[CopyrightAnnotation, None, None]:
    for ant in CopyrightDeParser.get_copyright_annotations(text, return_sources):
        ant.locale = 'de'
        yield ant


#def get_copyright_annotations(text: str, language: str = None) -> Generator[dict, None, None]:
#    ants = parser.parse(text, language if language else 'de')
#    for ant in ants:
#        yield ant


def get_copyrights(text: str, return_sources=False) -> \
        Generator[dict, None, None]:
    for ant in get_copyright_annotations(text, return_sources):
        yield ant.to_dictionary()


def get_copyright_list(text: str, return_sources=False) -> List[CopyrightAnnotation]:
    return list(get_copyright_annotations(text, return_sources))
