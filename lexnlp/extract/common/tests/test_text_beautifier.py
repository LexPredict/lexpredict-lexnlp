from unittest import TestCase

from lexnlp.extract.common.text_beautifier import TextBeautifier

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestTextBeautifier(TestCase):
    def test_negative(self):
        text = '(x + 3) *[(y-1)/(y+1)^2]^3'
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual(text, cleared)

        text = '"Jupyter", Venus and "Mars"'
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual(text, cleared)

        text = "Let' get loud"
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual(text, cleared)

    def test_braces_shape(self):
        text = '{x + 3) *[(y-1)/(y+1]^2]^3'
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual('{x + 3} *[(y-1)/(y+1)^2]^3', cleared)

    def test_unbalanced_braces(self):
        text = '{x + 3) *[(y-1)/(y+1^2]^3'
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual('{x + 3} *(y-1)/(y+1^2)^3', cleared)

        text = 'Ma tem ca nu cred ((in general) in legatura printre aceste fapte ('
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual('Ma tem ca nu cred (in general) in legatura printre aceste fapte ', cleared)

    def test_doubled_quotes(self):
        text = '""Consolidated EBITDA" means, for any period'
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual('"Consolidated EBITDA" means, for any period', cleared)

    def test_misplaced_quotes(self):
        text = '”Consolidated EBITDA“'
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual('“Consolidated EBITDA”', cleared)

    def test_mixshaped_quotes(self):
        text = 'Equity Interest upon the occurrence of an “asset sale" or a “change of control” '
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual("Equity Interest upon the occurrence of an “asset sale” or a “change of control” ",
                         cleared)

        text = 'На "бобах\' одна старушка погадала бы, да \'жалко": "померла"'
        cleared = TextBeautifier.unify_quotes_braces(text)
        # the text remains untouched because dub. quotes are balanced
        self.assertEqual(text, cleared)

        text = 'called "champerty\''
        cleared = TextBeautifier.unify_quotes_braces(text)
        self.assertEqual('called "champerty"', cleared)
