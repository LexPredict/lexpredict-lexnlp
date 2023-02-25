__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
from unittest import TestCase

from lexnlp.extract.common.base_path import lexnlp_test_path
from lexnlp.extract.common.ocr_rating.ocr_rating_calculator import build_cs_quad_rating_calculator


class TestOcrGrade(TestCase):
    def test_empty_text(self):
        calc = build_cs_quad_rating_calculator()
        rating = calc.get_rating('', '')
        self.assertEqual(0, rating)

    def test_pretty_text(self):
        file_path = os.path.join(
            lexnlp_test_path, 'lexnlp/extract/common/ocr_grade/pretty_en_file.txt')
        calc = build_cs_quad_rating_calculator()
        rating = calc.get_file_rating(file_path, 'en')
        self.assertGreater(rating, 8)

    def test_lorem_ipsum(self):
        file_path = os.path.join(
            lexnlp_test_path, 'lexnlp/extract/common/ocr_grade/lorem_ipsum.txt')
        calc = build_cs_quad_rating_calculator()
        rating = calc.get_file_rating(file_path, 'en')
        self.assertLess(rating, 7)

    def test_deutsche(self):
        file_path = os.path.join(
            lexnlp_test_path, 'lexnlp/extract/common/ocr_grade/totem_und_tabu.txt')
        calc = build_cs_quad_rating_calculator()
        rating_en = calc.get_file_rating(file_path, 'en')
        self.assertGreater(rating_en, 0)
        self.assertLess(rating_en, 7)

        rating_de = calc.get_file_rating(file_path, 'de')
        self.assertGreater(rating_de, rating_en)
        self.assertGreater(rating_de, 6)
