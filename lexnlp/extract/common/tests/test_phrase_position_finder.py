from unittest import TestCase
from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestPhraseFinder(TestCase):
    def test_exact_entry(self):
        text = 'The Treebank tokenizer uses regular  expressions to tokenize text as in Penn Treebank.'
        phrases = ['regular  expressions']
        tagged = PhrasePositionFinder.find_phrase_in_source_text(text, phrases)[0]
        pos = tagged[1]
        self.assertEqual(text.find(phrases[0]), pos)

    def test_extra_spaced_entry(self):
        text = 'The Treebank tokenizer uses regular(expressions) to tokenize text as in Penn Treebank.'
        phrases = ['regular (expressions)']
        tagged = PhrasePositionFinder.find_phrase_in_source_text(text, phrases)[0]
        self.assertEqual(45-17, tagged[1])

    def test_corrupted_entry(self):
        text = 'The Treebank tokenizer uses regular(expressions) to tokenize text as in Penn Treebank.'
        phrases = ['regular expressions']
        tagged = PhrasePositionFinder.find_phrase_in_source_text(text, phrases)[0]
        self.assertEqual(0, tagged[1])

    def test_similar_entries(self):
        text = 'aa aaa aaa aaaaa aa aaa aa'
        tagged = PhrasePositionFinder.find_phrase_in_source_text(text, ['aaa', 'aa'])
        self.assertEqual((3, 7), (tagged[0][1], tagged[1][1]))

    def test_tagging_non_uni_quotes(self):
        text = '(each an “Obligation” and collectively, the “Obligations”)'
        tagged = PhrasePositionFinder.find_phrase_in_source_text(
            text, ['"Obligation"', '"Obligations"'], 0, 58)
        self.assertEqual((9, 44), (tagged[0][1], tagged[1][1]))
