import re
from typing import Generator, List, Union, Tuple

import numpy as np
import pandas as pd


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.4"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DataframeEntityParser(object):
    """
    Class that provides ability to extract entities from a text
    having some collection of entities formed as dataframe.
    Returns dict of start/end positions of found item in a text
    and other user-defined key-value pairs

    Params:
      - dataframe: pandas.DataFrame with entities collection
      - parse_columns: list or tuple - these columns will be used to search their values in a text
      - result_columns: dict - map like {'dataframe column name to take a value
        corresponding with extracted entity': 'new_column_name'}
      - preformed_entity: dict - initial, static key-value pairs to use for each extracted entity
      - priority_sort_column: str - column name to sort by and get first match
        if multiple results found, otherwise the first matched row will be used
      - priority_sort_ascending: bool - sort order for priority_sort_column

    Eg:
        >>> parse_columns = ('Kurztitel', 'Titel', 'Abkürzung')
        >>> result_columns = {'Titel': 'name'}
        >>> preformed_entity = {'entity_type': 'Laws and Rules',
        >>>                     'source': 'BaFin',
        >>>                     'country': 'Germany'}
        >>> sort_column = 'Titel'
        >>> items = DataframeEntityParser(
        >>>     df, parse_columns, result_columns, preformed_entity, sort_column).parse(text)
    """

    SEARCH_PTN = r'(?:^|\W)({})(?:\W|$)'

    def __init__(self, dataframe, parse_columns, result_columns=None, preformed_entity=None,
                 priority_sort_column=None, priority_sort_ascending=True):
        self.dataframe = dataframe.fillna('')
        self.parse_columns = parse_columns
        self.result_columns = result_columns or {}
        self.preformed_entity = preformed_entity or {}
        self.priority_sort_column = priority_sort_column
        self.priority_sort_ascending = priority_sort_ascending
        self.collection_patterns = {
            col_name: self.get_collection_ptn(self.dataframe[col_name].values) for col_name in
            parse_columns}

    def get_collection_ptn(self, collection):
        ptn = self.SEARCH_PTN.format(
            '|'.join(re.escape(i) for i in collection if i != ''))
        return re.compile(ptn)

    def get_single_result(self, rows):
        if self.priority_sort_column:
            rows = rows.sort_values(by=self.priority_sort_column,
                                    ascending=self.priority_sort_ascending)
        return rows.iloc[0]

    def get_formed_entity(self, match, col_name):
        matched_str = match.groups()[0]
        location_start, location_end = match.span()
        formed_entity = {
            "location_start": location_start,
            "location_end": location_end,
            "source": matched_str
        }
        if self.result_columns:
            matched_rows = self.dataframe[self.dataframe[col_name] == matched_str]
            matched_row = self.get_single_result(matched_rows)
            for _col_name, new_col_name in self.result_columns.items():
                formed_entity[new_col_name] = matched_row[_col_name]
        formed_entity.update(self.preformed_entity)
        return formed_entity

    def get_entities(self, text):
        for col_name, collection_ptn in self.collection_patterns.items():
            for match in collection_ptn.finditer(text):
                yield self.get_formed_entity(match, col_name)

    def get_entity_list(self, text):
        return list(self.get_entities(text))


def get_entities(text: str,
                 config: pd.DataFrame,
                 parse_columns: Union[List[str], Tuple[str]],
                 result_columns: Union[dict, None] = None,
                 preformed_entity: Union[dict, None] = None,
                 priority_sort_column: Union[str, None] = None,
                 priority_sort_ascending: bool = True) -> Generator:
    """
    Simple wrapper around DataframeEntityParser
    """
    yield from DataframeEntityParser(dataframe=config,
                                     parse_columns=parse_columns,
                                     result_columns=result_columns,
                                     preformed_entity=preformed_entity,
                                     priority_sort_column=priority_sort_column,
                                     priority_sort_ascending=priority_sort_ascending).get_entities(text)


def get_entity_list(text: str,
                    config: pd.DataFrame,
                    parse_columns: Union[List[str], Tuple[str]],
                    result_columns: Union[dict, None] = None,
                    preformed_entity: Union[dict, None] = None,
                    priority_sort_column: Union[str, None] = None,
                    priority_sort_ascending: bool = True) -> List:
    """
    Simple wrapper around DataframeEntityParser
    """
    return DataframeEntityParser(dataframe=config,
                                 parse_columns=parse_columns,
                                 result_columns=result_columns,
                                 preformed_entity=preformed_entity,
                                 priority_sort_column=priority_sort_column,
                                 priority_sort_ascending=priority_sort_ascending).get_entity_list(text)
