import re
from typing import List
from lexnlp.extract.common.universal_definition_parser import UniversalDefinitionsParser, DefinitionMatch, CommonDefinitionPatterns
from lexnlp.extract.es.language_tokens import EsLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SpanishParsingMethods:
    """
    the class contains methods with the same signature:
        def method_name(phrase: str) -> List[DefinitionMatch]:
    the methods are used for finding definition "candidates"
    """
    reg_hereafter = re.compile("(?<=(en adelante[,\\s]))[\\w\\s*\\\"*]+", re.UNICODE)
    reg_reffered = re.compile("^.+(?=se refiere)", re.UNICODE)

    @staticmethod
    def match_es_def_by_hereafter(phrase: str) -> List[DefinitionMatch]:
        """
        :param phrase: las instrucciones de uso o instalación del software o todas las descripciones de uso del mismo (de aquí en adelante, la "Documentación");
        :return: {name: 'Documentación', probability: 100, ...}
        """
        reg = SpanishParsingMethods.reg_hereafter
        reg_quoted = CommonDefinitionPatterns.reg_quoted
        prob = 100
        defs = []

        for match in reg.finditer(phrase):
            for match in reg.finditer(phrase):
                quoted_matches = \
                    CommonDefinitionPatterns.peek_quoted_part(match,
                                                              lambda m, e: 0,
                                                              lambda m, e: m.start() + e.end(),
                                                              prob)
                if len(quoted_matches) > 0:
                    defs += quoted_matches
                    continue

            df = DefinitionMatch()
            df.name = match.group()
            df.start = 0
            df.end = match.end()
            df.probability = prob
            defs.append(df)

        return defs

    @staticmethod
    def match_es_def_by_reffered(phrase: str) -> List[DefinitionMatch]:
        """
        :param phrase: En este acuerdo, el término "Software" se refiere a: (i) el programa informático que acompaña a este Acuerdo y todos sus componentes;
        :return:
        """
        reg = SpanishParsingMethods.reg_reffered
        reg_quoted = CommonDefinitionPatterns.reg_quoted
        prob = 100
        defs = []

        for match in reg.finditer(phrase):
            quoted_matches = \
                CommonDefinitionPatterns.peek_quoted_part(match,
                                                          lambda m, e: m.start() + e.start(),
                                                          lambda m, e: len(phrase),
                                                          prob)
            if len(quoted_matches) > 0:
                defs += quoted_matches
                continue

            df = DefinitionMatch()
            df.name = match.group()
            df.start = match.start()
            df.end = len(phrase)
            df.probability = prob
            defs.append(df)

        return defs

def make_es_definitions_parser():
    split_params = LineSplitParams()
    split_params.line_breaks = {'\n', '.', ';', '!', '?'}
    split_params.abbreviations = EsLanguageTokens.abbreviations
    split_params.abbr_ignore_case = True

    functions = [CommonDefinitionPatterns.match_es_def_by_semicolon,
                 SpanishParsingMethods.match_es_def_by_hereafter,
                 SpanishParsingMethods.match_es_def_by_reffered]

    parser = UniversalDefinitionsParser(functions, split_params)
    return parser


parser = make_es_definitions_parser()


def get_definition_list(text: str, language=None):
    return parser.parse(text)


def get_definitions(text: str, language=None):
    dfs = parser.parse(text)
    for d in dfs:
        yield d
