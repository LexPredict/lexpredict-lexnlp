__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Dict, Generator, Union
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.extract.common.text_pattern_collector import TextPatternCollector
from lexnlp.utils.lines_processing.line_processor import LineOrPhrase


class UniversalDefinitionsParser(TextPatternCollector):
    """
    EsDefinitionsParser searches for definitions in text according to the
    rules of Spanish. See the "parse" method
    """

    def make_annotation_from_pattern(
        self,
        locale: str,
        ptrn: PatternFound,
        phrase: LineOrPhrase,
    ) -> DefinitionAnnotation:
        return DefinitionAnnotation(
            name=ptrn.name,
            coords=(ptrn.start, ptrn.end),
            text=phrase.text[ptrn.start: ptrn.end],
            locale=locale
        )
