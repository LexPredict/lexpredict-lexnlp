__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

import nltk

from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder
from lexnlp.extract.en.preprocessing.span_tokenizer import SpanTokenizer


class TestSpanTokenizer(TestCase):
    def test_split_simplest_case(self):
        text = 'John was named after his dog'
        spans = list(SpanTokenizer.get_token_spans(text))
        self.assertGreater(len(spans), 3)

    def test_split_plain(self):
        text = 'He took my heart in East Atlanta, nah-nah-nah'
        spans = list(SpanTokenizer.get_token_spans(text))
        self.assertGreater(len(spans), 3)
        self.assertEqual(('He', 'PRP', 0, 1), spans[0])
        self.assertEqual(('nah-nah-nah', 'JJ', 34, 44), spans[8])

    def test_split_dont(self):
        text = "You don't do it, man!"
        spans = list(SpanTokenizer.get_token_spans(text))
        self.assertEqual(8, len(spans))
        self.assertEqual(17, spans[6][2])
        self.assertEqual(19, spans[6][3])

    def test_split_with_quotes(self):
        text = 'He took my heart in "East Atlanta"\n, nah-nah-nah'
        spans = list(SpanTokenizer.get_token_spans(text))
        self.assertEqual(('"', '``', 20, 20), spans[5])
        self.assertEqual(('nah-nah-nah', 'JJ', 37, 47), spans[10])

        words = nltk.word_tokenize(text)
        tokens = nltk.pos_tag(words)
        phrases = [t[0] for t in tokens]

        spans_alt = PhrasePositionFinder.find_phrase_in_source_text(
            text, phrases)
        self.assertEqual(('``', 20, 21), spans_alt[5])
        self.assertEqual(('nah-nah-nah', 37, 48), spans_alt[10])
