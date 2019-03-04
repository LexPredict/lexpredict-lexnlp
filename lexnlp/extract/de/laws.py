import pandas as pd
from typing import List, Generator
from lexnlp.extract.common.annotations.law_annotation import LawAnnotation
from lexnlp.utils.parse_df import DataframeEntityParser


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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

        self.gesetze_parser = DataframeEntityParser(
            gesetze_df, parse_columns, dependent_columns, preformed_entity)

        self.verordnungen_parser = DataframeEntityParser(
            verordnungen_df, parse_columns, dependent_columns, preformed_entity)

        parse_columns = ('b',)
        dependent_columns = {'b': 'External Reference Normalized',
                             'a': 'External Reference Type'}
        preformed_entity.pop('External Reference Type')

        self.concept_parser = DataframeEntityParser(
            concept_df, parse_columns, dependent_columns, preformed_entity)

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
            ant = LawAnnotation(name=text, coords=coords, text=text, locale=self.locale)
            # new_item.update(i)
            res_formatted.append(ant)
        return res_formatted


parser = None  # type: LawsParser


def initialize_parser(gesetze_df: pd.DataFrame,
                      verordnungen_df: pd.DataFrame,
                      concept_df: pd.DataFrame) -> LawsParser:
    return LawsParser(gesetze_df, verordnungen_df, concept_df)


def get_laws(text: str, language: str = None) -> Generator[dict, None, None]:
    if not parser:
        return None
    ants = parser.parse(text, language if language else 'de')
    for ant in ants:
        yield ant.to_dictionary()


def get_law_list(text: str, language: str = None) -> List[LawAnnotation]:
    if not parser:
        return []  # type: List[LawAnnotation]
    return parser.parse(text, language if language else 'de')
