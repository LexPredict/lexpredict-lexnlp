from unittest import TestCase

from lexnlp.utils.lines_processing.phrase_finder import PhraseFinder


class TestPhraseFinder(TestCase):
    def test_abbreviation(self):
        text = "In C.D. Ill. we should find"
        finder = PhraseFinder(['C.D. Ill.'])
        rst = finder.find_word(text, True)
        self.assertEqual(1, len(rst))

        finder = PhraseFinder(['C.D. Ill.', 'sh', 'should', 'find'])
        rst = finder.find_word(text, True)
        self.assertEqual(3, len(rst))
