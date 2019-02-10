import re
from typing import List
from lexnlp.extract.common.universal_definition_parser import CommonDefinitionPatterns
from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.extract.es.definitions import DefinitionMatch, UniversalDefinitionsParser
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DeutscheParsingMethods:
    """
    the class contains methods with the same signature:
        def method_name(phrase: str) -> List[DefinitionMatch]:
    the methods are used for finding definition "candidates"
    """
    reg_im_sinne = re.compile("(.+(?=im Sinne.+[\\s\\b]sind[\\s\\b]))|(.+(?=im Sinne.+[\\s\\b]ist[\\s\\b]))",
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
    def match_im_sinne(phrase: str) -> List[DefinitionMatch]:
        """
        :param phrase: Vermögensgegenstände im Sinne dieses Gesetzes sind unbewegliches Vermögen im Sinne des Absatzes 8, ferner zu dessen Bewirtschaftung;
        :return: {name: 'Vermögensgegenstände', probability: 100, ...}
        """
        reg = DeutscheParsingMethods.reg_im_sinne
        prob = 100
        defs = []
        for match in reg.finditer(phrase):
            quoted_matches = \
                CommonDefinitionPatterns.peek_quoted_part(match,
                                                        lambda m, e: 0,
                                                        lambda m, e: len(phrase),
                                                        prob)
            if len(quoted_matches) > 0:
                defs += quoted_matches
                continue

            df = DefinitionMatch()
            df.name = match.group().strip()
            df.start = 0
            df.end = len(phrase)
            df.probability = prob
            defs.append(df)

        return defs

    @staticmethod
    def match_ist_jeder(phrase: str) -> List[DefinitionMatch]:
        """
        :param phrase: ist Diensteanbieter jeder natürliche oder juristische Person, die eigene oder fremde Telemedien zur Nutzung bereithält oder den Zugang zur Nutzung vermittelt;
        :return: {name: 'Diensteanbieter', probability: 100, ...}
        """
        prob = 80
        defs = []
        for reg in DeutscheParsingMethods.reg_ist_jeder:
            for match in reg.finditer(phrase):
                quoted_matches = \
                    CommonDefinitionPatterns.peek_quoted_part(match,
                                                            lambda m, e: 0,
                                                            lambda m, e: len(phrase),
                                                            prob)
                if len(quoted_matches) > 0:
                    defs += quoted_matches
                    continue

                df = DefinitionMatch()
                df.name = match.group().strip()
                df.start = 0
                df.end = len(phrase)
                df.probability = prob
                defs.append(df)

        return defs


def make_de_definitions_parser():
    split_params = LineSplitParams()
    split_params.line_breaks = {'\n', '.', ';', '!', '?'}
    split_params.abbreviations = DeLanguageTokens.abbreviations
    split_params.abbr_ignore_case = True

    functions = [CommonDefinitionPatterns.match_es_def_by_semicolon,
                 DeutscheParsingMethods.match_ist_jeder,
                 DeutscheParsingMethods.match_im_sinne]

    parser = UniversalDefinitionsParser(functions, split_params)
    parser.prohibited_words = {w for w in DeLanguageTokens.articles + DeLanguageTokens.conjunctions}
    return parser


parser = make_de_definitions_parser()


def get_definition_list(text: str, language=None):
    return parser.parse(text)


def get_definitions(text: str, language=None):
    dfs = parser.parse(text)
    for d in dfs:
        yield d