from typing import Union, List, Tuple, Generator

import pandas as pd

from lexnlp.extract.common.annotations.geo_annotation import GeoAnnotation
from lexnlp.utils.parse_df import get_entities, get_entity_list, DataframeEntityParser

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


get_geoentities = get_entities


get_geoentity_list = get_entity_list


def get_geoentity_annotations(
                        text: str,
                        config: pd.DataFrame,
                        parse_columns: Union[List[str], Tuple[str]] = None,
                        result_columns: Union[dict, None] = None,
                        preformed_entity: Union[dict, None] = None,
                        priority_sort_column: Union[str, None] = None,
                        priority_sort_ascending: bool = True,
                        cell_values_separator: Union[str, None] = ';',
                        unique_column_values: bool = True) -> Generator[GeoAnnotation, None, None]:
    parser = DeGeoentitiesParser()
    yield from parser.get_geoentity_annotations(text,
                                                config,
                                                parse_columns,
                                                result_columns,
                                                preformed_entity,
                                                priority_sort_column,
                                                priority_sort_ascending,
                                                cell_values_separator,
                                                unique_column_values)


class DeGeoentityColumn:
    """
    dataframe_col_name: column in the source Pandas dataframe
    resulted_name: column in resulted set, produced by DataframeEntityParser
    attr_name: GeoAnnotation property name
    """
    def __init__(self,
                 dataframe_col_name: str,
                 resulted_name: str,
                 attr_name: str):
        self.dataframe_col_name = dataframe_col_name
        self.resulted_name = resulted_name or dataframe_col_name
        self.attr_name = attr_name

    def __repr__(self):
        if self.resulted_name:
            return f'{self.dataframe_col_name} ({self.resulted_name}): {self.attr_name}'
        return f'{self.dataframe_col_name}: {self.attr_name}'


class DeGeoentitiesParser:
    # DF column - GeoAnnotation attribute
    default_annotation_columns = \
        [DeGeoentityColumn('Entity ID', '', 'entity_id'),
         DeGeoentityColumn('Entity Category', '', 'entity_category'),
         DeGeoentityColumn('', 'source', 'source'),
         DeGeoentityColumn('German Name', '', 'name'),
         DeGeoentityColumn('Entity Name', '', 'name_en'),
         DeGeoentityColumn('Entity Priority', '', 'entity_priority'),
         DeGeoentityColumn('ISO-3166-2', '', 'iso_3166_2'),
         DeGeoentityColumn('ISO-3166-3', '', 'iso_3166_3'),
         DeGeoentityColumn('Alias', '', 'alias')]

    default_selecting_columns = ["German Name",
                                 "ISO-3166-2",
                                 "ISO-3166-3",
                                 "Alias"]

    def get_geoentities(self,
                     text: str,
                     config: pd.DataFrame,
                     parse_columns: Union[List[str], Tuple[str]] = None,
                     result_columns: Union[dict, None] = None,
                     preformed_entity: Union[dict, None] = None,
                     priority_sort_column: Union[str, None] = None,
                     priority_sort_ascending: bool = True,
                     cell_values_separator: Union[str, None] = ';',
                     unique_column_values: bool = True) -> Generator:

        parse_columns = parse_columns or self.default_selecting_columns

        yield from DataframeEntityParser(dataframe=config,
                                         parse_columns=parse_columns,
                                         result_columns=result_columns,
                                         preformed_entity=preformed_entity,
                                         priority_sort_column=priority_sort_column,
                                         priority_sort_ascending=priority_sort_ascending,
                                         cell_values_separator=cell_values_separator,
                                         unique_column_values=unique_column_values).get_entities(text)

    def get_geoentity_annotations(
                        self,
                        text: str,
                        config: pd.DataFrame,
                        parse_columns: Union[List[str], Tuple[str]] = None,
                        result_columns: List[DeGeoentityColumn] = None,
                        preformed_entity: Union[dict, None] = None,
                        priority_sort_column: Union[str, None] = None,
                        priority_sort_ascending: bool = True,
                        cell_values_separator: Union[str, None] = ';',
                        unique_column_values: bool = True) -> Generator[GeoAnnotation, None, None]:

        parse_columns = parse_columns or self.default_selecting_columns
        result_columns = result_columns or self.default_annotation_columns
        df_result_columns = {c.dataframe_col_name: c.dataframe_col_name
                             for c in self.default_annotation_columns
                             if c.dataframe_col_name}

        for ent in get_entities(text,
                                config=config,
                                parse_columns=parse_columns,
                                result_columns=df_result_columns,
                                preformed_entity=preformed_entity,
                                priority_sort_column=priority_sort_column,
                                priority_sort_ascending=priority_sort_ascending,
                                cell_values_separator=cell_values_separator,
                                unique_column_values=unique_column_values):
            ant = GeoAnnotation(coords=(ent['location_start'], ent['location_end']),
                                locale='de')
            for col in result_columns:
                setattr(ant, col.attr_name,
                        ent[col.resulted_name or col.dataframe_col_name])
            yield ant
