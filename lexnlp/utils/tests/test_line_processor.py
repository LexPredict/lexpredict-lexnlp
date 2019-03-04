from unittest import TestCase
from lexnlp.utils.lines_processing.line_processor import LineProcessor, LineSplitParams


class TestLineProcessor(TestCase):

    def test_line_processor_lines(self):
        text = """
    aaa
    Bb b
    c"""
        proc = LineProcessor()
        lines = [line for line in proc.split_text_on_line_with_endings(text)]
        assert len(lines) == 3

    def test_line_processor_phrases(self):
        text = """
Once upon a midnight dreary

While I pounded, weak and weary. Over many a quaint and curious volume of forgotten lore,
While I nodded, nearly napping; suddenly there came a tapping,
As of some one gently rapping, rapping at my chamber door."""
        proc = LineProcessor()
        ptrs = LineSplitParams()
        ptrs.line_breaks = {'\n', '.', ';'}
        lines = [line for line in proc.split_text_on_line_with_endings(text, ptrs)]
        assert len(lines) == 6

    def test_line_processor_phrases_de(self):
        text = """
        (2) Vermögenswerte im Sinne dieses Gesetzes sind bebaute und unbebaute Grundstücke sowie rechtlich selbständige Gebäude und Baulichkeiten (im folgenden Grundstücke und Gebäude genannt), Nutzungsrechte und dingliche Rechte an Grundstücken oder Gebäuden, bewegliche Sachen sowie gewerbliche Schutzrechte, Urheberrechte und verwandte Schutzrechte. Vermögenswerte im Sinne dieses Gesetzes sind auch Kontoguthaben und sonstige auf Geldzahlungen gerichtete Forderungen sowie Eigentum/Beteiligungen an Unternehmen oder an Betriebsstätten/Zweigniederlassungen von Unternehmen mit Sitz außerhalb der Deutschen Demokratischen Republik.
        """
        proc = LineProcessor()
        ptrs = LineSplitParams()
        ptrs.line_breaks = {'\n', '.', ';'}
        lines = [line for line in proc.split_text_on_line_with_endings(text, ptrs)]
        assert len(lines) == 3 # plus one for an empty line

    def test_split_text_on_words(self):
        text = " While I pounded, weak  and weary. Over "
        proc = LineProcessor()
        all_words = proc.split_text_on_words(text)
        separators = [w for w in all_words if w.is_separator]
        words = [w for w in all_words if not w.is_separator]

        assert len(separators) == 8
        assert len(words) == 7

    def test_line_processor_phrases_abbr(self):
        text = 'Articolul saisprezece (16) Nr. 2. Textul:'
        proc = LineProcessor()
        ptrs = LineSplitParams()
        ptrs.line_breaks = {'\n', '.', ';'}

        lines = [line for line in proc.split_text_on_line_with_endings(text, ptrs)]
        assert len(lines) == 3

        ptrs.abbreviations = ['nr.', 'abs.']
        ptrs.abbr_ignore_case = True
        lines = [line for line in proc.split_text_on_line_with_endings(text, ptrs)]
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
