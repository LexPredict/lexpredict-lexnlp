__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from unittest import TestCase
from lexnlp.utils.lines_processing.line_processor import LineProcessor, LineSplitParams


class TestLineProcessor(TestCase):

    def test_line_processor_lines(self):
        text = """
    aaa
    Bb b
    c"""
        proc = LineProcessor()
        lines = list(proc.split_text_on_line_with_endings(text))
        assert len(lines) == 3

    def test_line_processor_phrases(self):
        text = """
Once upon a midnight dreary

While I pounded, weak and weary. Over many a quaint and curious volume of forgotten lore,
While I nodded, nearly napping; suddenly there came a tapping,
As of some one gently rapping, rapping at my chamber door."""
        ptrs = LineSplitParams()
        ptrs.line_breaks = {'\n', '.', ';'}
        proc = LineProcessor(line_split_params=ptrs)
        lines = list(proc.split_text_on_line_with_endings(text))
        assert len(lines) == 6

    def test_line_processor_phrases_de(self):
        text = """
        (2) Vermögenswerte im Sinne dieses Gesetzes sind bebaute und unbebaute Grundstücke sowie rechtlich selbständige Gebäude und Baulichkeiten (im folgenden Grundstücke und Gebäude genannt), Nutzungsrechte und dingliche Rechte an Grundstücken oder Gebäuden, bewegliche Sachen sowie gewerbliche Schutzrechte, Urheberrechte und verwandte Schutzrechte. Vermögenswerte im Sinne dieses Gesetzes sind auch Kontoguthaben und sonstige auf Geldzahlungen gerichtete Forderungen sowie Eigentum/Beteiligungen an Unternehmen oder an Betriebsstätten/Zweigniederlassungen von Unternehmen mit Sitz außerhalb der Deutschen Demokratischen Republik.
        """
        ptrs = LineSplitParams()
        ptrs.line_breaks = {'\n', '.', ';'}
        proc = LineProcessor(line_split_params=ptrs)
        lines = list(proc.split_text_on_line_with_endings(text))
        assert len(lines) == 3   # plus one for an empty line

    def test_split_text_on_words(self):
        text = " While I pounded, weak  and weary. Over "
        proc = LineProcessor()
        all_words = proc.split_text_on_words(text)
        separators = [w for w in all_words if w.is_separator]
        words = [w for w in all_words if not w.is_separator]

        assert len(separators) == 8
        assert len(words) == 7

    def test_line_processor_phrases_abbr(self):
        text = 'Articolul saisprezece (16) nr. 2. Textul:'
        ptrs = LineSplitParams()
        ptrs.line_breaks = {'\n', '.', ';'}
        proc = LineProcessor(line_split_params=ptrs)

        lines = list(proc.split_text_on_line_with_endings(text))
        assert len(lines) == 3

        ptrs.abbreviations = {'nr.', 'abs.'}
        ptrs.abbr_ignore_case = True
        proc = LineProcessor(line_split_params=ptrs)
        lines = list(proc.split_text_on_line_with_endings(text))
        assert len(lines) == 2

    def test_check_phrase_starts_with_phrase(self):
        text = 'While I pounded, weak and weary. Over many a quaint and curious volume of forgotten lore'
        proc = LineProcessor()
        words = proc.split_text_on_words(text)

        ret = proc.check_phrase_starts_with_phrase(words, 2, ['I', 'goat'])
        assert ret

        ret = proc.check_phrase_starts_with_phrase(words, 3, ['I', 'goat'])
        assert not ret

        ret = proc.check_phrase_starts_with_phrase(words, 6, ['I', 'weak'])
        assert ret

        ret = proc.check_phrase_starts_with_phrase(words, 6, ['I', ['weak', 'and']])
        assert ret

        ret = proc.check_phrase_starts_with_phrase(words, 6, ['I', ['weak', 'weary']])
        assert not ret

    def test_de_linebreaks(self):
        split_params = LineSplitParams()
        split_params.line_breaks = {'.', ';', '!', '?'}
        split_params.abbreviations = {'nr.', 'abs.', 'no.', 'act.', 'inc.', 'p.'}
        split_params.abbr_ignore_case = True
        text = 'Nach der Allgemeine\nGebührenverordnung'
        proc = LineProcessor(line_split_params=split_params)
        sents = list(proc.split_text_on_line_with_endings(text))
        self.assertEqual(1, len(sents))

    def test_de_abbrs(self):
        split_params = LineSplitParams()
        split_params.line_breaks = {'.', ';', '!', '?'}
        split_params.abbreviations = {'nr.', 'abs.', 'no.', 'act.', 'a.D.'}
        split_params.abbr_ignore_case = True

        text = '1000 a.D. und drang'
        proc = LineProcessor(line_split_params=split_params)
        sents = list(proc.split_text_on_line_with_endings(text))
        self.assertEqual(1, len(sents))

        text = '1000 A.d. und drang'
        sents = list(proc.split_text_on_line_with_endings(text))
        self.assertGreater(len(sents), 1)
