__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

import pandas as pd
from typing import List, Generator

from lexnlp.extract.de.language_tokens import DeLanguageTokens
from lexnlp.extract.common.annotations.law_annotation import LawAnnotation
from lexnlp.utils.parse_df import DataframeEntityParser
from lexnlp.utils.lines_processing.line_processor import LineSplitParams, LineProcessor


ANNOTATION_SET_NAME = 'Laws and Rules'


class LawsParser:
    def __init__(self,
                 gesetze_df: pd.DataFrame,
                 verordnungen_df: pd.DataFrame,
                 concept_df: pd.DataFrame):
        self.locale = ''
        parse_columns = ('Kurztitel', 'Titel', 'Abkürzung')
        dependent_columns = {'Titel': 'External Reference Normalized'}
        preformed_entity = {'External Reference Type': 'Laws and Rules',
                            'External Reference Source': 'BaFin',
                            'External Reference Issuing Country': 'Germany'}
        split_params = LineSplitParams()
        split_params.line_breaks = {'.', ';', '!', '?'}
        split_params.abbreviations = DeLanguageTokens.abbreviations
        split_params.abbr_ignore_case = True
        proc = LineProcessor(line_split_params=split_params)

        self.gesetze_parser = DataframeEntityParser(
            gesetze_df,
            parse_columns,
            result_columns=dependent_columns,
            preformed_entity=preformed_entity,
            line_processor=proc)

        self.verordnungen_parser = DataframeEntityParser(
            verordnungen_df,
            parse_columns,
            result_columns=dependent_columns,
            preformed_entity=preformed_entity,
            line_processor=proc)

        parse_columns = ('b',)
        dependent_columns = {'b': 'External Reference Normalized',
                             'a': 'External Reference Type'}
        preformed_entity.pop('External Reference Type')

        self.concept_parser = DataframeEntityParser(
            concept_df,
            parse_columns,
            result_columns=dependent_columns,
            preformed_entity=preformed_entity,
            line_processor=proc)

    def parse(self, text: str, locale: str = None) -> List[LawAnnotation]:
        res = []
        self.locale = locale if locale else 'de'
        res.extend(self.gesetze_parser.get_entity_list(text))
        res.extend(self.verordnungen_parser.get_entity_list(text))
        res.extend(self.concept_parser.get_entity_list(text))

        res_formatted = []  # type: List[LawAnnotation]
        for i in res:
            coords = (i.pop('location_start'), i.pop('location_end'))
            text = i.pop('source')
            ant = LawAnnotation(name=text, coords=coords,
                                text=text, locale=self.locale)
            # new_item.update(i)
            res_formatted.append(ant)
        return res_formatted


parser = None  # type: LawsParser


def initialize_parser(gesetze_df: pd.DataFrame,
                      verordnungen_df: pd.DataFrame,
                      concept_df: pd.DataFrame) -> LawsParser:
    return LawsParser(gesetze_df, verordnungen_df, concept_df)


def get_law_annotations(text: str, language: str = None) -> \
        Generator[LawAnnotation, None, None]:
    if not parser:
        return None
    yield from parser.parse(text, language if language else 'de')


def get_laws(text: str, language: str = None) -> Generator[dict, None, None]:
    if not parser:
        return None
    ants = parser.parse(text, language if language else 'de')
    for ant in ants:
        yield ant.to_dictionary()


def get_law_list(text: str, language: str = None) -> List[LawAnnotation]:
    if not parser:
        return []
    return parser.parse(text, language if language else 'de')
