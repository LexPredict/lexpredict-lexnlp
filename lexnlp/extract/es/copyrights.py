# pylint: disable=unused-import
# pylint: enable=unused-import

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Generator, Tuple
from lexnlp.extract.common.copyrights.copyright_en_style_parser import CopyrightEnStyleParser
from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.es.language_tokens import EsLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams
from lexnlp.utils.lines_processing.line_processor import LineProcessor


class CopyrightEsParser(CopyrightEnStyleParser):
    line_processor = None  # type:LineProcessor

    @staticmethod
    def init_parser():
        split_params = LineSplitParams()
        split_params.line_breaks = {'\n', '.', ';', '!', '?'}
        split_params.abbreviations = EsLanguageTokens.abbreviations
        split_params.abbr_ignore_case = True
        CopyrightEsParser.line_processor = LineProcessor(
            line_split_params=split_params)

    @classmethod
    def extract_phrases_with_coords(cls, sentence: str) -> List[Tuple[str, int, int]]:
        return [(t.text, t.start, t.get_end()) for t in
                cls.line_processor.split_text_on_line_with_endings(sentence)]


CopyrightEsParser.init_parser()


def get_copyright_annotations(text: str, return_sources=False) -> Generator[CopyrightAnnotation, None, None]:
    for ant in CopyrightEsParser.get_copyright_annotations(text, return_sources):
        ant.locale = 'es'
        yield ant


def get_copyright_annotation_list(text: str, return_sources=False) -> List[CopyrightAnnotation]:
    return list(get_copyright_annotations(text, return_sources))


def get_copyrights(text: str, return_sources=False) -> Generator[dict, None, None]:
    for ant in get_copyright_annotations(text, return_sources):
        yield ant.to_dictionary()


def get_copyright_list(text: str, return_sources=False) -> List[dict]:
    return list(get_copyrights(text, return_sources))
