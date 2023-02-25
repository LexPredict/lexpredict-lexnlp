__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase
import numpy as np

from lexnlp.extract.ml.detector.phrase_constructor import PhraseConstructor


class TestPhraseConstructor(TestCase):
    def test_join_class_nonstrict_01(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(8)]
        predicted = np.array([0, 0, 1, 1, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_class(
            tokens, predicted, strict=False))
        self.assertEqual(1, len(phrases))
        self.assertEqual((20, 69), phrases[0])

    def test_join_class_nonstrict_02(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(10)]
        predicted = np.array([0, 0, 0, 1, 0, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_class(
            tokens, predicted, strict=False))
        self.assertEqual(2, len(phrases))
        self.assertEqual((30, 49), phrases[0])
        self.assertEqual((50, 79), phrases[1])

    def test_join_class_strict_01(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(8)]
        predicted = np.array([0, 0, 1, 1, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_class(
            tokens, predicted, strict=True))
        self.assertEqual(0, len(phrases))

    def test_join_class_strict_02(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(10)]
        predicted = np.array([0, 0, 0, 1, 0, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_class(
            tokens, predicted, strict=True))
        self.assertEqual(0, len(phrases))

    def test_join_class_strict_03(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(8)]
        predicted = np.array([0, 0, 1, 2, 2, 3, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_class(
            tokens, predicted, strict=True))
        self.assertEqual(1, len(phrases))

    def test_join_score_1_01(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(8)]
        predicted = np.array([0, 0, 1, 1, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_score(
            tokens, predicted, max_zeros=1, min_token_score=1))
        self.assertEqual(2, len(phrases))
        self.assertEqual((20, 29), phrases[0])
        self.assertEqual((30, 59), phrases[1])

    def test_join_score_2_01(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(8)]
        predicted = np.array([0, 0, 1, 1, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_score(
            tokens, predicted, max_zeros=1, min_token_score=2))
        self.assertEqual(1, len(phrases))
        self.assertEqual((30, 59), phrases[0])

    def test_join_score_2_02(self):
        tokens = [(i * 10, i * 10 + 9) for i in range(8)]
        predicted = np.array([0, 0, 1, 1, 0, 0, 2, 2, 0, 0])
        phrases = list(PhraseConstructor.join_tokens_by_score(
            tokens, predicted, max_zeros=1, min_token_score=2))
        self.assertEqual(0, len(phrases))

        phrases = list(PhraseConstructor.join_tokens_by_score(
            tokens, predicted, max_zeros=2, min_token_score=2))
        self.assertEqual(1, len(phrases))
        self.assertEqual((30, 79), phrases[0])
