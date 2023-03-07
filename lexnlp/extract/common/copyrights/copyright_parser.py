__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List

from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.extract.common.text_pattern_collector import TextPatternCollector
from lexnlp.utils.lines_processing.line_processor import LineOrPhrase


class CopyrightParser(TextPatternCollector):
    def make_annotation_from_pattern(
        self,
        locale: str,
        ptrn: PatternFound,
        phrase: LineOrPhrase,
    ) -> TextAnnotation:
        ant = CopyrightAnnotation(name=ptrn.name, coords=(ptrn.start, ptrn.end),
                                  text=phrase.text[ptrn.start: ptrn.end],
                                  locale=locale)
        ant.company = ptrn.company  # pattern in fact CopyrightPatternFound
        ant.year_start = ptrn.start_year
        ant.year_end = ptrn.end_year
        return ant
