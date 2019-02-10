import re
from itertools import groupby
from typing import List, Callable, Match

from lexnlp.utils.lines_processing.line_processor import LineProcessor, LineSplitParams


class DefinitionMatch:
    """
    used inside EsDefinitionsParser and SpanishParsingMethods
    to store intermediate parsing results
    """
    def __init__(self):
        self.name = None # type: str
        self.start = 0
        self.end = 0
        self.probability = 0


class UniversalDefinitionsParser:
    """
    EsDefinitionsParser searches for definitions in text according to the
    rules of Spanish. See the "parse" method
    """
    def __init__(self, parsing_functions: List[Callable[[str], List[DefinitionMatch]]],
                 split_params: LineSplitParams):
        """
        :param parsing_functions: a functions' collection from SpanishParsingMethods
        :param split_params: text-to-sentences splitting params
        """
        self.parsing_functions = parsing_functions
        self.annotations = [] # type: List[dict]
        self.split_params = split_params
        self.proc = LineProcessor()
        self.prohibited_words = {} # words that are Not definitions per se

    def parse(self, text: str) -> List[dict]:
        """
        :param text: En este acuerdo, el término "Software" se refiere a: (i) el programa informático
        :return: { "attrs": {"start": 28, "end": 82}, "tags": {"Extracted Entity Type": "definition",
                "Extracted Entity Definition Name": "Software",
                "Extracted Entity Text": ""Software" se refiere a: (i) el programa informático"} }
        """
        for phrase in self.proc.split_text_on_line_with_endings(text, self.split_params):
            matches = []
            for f in self.parsing_functions:
                ml = f(phrase.text)
                matches += ml
            # find synonyms
            # sort and take the most appropriate matches
            matches = self.remove_prohibited_words(matches)
            if len(matches) > 1:
                matches = self.choose_best_matches(matches)
                matches = self.choose_more_precise_matches(matches)
            # trim parts of matches
            for match in matches:
                ant = {
                    "attrs": {
                        "start": phrase.start + match.start,
                        "end": phrase.start + match.end
                    },
                    "tags": {
                        'Extracted Entity Type': 'definition',
                        'Extracted Entity Definition Name': match.name,
                        'Extracted Entity Text': phrase.text[match.start: match.end]
                    }
                }
                self.annotations.append(ant)
        return self.annotations

    def remove_prohibited_words(self, matches: List[DefinitionMatch]) -> List[DefinitionMatch]:
        # like 'und' or 'and' or 'the' - the word like this is not a definition itself
        return [m for m in matches if m.name not in self.prohibited_words]

    def choose_best_matches(self, matches: List[DefinitionMatch]) -> List[DefinitionMatch]:
        resulted = []
        for k, g in groupby(matches, lambda m: m.name.strip(" \t'\"")):
            same_matches = list(g)
            if len(same_matches) > 1:
                same_matches = [sorted(same_matches,
                                       key=UniversalDefinitionsParser.estimate_match_quality, reverse=True)[0]]
            resulted += same_matches
        return resulted

    def choose_more_precise_matches(self, matches: List[DefinitionMatch]) -> List[DefinitionMatch]:
        """
        look for a match "consumed" by other matches and spare the consuming! matches
        """
        resulted = []
        if len(matches) < 2:
            return matches
        for i in range(0, len(matches)):
            a = matches[i]
            is_consuming = False
            for j in range(0, len(matches)):
                if i == j:
                    continue
                b = matches[j]
                if b.name in a.name:
                    is_consuming = True
                    break
            if not is_consuming:
                resulted.append(a)
        return resulted


    @staticmethod
    def estimate_match_quality(match: DefinitionMatch) -> int:
        return 1000 * match.probability - (match.end - match.start)


class CommonDefinitionPatterns:
    reg_semicolon = re.compile("([\"'“„])(?:(?=(\\\\?))\\2.)*?\\1(?=:)", re.UNICODE | re.IGNORECASE)
    reg_quoted = re.compile("([\"'“„])(?:(?=(\\\\?))\\2.)*?\\1", re.UNICODE | re.IGNORECASE)

    @staticmethod
    def match_es_def_by_semicolon(phrase: str) -> List[DefinitionMatch]:
        """
        :param phrase: "Modern anatomy human": a human of modern anatomy.
        :return: {name: 'Modern anatomy human', probability: 100, ...}
        """

        prob = 100
        defs = []

        for match in CommonDefinitionPatterns.reg_semicolon.finditer(phrase):
            df = DefinitionMatch()
            df.name = match.group()
            df.start = 0
            df.end = len(phrase)
            df.probability = prob
            defs.append(df)
            prob = 66

        return defs

    @staticmethod
    def peek_quoted_part(match: Match,
                         start_func: Callable[[Match, Match], int],
                         end_func: Callable[[Match, Match], int],
                         match_prob: int) -> List[DefinitionMatch]:
        defs = []
        text = match.group()
        quoted_entries = [m for m in CommonDefinitionPatterns.reg_quoted.finditer(text)]
        if len(quoted_entries) == 0:
            return defs
        for entry in quoted_entries:
            df = DefinitionMatch()
            df.name = entry.group()
            df.start = start_func(match, entry)
            df.end = end_func(match, entry)
            df.probability = match_prob
            defs.append(df)
        return defs
