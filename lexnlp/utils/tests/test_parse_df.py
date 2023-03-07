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

    def get_entries(self, text: str, columns=None):
        columns = columns or self.default_columns
        parser = DataframeEntityParser(dataframe=entity_df,
                                       parse_columns=columns)
        return list(parser.get_entities(text))
