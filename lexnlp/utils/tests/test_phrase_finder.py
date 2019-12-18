from unittest import TestCase

from lexnlp.utils.lines_processing.phrase_finder import PhraseFinder

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestPhraseFinder(TestCase):
    def test_abbreviation(self):
        text = "In C.D. Ill. we should find"
        finder = PhraseFinder(['C.D. Ill.'])
        rst = finder.find_word(text, True)
        self.assertEqual(1, len(rst))

        finder = PhraseFinder(['C.D. Ill.', 'sh', 'should', 'find'])
        rst = finder.find_word(text, True)
        self.assertEqual(3, len(rst))
