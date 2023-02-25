__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from abc import abstractmethod
from itertools import groupby
from typing import Callable, Generator, List
from lexnlp.extract.common.annotations.text_annotation import TextAnnotation
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.utils.lines_processing.line_processor import LineProcessor, LineSplitParams, LineOrPhrase


class TextPatternCollector:
    basic_line_processor = LineProcessor()
    """
    EsDefinitionsParser searches for definitions in text according to the
    rules of Spanish. See the "parse" method
    """
    def __init__(self, parsing_functions: List[Callable[[str], List[PatternFound]]], split_params: LineSplitParams):
        """
        :param parsing_functions: a functions' collection from SpanishParsingMethods
        :param split_params: text-to-sentences splitting params
        """
        self.parsing_functions = parsing_functions
        self.split_params = split_params
        self.proc = LineProcessor(line_split_params=self.split_params)
        self.prohibited_words = {}    # words that are Not definitions per se

    def parse(self, text: str, locale: str = None) -> Generator[TextAnnotation, None, None]:
        """
        :param locale: 'En', 'De', 'Es', ...
        :param text: En este acuerdo, el término "Software" se refiere a: (i) el programa informático
        :return: { "attrs": {"start": 28, "end": 82}, "tags": {"Extracted Entity Type": "definition",
                "Extracted Entity Definition Name": "Software",
                "Extracted Entity Text": ""Software" se refiere a: (i) el programa informático"} }
        """
        for phrase in self.proc.split_text_on_line_with_endings(text):
            matches = []
            for f in self.parsing_functions:
                ml = f(phrase.text)
                matches += ml
            # find synonyms
            # sort and take the most appropriate matches
            matches = self.remove_prohibited_words(matches)
            if len(matches) > 1:
                matches = self.choose_best_matches(matches)
                matches = self.choose_more_precise_matches(matches, phrase.text)
            # trim parts of matches
            for match in matches:
                ant = self.make_annotation_from_pattern(locale, match, phrase)
                ant.coords = (ant.coords[0] + phrase.start, ant.coords[1] + phrase.start)
                yield ant

    @abstractmethod
    def make_annotation_from_pattern(
        self,
        locale: str,
        ptrn: PatternFound,
        phrase: LineOrPhrase,
    ) -> TextAnnotation:
        raise NotImplementedError

    def remove_prohibited_words(self, matches: List[PatternFound]) -> List[PatternFound]:
        # like 'und' or 'and' or 'the' - the word like this is not a definition itself
        return [m for m in matches if m.name not in self.prohibited_words]

    @staticmethod
    def choose_best_matches(matches: List[PatternFound]) -> List[PatternFound]:
        resulted = []
        # pylint: disable=unused-variable
        for _, g in groupby(matches, lambda m: m.name.strip(" \t'\"")):
        # pylint: enable=unused-variable
            same_matches = list(g)
            if len(same_matches) > 1:
                same_matches = [sorted(same_matches,
                                       key=TextPatternCollector.estimate_match_quality, reverse=True)[0]]
            resulted += same_matches
        return resulted

    @staticmethod
    def choose_more_precise_matches(matches: List[PatternFound], text: str) -> List[PatternFound]:
        """
        look for a match "consumed" by other matches and spare the consuming! matches
        """
        resulted = []
        if len(matches) < 2:
            return matches
        for i, a in enumerate(matches):
            a_worse_b = False
            for j, b in enumerate(matches):
                if i == j:
                    continue
                if a.pattern_worse_than_target(b, text):
                    a_worse_b = True
                    break
            if not a_worse_b:
                resulted.append(a)
        return resulted

    @staticmethod
    def estimate_match_quality(match: PatternFound) -> int:
        return 1000 * match.probability - (match.end - match.start)
