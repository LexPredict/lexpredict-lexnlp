__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase

from lexnlp.extract.common.text_beautifier import TextBeautifier


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

    def test_quotes_coords(self):
        text = '"Consolidated EBITDA means, for any period'
        cleared = TextBeautifier.unify_quotes_braces_coords(text, 10, 93)
        self.assertEqual(('Consolidated EBITDA means, for any period', 11, 93), cleared)

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

    def test_strip_pair_symbols(self):
        text = '"(A right of set-off; B)"'
        cleared = TextBeautifier.strip_pair_symbols(text)
        self.assertEqual('A right of set-off; B', cleared)

        text = '("A right" of set-off; "B")'
        cleared = TextBeautifier.strip_pair_symbols(text)
        self.assertEqual('"A right" of set-off; "B"', cleared)

    def test_strip_pair_symbols_coords(self):
        text = ' "(A right of set-off; B)"'
        cleared = TextBeautifier.strip_pair_symbols((text, 2, 23))
        self.assertEqual(('A right of set-off; B', 5, 21), cleared)

        text = '("A right" of set-off; "B")'
        cleared = TextBeautifier.strip_pair_symbols((text, 100, 119))
        self.assertEqual(('"A right" of set-off; "B"', 101, 118), cleared)

        text = '  "A right" of set-off; "B" '
        cleared = TextBeautifier.strip_pair_symbols((text, 100, 119))
        self.assertEqual(('"A right" of set-off; "B"', 102, 118), cleared)

    def test_strip_pair_symbols_untouched(self):
        text = '(A) right of set-off; (B)'
        cleared = TextBeautifier.strip_pair_symbols(text)
        self.assertEqual(text, cleared)

        text = '(A ( right) of set-off; (B)'
        cleared = TextBeautifier.strip_pair_symbols(text)
        self.assertEqual(text, cleared)

        text = '"(A ( right)" "of set-off; (B)"'
        cleared = TextBeautifier.strip_pair_symbols(text)
        self.assertEqual(text, cleared)

    def test_strip_text_coords(self):
        text = '    (A) right of set-off; (B) '
        stripped = TextBeautifier.strip_string_coords(
            text, 100, 127)
        self.assertEqual(('(A) right of set-off; (B)', 104, 126), stripped)

        text = '    (A) right of set-off; (B) '
        stripped = TextBeautifier.lstrip_string_coords(
            text, 100, 127)
        self.assertEqual(('(A) right of set-off; (B) ', 104, 127), stripped)

        text = '    (A) right of set-off; (B) '
        stripped = TextBeautifier.rstrip_string_coords(
            text, 100, 127)
        self.assertEqual(('    (A) right of set-off; (B)', 100, 126), stripped)

    def test_find_transformed_word(self):
        text = '(each an “Obligation” and collectively, the “Obligations”)'
        wrd = TextBeautifier.find_transformed_word(text, '"Obligation"', 0)
        self.assertEqual(None, wrd)
