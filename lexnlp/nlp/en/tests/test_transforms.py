#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.nlp.en.transforms.characters import get_character_distribution
from lexnlp.nlp.en.transforms.tokens import get_token_distribution, get_stem_distribution


class TestTransforms(TestCase):
    def test_character_distribution_example(self):
        distribution = get_character_distribution("abc")
        self.assertTrue("a" in distribution)
        self.assertEqual(1, distribution["a"])
        self.assertTrue("b" in distribution)
        self.assertEqual(1, distribution["b"])
        self.assertTrue("c" in distribution)
        self.assertEqual(1, distribution["c"])

    def test_token_distribution_example_1(self):
        distribution = get_token_distribution("abc 123")
        self.assertTrue("abc" in distribution)
        self.assertEqual(1, distribution["abc"])
        self.assertTrue("123" in distribution)
        self.assertEqual(1, distribution["123"])

    def test_stem_distribution_example_1(self):
        distribution = get_stem_distribution("Trump trumps to entrump trumped intrumpable")
        self.assertTrue("trump" in distribution)
        self.assertTrue("intrump" in distribution)
        self.assertEqual(3, distribution["trump"])
