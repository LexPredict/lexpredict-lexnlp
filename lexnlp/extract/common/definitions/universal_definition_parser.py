from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.extract.common.text_pattern_collector import TextPatternCollector
from lexnlp.extract.en.tests.test_definitions import DefinitionAnnotation
from lexnlp.utils.lines_processing.line_processor import LineOrPhrase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class UniversalDefinitionsParser(TextPatternCollector):
    """
    EsDefinitionsParser searches for definitions in text according to the
    rules of Spanish. See the "parse" method
    """

    def make_annotation_from_pattrn(self,
                                    locale: str,
                                    ptrn: PatternFound,
                                    phrase: LineOrPhrase) -> TextAnnotation:
        return DefinitionAnnotation(
            name=ptrn.name, coords=(ptrn.start, ptrn.end),
            text=phrase.text[ptrn.start: ptrn.end],
            locale=locale)

    def get_definition_dictionaries(self):
        dfs = []
        for ant in self.annotations:
            dfs.append({
                    "attrs": {
                        "start": ant.coords[0],
                        "end": ant.coords[1]
                    },
                    "tags": {
                        'Extracted Entity Type': 'definition',
                        'Extracted Entity Definition Name': ant.name,
                        'Extracted Entity Text': ant.text
                    }
                })
        return dfs
