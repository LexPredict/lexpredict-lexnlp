# pylint: disable=unused-import

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from typing import Dict, Generator, List, Tuple
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


def get_copyright_annotations(text: str, return_sources=False) -> Generator[CopyrightAnnotation, None, None]:
    """
    Gets copyright annotations.

    Args:
        text (str):
            An input string to search for copyrights.

        return_sources (bool=False):
            Whether to return the input text.

    Yields:
        CopyrightAnnotation
    """
    for ant in CopyrightDeParser.get_copyright_annotations(text, return_sources):
        ant.locale = 'de'
        yield ant


def get_copyright_annotation_list(text: str, return_sources=False) -> List[CopyrightAnnotation]:
    """
    Gets a list of copyright annotations.

    Args:
        text (str):
            An input string to search for copyrights.

        return_sources (bool=False):
            Whether to return the input text.

    Returns:
        A list of CopyrightAnnotations
    """
    return list(get_copyright_annotations(text, return_sources))


def get_copyrights(text: str, return_sources=False) -> Generator[dict, None, None]:
    """
    Gets copyrights.

    Args:
        text (str):
            An input string to search for copyrights.

        return_sources (bool=False):
            Whether to return the input text.

    Yields:
        Dictionaries representing copyright annotations.
    """
    for ant in get_copyright_annotations(text, return_sources):
        yield ant.to_dictionary()


def get_copyright_list(text: str, return_sources: bool = False) -> List[Dict]:
    """
    Gets a list of dictionaries representing copyright annotations.

    Args:
        text (str):
            An input string to search for copyrights.

        return_sources (bool=False):
            Whether to return the input text.

    Returns:
        A list of dictionaries representing copyright annotations.
    """
    return list(get_copyrights(text, return_sources))
