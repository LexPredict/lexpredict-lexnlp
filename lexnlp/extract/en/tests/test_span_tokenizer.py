from unittest import TestCase

from lexnlp.extract.en.preprocessing.span_tokenizer import SpanTokenizer

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestSpanTokenizer(TestCase):
    def test_split_square(self):
        text = 'He took my heart in East Atlanta, nah-nah-nah'
        spans = list(SpanTokenizer.get_token_spans(text))
        self.assertGreater(len(spans), 3)
        self.assertEqual(('He', 'PRP', 0, 1), spans[0])
        self.assertEqual(('nah-nah-nah', 'JJ', 34, 44), spans[8])

    def test_split_with_quotes(self):
        #text = 'He took my heart in "East Atlanta"\n, nah-nah-nah'
        #text = 'John also likes so called blue house at the end of the street.'
        text = 'John was named after his dog'
        spans = list(SpanTokenizer.get_token_spans(text))
        self.assertGreater(len(spans), 3)
