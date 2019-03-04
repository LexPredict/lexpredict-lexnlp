# pylint: unused-argument

import re
from typing import List, Generator
from lexnlp.extract.common.annotations.definition_annotation import DefinitionAnnotation
from lexnlp.extract.common.definitions.common_definition_patterns import CommonDefinitionPatterns
from lexnlp.extract.common.definitions.universal_definition_parser import UniversalDefinitionsParser
from lexnlp.extract.common.pattern_found import PatternFound
from lexnlp.extract.es.language_tokens import EsLanguageTokens
from lexnlp.utils.lines_processing.line_processor import LineSplitParams

# pylint: disable=unused-argument

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
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
    reg_first_word_is = re.compile(r"^.+?(?=es\s+\w+\W+\w+|está\s+\w+\W+\w+)", re.UNICODE)

    @staticmethod
    def match_es_def_by_hereafter(phrase: str) -> List[PatternFound]:
        """
        :param phrase: las instrucciones de uso o instalación del software o todas las descripciones
                       de uso del mismo (de aquí en adelante, la "Documentación");
        :return: {name: 'Documentación', probability: 100, ...}
        """
        reg = SpanishParsingMethods.reg_hereafter
        dfs = CommonDefinitionPatterns. \
            collect_regex_matches_with_quoted_chunks(phrase, reg, 100,
                                                     lambda p, m, e: 0,
                                                     lambda p, m, e: m.start() + e.end(),
                                                     lambda p, m: 0,
                                                     lambda p, m: m.end())
        return dfs

    @staticmethod
    def match_es_def_by_reffered(phrase: str) -> List[PatternFound]:
        """
        :param phrase: En este acuerdo, el término "Software" se refiere a: (i) el programa informático
                       que acompaña a este Acuerdo y todos sus componentes;
        :return: definitions (objects)
        """
        reg = SpanishParsingMethods.reg_reffered
        dfs = CommonDefinitionPatterns. \
            collect_regex_matches_with_quoted_chunks(phrase, reg, 100,
                                                     lambda p, m, e: m.start() + e.start(),
                                                     lambda p, m, e: len(phrase),
                                                     lambda p, m: m.start(),
                                                     lambda p, m: len(p))
        return dfs

    @staticmethod
    def match_first_word_is(phrase: str) -> List[PatternFound]:
        """
        :param phrase: El tabaquismo es la adicción al tabaco, provocada principalmente.
        :return: definitions (objects)
        """
        reg = SpanishParsingMethods.reg_first_word_is
        dfs = CommonDefinitionPatterns.\
            collect_regex_matches_with_quoted_chunks(phrase, reg, 65,
                                                     lambda p, m, e: m.start() + e.start(),
                                                     lambda p, m, e: len(phrase),
                                                     lambda p, m: m.start(),
                                                     lambda p, m: len(p))
        return dfs


def make_es_definitions_parser():
    split_params = LineSplitParams()
    split_params.line_breaks = {'\n', '.', ';', '!', '?'}
    split_params.abbreviations = EsLanguageTokens.abbreviations
    split_params.abbr_ignore_case = True

    functions = [CommonDefinitionPatterns.match_es_def_by_semicolon,
                 CommonDefinitionPatterns.match_acronyms,
                 SpanishParsingMethods.match_es_def_by_hereafter,
                 SpanishParsingMethods.match_es_def_by_reffered,
                 SpanishParsingMethods.match_first_word_is]

    return UniversalDefinitionsParser(functions, split_params)


parser = make_es_definitions_parser()


def get_definitions(text: str, language=None) -> Generator[dict, None, None]:
    dfs = parser.parse(text, language if language else 'es')
    for d in dfs:
        yield d.to_dictionary()


def get_definition_list(text: str, language=None) -> List[DefinitionAnnotation]:
    return parser.parse(text, language if language else 'es')
