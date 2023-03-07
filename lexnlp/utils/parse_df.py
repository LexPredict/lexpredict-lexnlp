__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
from typing import Generator, List, Union, Tuple

import pandas as pd

from lexnlp.utils.lines_processing.line_processor import LineProcessor


class DataframeEntityParser:
    """
    Class that provides ability to extract entities from a text
    having some collection of entities formed as dataframe.
    By default it means that dataframe has UNIQUE values in those columns you use for search.
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
      - cell_values_separator: str or None - multiple values in datafame cell separated by
        that separator
      - unique_column_values: bool - dataframe columns have unique values

    E.g.:
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

    def __init__(self,
                 dataframe,
                 parse_columns,
                 result_columns=None,
                 preformed_entity=None,
                 priority_sort_column=None,
                 priority_sort_ascending=True,
                 cell_values_separator=';',
                 unique_column_values=True,
                 line_processor: LineProcessor = None):
        self.dataframe = dataframe.fillna('')
        self.parse_columns = parse_columns
        self.result_columns = result_columns or {}
        self.preformed_entity = preformed_entity or {}
        self.priority_sort_column = priority_sort_column
        self.priority_sort_ascending = priority_sort_ascending
        self.cell_values_separator = cell_values_separator
        self.unique_column_values = unique_column_values
        self.line_processor = line_processor

        collection_patterns = \
            [(col_name, self.get_collection_ptn(self.dataframe[col_name].values))
            for col_name in parse_columns if col_name]
        self.collection_patterns = {
                c[0]: c[1] for c in collection_patterns if c[1]
            }

    def get_collection_ptn(self, collection):
        """
        Convert list of values to regex pattern
        :param collection: list of entities to search in
        :return: compilled regex pattern
        """
        collection = [c for c in collection if c]
        if not collection:
            return None

        ptn = self.SEARCH_PTN.format(
            '|'.join(re.escape(j) for i in collection for j in i.split(self.cell_values_separator) if i))
        return re.compile(ptn)

    def get_single_result(self, rows):
        """
        By default we mean that all values we filter by in dataframe are UNIQUE, so just take 1st
        Implement your own logic to choose from multiple matched dataframe rows
        """
        if self.priority_sort_column:
            rows = rows.sort_values(by=self.priority_sort_column,
                                    ascending=self.priority_sort_ascending)
        return rows.iloc[0]

    def get_formed_entity(self, match, col_name):
        """
        Get formed entity from matched row in dataframe
        :param match: re.match object
        :param col_name: df column name
        :return: dict
        """
        matched_str = match.groups()[0]
        location_start, location_end = match.span()
        formed_entity = {
            'location_start': location_start,
            'location_end': location_end,
            'source': matched_str
        }
        if self.result_columns:
            matched_rows = self.dataframe[self.dataframe[col_name].str.contains(r'(?:^|;){}(?:$|;)'.format(matched_str), regex=True)]
            if self.unique_column_values:
                matched_row = self.get_single_result(matched_rows)
                for _col_name, new_col_name in self.result_columns.items():
                    formed_entity[new_col_name] = matched_row[_col_name]
            else:
                formed_entity["entities"] = []
                for _, matched_row in matched_rows.iterrows():
                    sub_entity = {}
                    for _col_name, new_col_name in self.result_columns.items():
                        sub_entity[new_col_name] = matched_row[_col_name]
                    formed_entity["entities"].append(sub_entity)

        formed_entity.update(self.preformed_entity)
        return formed_entity

    def get_entities(self, text: str) -> Generator[dict, None, None]:
        if self.line_processor:
            # split text on sentences and remove linebreaks within sentences
            for sent in self.line_processor.split_text_on_line_with_endings(text):
                for ent in self.get_entities_from_text(sent.text):
                    ent['location_start'] += sent.start
                    ent['location_end'] += sent.start
                    yield ent
        else:
            yield from self.get_entities_from_text(text)

    def get_entities_from_text(self, text: str) -> Generator[dict, None, None]:
        sent_text = text.replace('\n', ' ')
        for col_name, collection_ptn in self.collection_patterns.items():
            for match in collection_ptn.finditer(sent_text):
                yield self.get_formed_entity(match, col_name)

    def get_entity_list(self, text):
        return list(self.get_entities(text))


def get_entities(text: str,
                 config: pd.DataFrame,
                 parse_columns: Union[List[str], Tuple[str]],
                 result_columns: Union[dict, None] = None,
                 preformed_entity: Union[dict, None] = None,
                 priority_sort_column: Union[str, None] = None,
                 priority_sort_ascending: bool = True,
                 cell_values_separator: Union[str, None] = ';',
                 unique_column_values: bool = True) -> Generator[dict, None, None]:
    """
    Simple wrapper around DataframeEntityParser
    """
    yield from DataframeEntityParser(dataframe=config,
                                     parse_columns=parse_columns,
                                     result_columns=result_columns,
                                     preformed_entity=preformed_entity,
                                     priority_sort_column=priority_sort_column,
                                     priority_sort_ascending=priority_sort_ascending,
                                     cell_values_separator=cell_values_separator,
                                     unique_column_values=unique_column_values).get_entities(text)


def get_entity_list(text: str,
                    config: pd.DataFrame,
                    parse_columns: Union[List[str], Tuple[str]],
                    result_columns: Union[dict, None] = None,
                    preformed_entity: Union[dict, None] = None,
                    priority_sort_column: Union[str, None] = None,
                    priority_sort_ascending: bool = True,
                    cell_values_separator: Union[str, None] = ';',
                    unique_column_values: bool = True) -> List:
    """
    Simple wrapper around DataframeEntityParser
    """
    return DataframeEntityParser(dataframe=config,
                                 parse_columns=parse_columns,
                                 result_columns=result_columns,
                                 preformed_entity=preformed_entity,
                                 priority_sort_column=priority_sort_column,
                                 priority_sort_ascending=priority_sort_ascending,
                                 cell_values_separator=cell_values_separator,
                                 unique_column_values=unique_column_values).get_entity_list(text)
