# pylint: disable=unused-argument

import re
from typing import List, Generator
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.common.definitions.common_definition_patterns import CommonDefinitionPatterns
from lexnlp.extract.common.definitions.universal_definition_parser import UniversalDefinitionsParser
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DeutscheParsingMethods:
    """
    the class contains methods with the same signature:
        def method_name(phrase: str) -> List[DefinitionMatch]:
    the methods are used for finding definition "candidates"
    """
    reg_im_sinne = re.compile(r"(.+(?=im Sinne.+[\s\b]sind[\s\b]))|(.+(?=im Sinne.+[\s\b]ist[\s\b]))",
                              re.UNICODE | re.IGNORECASE)
    ist_sind = ['ist', 'sind']
    ist_break_words = DeLanguageTokens.articles + ['jede']
    reg_ist_jeder = []

    # region STATICINIT
    if not reg_ist_jeder:
        articles_ptrn = "|".join(["\\s%s" % w for w in ist_break_words])
        for sw in ist_sind:
            reg_ist_jeder.append(re.compile(
                "(?<=\\b%s\\s).+?(?=\\s%s|,|;|$)" % (sw, articles_ptrn),
                re.UNICODE | re.IGNORECASE))
    # endregion

    @staticmethod
    def match_im_sinne(phrase: str) -> List[PatternFound]:
        """
        :param phrase: Vermögensgegenstände im Sinne dieses Gesetzes sind unbewegliches Vermögen im Sinne des Absatzes 8, ferner zu dessen Bewirtschaftung;
        :return: {name: 'Vermögensgegenstände', probability: 100, ...}
        """
        reg = DeutscheParsingMethods.reg_im_sinne
        dfs = CommonDefinitionPatterns. \
            collect_regex_matches_with_quoted_chunks(phrase, reg, 100,
                                                     lambda p, m, e: 0,
                                                     lambda p, m, e: len(phrase),
                                                     lambda p, m: 0,
                                                     lambda p, m: len(p))
        return dfs

    @staticmethod
    def match_ist_jeder(phrase: str) -> List[PatternFound]:
        """
        :param phrase: ist Diensteanbieter jeder natürliche oder juristische Person, die eigene oder fremde Telemedien zur Nutzung bereithält oder den Zugang zur Nutzung vermittelt;
        :return: {name: 'Diensteanbieter', probability: 100, ...}
        """
        defs = []
        for reg in DeutscheParsingMethods.reg_ist_jeder:
            dfs = CommonDefinitionPatterns. \
                collect_regex_matches_with_quoted_chunks(phrase, reg, 80,
                                                         lambda p, m, e: 0,
                                                         lambda p, m, e: len(phrase),
                                                         lambda p, m: 0,
                                                         lambda p, m: len(p))
            defs += dfs
        return defs


def make_de_definitions_parser():
    split_params = LineSplitParams()
    split_params.line_breaks = {'\n', '.', ';', '!', '?'}
    split_params.abbreviations = DeLanguageTokens.abbreviations
    split_params.abbr_ignore_case = True

    functions = [CommonDefinitionPatterns.match_es_def_by_semicolon,
                 CommonDefinitionPatterns.match_acronyms,
                 DeutscheParsingMethods.match_ist_jeder,
                 DeutscheParsingMethods.match_im_sinne]

    p = UniversalDefinitionsParser(functions, split_params)
    p.prohibited_words = {w for w in DeLanguageTokens.articles + DeLanguageTokens.conjunctions}
    return p


parser = make_de_definitions_parser()


def get_definitions(text: str, language=None) -> Generator[dict, None, None]:
    dfs = parser.parse(text, language if language else 'de')
    for d in dfs:
        yield d.to_dictionary()


def get_definition_list(text: str, language=None) -> List[DefinitionAnnotation]:
    return parser.parse(text, language if language else 'de')
