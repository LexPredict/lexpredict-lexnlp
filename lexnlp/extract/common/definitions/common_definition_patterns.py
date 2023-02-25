__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Match, Callable
import regex as re
from lexnlp.extract.common.definitions.universal_definition_parser import UniversalDefinitionsParser
from lexnlp.extract.common.pattern_found import PatternFound


class CommonDefinitionPatterns:
    reg_semicolon = re.compile("([\"'“„])(?:(?=(\\\\?))\\2.)*?\\1(?=:)", re.UNICODE | re.IGNORECASE)
    reg_quoted = re.compile("([\"'“„])(?:(?=(\\\\?))\\2.)*?\\1", re.UNICODE | re.IGNORECASE)
    reg_acronyms = re.compile(r"\(\p{Lu}\p{L}*\p{Lu}\)", re.UNICODE)

    @staticmethod
    def match_acronyms(phrase: str) -> List[PatternFound]:
        """
        :param phrase: rompió el silencio tras ser despedido del Canal del Fútbol (CDF).
        :return: {name: 'CDF', probability: 100, ...}
        """
        defs = []
        for match in CommonDefinitionPatterns.reg_acronyms.finditer(phrase):
            acr_start = CommonDefinitionPatterns.get_acronym_words_start(phrase, match)
            if acr_start < 0:
                continue
            df = PatternFound()
            df.name = match.group().strip('() ')
            df.start = acr_start
            df.end = match.start() - 1
            df.probability = 100
            defs.append(df)
        return defs

    @staticmethod
    def get_acronym_words_start(phrase: str, match: Match) -> int:
        """
        each acronym match should be preceded by capitalized words that start from the same letters
        :param phrase: "rompió el silencio tras ser despedido del Canal del Fútbol (CDF). "
        :param match: "(CDF)" Match object for this example
        :return: start letter (42 for this case) index or -1
        """
        proc = UniversalDefinitionsParser.basic_line_processor
        name = match.group().strip('() ').upper()
        start = match.start()
        words = proc.split_text_on_words(phrase[:start])
        if len(words) < 2:
            return -1

        mistakes = 0
        uppercases = 0
        acr_index = len(name) - 1
        acr_start = words[-1].start

        for i in range(len(words) - 1, -1, -1):
            if words[i].is_separator:
                continue
            l = words[i].text[0]
            l_upper = l.upper()
            is_upper = l_upper == l
            if is_upper:
                uppercases += 1
            is_correct = name[acr_index] == l_upper
            if not is_correct:
                mistakes += 1
                if mistakes > 1:
                    return -1
                continue
            acr_start = words[i].start
            acr_index -= 1
            if acr_index < 0:
                break
        return acr_start if uppercases > 1 and acr_index < 0 else -1

    @staticmethod
    def match_es_def_by_semicolon(phrase: str) -> List[PatternFound]:
        """
        :param phrase: "Modern anatomy human": a human of modern anatomy.
        :return: {name: 'Modern anatomy human', probability: 100, ...}
        """
        prob = 100
        defs = []

        for match in CommonDefinitionPatterns.reg_semicolon.finditer(phrase):
            df = PatternFound()
            df.name = match.group()
            df.start = 0
            df.end = len(phrase)
            df.probability = prob
            defs.append(df)
            prob = 66

        return defs

    @staticmethod
    def peek_quoted_part(phrase: str,
                         match: Match,
                         start_func: Callable[[str, Match, Match], int],
                         end_func: Callable[[str, Match, Match], int],
                         match_prob: int) -> List[PatternFound]:
        """
        :param phrase: the whole text, may be used for getting the definition's text length
        :param match: the matched part of the phrase that may contain several quote-packed definitions
        :param start_func: (phrase, match, quoted_match) -> definition's start
        :param end_func: (phrase, match, quoted_match) -> definition's end
        :param match_prob: definition's probability
        :return: a list of definitions found or an empty list
        """
        defs = []
        text = match.group()
        quoted_entries = list(CommonDefinitionPatterns.reg_quoted.finditer(text))
        if len(quoted_entries) == 0:
            return defs
        for entry in quoted_entries:
            df = PatternFound()
            df.name = entry.group()
            df.start = start_func(phrase, match, entry)
            df.end = end_func(phrase, match, entry)
            df.probability = match_prob
            defs.append(df)
        return defs

    @staticmethod
    def collect_regex_matches_with_quoted_chunks(phrase: str, reg: re, prob: int,
                                                 quoted_def_start: Callable[[str, Match, Match], int],
                                                 quoted_def_end: Callable[[str, Match, Match], int],
                                                 def_start: Callable[[str, Match], int],
                                                 def_end: Callable[[str, Match], int]
                                                 ) -> List[PatternFound]:
        """
        First, find all matches by 'reg' ptr
        Second, go through matches
        For each match try to find a set of quoted words
        If found, use them as matches
        Or use the whole match
        :param quoted_def_start: (phrase, match, quoted_match) -> definition's start
        :param quoted_def_end: (phrase, match, quoted_match) -> definition's end
        :param def_start: (phrase, match) -> definition's start
        :param def_end: (phrase, match) -> definition's end
        :return:
        """
        defs = []
        for match in reg.finditer(phrase):
            quoted_matches = \
                CommonDefinitionPatterns.peek_quoted_part(phrase,
                                                          match,
                                                          quoted_def_start,
                                                          quoted_def_end,
                                                          prob)
            if len(quoted_matches) > 0:
                defs += quoted_matches
                continue

            df = PatternFound()
            df.name = match.group()
            df.start = def_start(phrase, match)
            df.end = def_end(phrase, match)
            df.probability = prob
            defs.append(df)

        return defs

    @staticmethod
    def collect_regex_matches(phrase: str, reg: re, prob: int,
                              def_start: Callable[[str, Match], int],
                              def_end: Callable[[str, Match], int]
                              ) -> List[PatternFound]:
        """
        find all matches by 'reg' ptr
        :param quoted_def_start: (phrase, match, quoted_match) -> definition's start
        :param quoted_def_end: (phrase, match, quoted_match) -> definition's end
        :param def_start: (phrase, match) -> definition's start
        :param def_end: (phrase, match) -> definition's end
        :return:
        """
        defs = []
        for match in reg.finditer(phrase):

            df = PatternFound()
            df.name = match.group()
            df.start = def_start(phrase, match)
            df.end = def_end(phrase, match)
            df.probability = prob
            defs.append(df)

        return defs
