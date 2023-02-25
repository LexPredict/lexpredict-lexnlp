__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.en.preprocessing.span_tokenizer import SpanTokenizer
from lexnlp.extract.en.introductory_words_detector import IntroductoryWordsDetector


class TestIntroductoryWordsDetector(TestCase):
    def test_negative(self):
        term = 'Physically Completed'
        term_pos = list(SpanTokenizer.get_token_spans(term))
        term_clear = \
            IntroductoryWordsDetector.remove_term_introduction(term, term_pos)
        self.assertEqual(term, term_clear)

    def test_negative_combined(self):
        term = 'Combined EDITT Deficit Alpha Beta Gamma Cappa'
        term_pos = list(SpanTokenizer.get_token_spans(term))
        term_clear = \
            IntroductoryWordsDetector.remove_term_introduction(term, term_pos)
        self.assertEqual(term, term_clear)

    def test_positive(self):
        term = 'so called "champerty\''
        term_pos = list(SpanTokenizer.get_token_spans(term))
        term_clear = \
            IntroductoryWordsDetector.remove_term_introduction(term, term_pos)
        self.assertEqual('"champerty\'', term_clear)
