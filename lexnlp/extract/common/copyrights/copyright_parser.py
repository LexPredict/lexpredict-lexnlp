from typing import List

from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.extract.common.text_pattern_collector import TextPatternCollector
from lexnlp.utils.lines_processing.line_processor import LineOrPhrase


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CopyrightParser(TextPatternCollector):
    def make_annotation_from_pattrn(self,
                                    locale: str,
                                    ptrn: PatternFound,
                                    phrase: LineOrPhrase) -> TextAnnotation:
        ant = CopyrightAnnotation(name=ptrn.name, coords=(ptrn.start, ptrn.end),
                                  text=phrase.text[ptrn.start: ptrn.end],
                                  locale=locale)
        ant.company = ptrn.company  # pattern in in fact CopyrightPatternFound
        ant.year_start = ptrn.start_year
        ant.year_end = ptrn.end_year
        return ant

    def get_annotations_as_dictionaries(self) -> List[dict]:
        dfs = []
        for ant in self.annotations:
            df = ant.to_dictionary()
            dfs.append(df)
        return dfs
