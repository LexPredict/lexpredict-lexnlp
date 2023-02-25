# pylint: disable=unused-import

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import Pattern, List, Tuple
# pylint: enable=unused-import
import regex as re
from lexnlp.extract.common import year_parser
from lexnlp.extract.common.copyrights.copyright_pattern_found import CopyrightPatternFound
from lexnlp.extract.common.definitions.common_definition_patterns import CommonDefinitionPatterns
from lexnlp.extract.common.pattern_found import PatternFound


class CopyrightParsingMethods:
    def __init__(self):
        self.trigger_words = ''
        self.reg_trigger_words = None  # type: Pattern
        self.reg_word_c_years = None  # type: List[Pattern]
        self.reg_c_years_word = None  # type: List[Pattern]
        self.init_trigger_words()
        self.init_regexes()

    def init_trigger_words(self):
        # should be overriden
        pass

    def init_regexes(self):
        self.reg_company_name = re.compile(r"[\p{L}\s]+", re.UNICODE | re.IGNORECASE)
        self.reg_trigger_words = re.compile(self.trigger_words,
                                            re.UNICODE | re.IGNORECASE)
        self.reg_word_c_years = re.compile(
            r"[^,;:\|\t]+(%s)\s+\d{4}([–\s-]+\d{4})?" % self.trigger_words,
            re.UNICODE | re.IGNORECASE)
        self.reg_c_years_word = re.compile(
            r"(%s)\s+\d{4}([–\s-]+\d{4})?[^\b;\.]+" % self.trigger_words,
            re.UNICODE | re.IGNORECASE)

    def match_word_c_years(self, phrase: str) -> List[PatternFound]:
        """
        :param phrase: © Siemens 1996 – 2019
        :return: {name: '© Siemens 1996 – 2019', probability: 100, ...}
        """
        if not self.reg_trigger_words.search(phrase):
            return []

        reg = self.reg_word_c_years
        dfs = CommonDefinitionPatterns. \
            collect_regex_matches(phrase, reg, 100,
                                  lambda p, m: m.start(),  # 0 ?
                                  lambda p, m: m.end())  # len(p) ?
        # 'start' - search for company name from the beginning
        patterns = self.pre_process_found_matches(dfs, 'start')
        return patterns

    def match_c_years_word(self, phrase: str) -> List[PatternFound]:
        """
        :param phrase: Copyright 1996 – 2019, Siemens
        :return: {name: '1996 – 2019, Siemens', probability: 100, ...}
        """
        if not self.reg_trigger_words.search(phrase):
            return []

        reg = self.reg_c_years_word
        dfs = CommonDefinitionPatterns. \
            collect_regex_matches(phrase, reg, 100,
                                  lambda p, m: m.start(),
                                  lambda p, m: m.end())  # len(p) ?
        # 'start' - search for company name from the beginning
        patterns = self.pre_process_found_matches(dfs, 'end')
        return patterns

    def pre_process_found_matches(self, matches: List[PatternFound],
                                  company_search_options: str) -> List[CopyrightPatternFound]:
        rst = []
        for match in matches:
            ptrn = CopyrightPatternFound(match)
            # Siemens 1996 – 2019
            # get dates (years)
            years = year_parser.year_parser.get_years_with_coords_from_string(match.name)
            if len(years) == 1:
                ptrn.end_year = years[0][0]
            elif len(years) > 1:
                ptrn.end_year = max(years[0][0], years[1][0])
                ptrn.start_year = min(years[0][0], years[1][0])

            # company name
            company = self.get_company_name_from_match(
                match.name, company_search_options, years)
            if company:
                ptrn.company = company
            rst.append(ptrn)

        return rst

    def get_company_name_from_match(self, text: str,
                                    company_search_options: str,
                                    years: List[Tuple[int, int, int]]) -> str:
        start = 0
        end = -1
        if company_search_options == 'start':
            if len(years) > 0:
                end = years[0][1]
        if company_search_options == 'end':
            if len(years) > 0:
                start = years[-1][2] + 1
        if start == len(text) - 1 or end == 0:
            start = 0
            end = -1

        # try to find company name in source text by 'company_search_options',
        # then, if was not found, find in the whole text
        texts = [text[start: end], text]
        for text in texts:
            words = [w.group().strip(' \t') for w in
                     self.reg_company_name.finditer(text)]
            words = [w for w in words if w]
            phrase = " ".join(words)
            # remove "Copyright" from company name
            phrase = re.sub(self.reg_trigger_words, '', phrase)
            if phrase:
                return phrase

        return ''
