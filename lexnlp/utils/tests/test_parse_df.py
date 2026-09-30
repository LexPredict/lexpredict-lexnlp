__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import io
import pandas as pd
from unittest import TestCase

from lexnlp.utils.parse_df import DataframeEntityParser


sample_csv = '''
"name","alias"
"Peppa","Peps"
"George",""
"Tati Purcelus",""
"Mamica Purceluss","mum"
'''

file_like = io.StringIO(sample_csv)

entity_df = pd.read_csv(file_like)


class TestParseDataframe(TestCase):
    default_columns = ['name', 'alias']

    def test_get_by_name(self):
        ents = self.get_entries('Sunt purcelusa Peppa. El e frateul al meu George, iar ea e Tati Purcelus.')
        self.assertEqual(3, len(ents))

    def test_get_by_alias(self):
        ents = self.get_entries('mum, Peps si George merg la plimbare impreuna.')
        self.assertEqual(3, len(ents))

    def test_spans_exclude_boundaries_and_allow_adjacent_entities(self):
        text = 'Peppa,George'
        ents = self.get_entries(text, columns=['name'])

        self.assertEqual(
            [
                {
                    'location_start': 0,
                    'location_end': 5,
                    'source': 'Peppa',
                },
                {
                    'location_start': 6,
                    'location_end': 12,
                    'source': 'George',
                },
            ],
            ents,
        )
        for ent in ents:
            self.assertEqual(
                ent['source'],
                text[ent['location_start']:ent['location_end']],
            )

    def test_longest_entity_wins_at_the_same_position(self):
        dataframe = pd.DataFrame({'name': ['Act', 'Act One']})
        parser = DataframeEntityParser(dataframe=dataframe, parse_columns=['name'])

        self.assertEqual(
            [{
                'location_start': 0,
                'location_end': 7,
                'source': 'Act One',
            }],
            parser.get_entity_list('Act One applies.'),
        )

    def test_constructor_splits_each_raw_cell_once(self):
        class CountingParser(DataframeEntityParser):
            def __init__(self, *args, **kwargs):
                self.split_values = []
                super().__init__(*args, **kwargs)

            def _split_cell_value(self, value):
                self.split_values.append(value)
                return super()._split_cell_value(value)

        dataframe = pd.DataFrame({'name': ['Alpha;A', 'Beta;B']})
        parser = CountingParser(dataframe=dataframe, parse_columns=['name'])

        self.assertEqual(['Alpha;A', 'Beta;B'], parser.split_values)
        self.assertEqual(
            r'(?<!\w)(Alpha|Beta|A|B)(?!\w)',
            parser.collection_patterns['name'].pattern,
        )
        self.assertEqual({}, parser._row_positions_by_column)

        enriched_parser = CountingParser(
            dataframe=dataframe,
            parse_columns=['name'],
            result_columns={'name': 'matched_name'},
        )
        self.assertEqual(['Alpha;A', 'Beta;B'], enriched_parser.split_values)
        self.assertEqual(
            {'A': [0], 'Alpha': [0], 'B': [1], 'Beta': [1]},
            enriched_parser._row_positions_by_column['name'],
        )
        self.assertEqual(
            [{
                'location_start': 6,
                'location_end': 7,
                'source': 'B',
                'matched_name': 'Beta;B',
            }],
            enriched_parser.get_entity_list('Found B.'),
        )

        parser.split_values.clear()
        pattern = parser.get_collection_ptn(['Gamma;G'])
        self.assertEqual(['Gamma;G'], parser.split_values)
        self.assertEqual(r'(?<!\w)(Gamma|G)(?!\w)', pattern.pattern)

    def get_entries(self, text: str, columns=None):
        columns = columns or self.default_columns
        parser = DataframeEntityParser(dataframe=entity_df,
                                       parse_columns=columns)
        return list(parser.get_entities(text))
