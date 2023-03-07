__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
from enum import Enum
from lexnlp.utils.lines_processing.line_processor import LineOrPhrase, LineProcessor


LineType = Enum('LineType', 'regular header paragraph_start')


class TypedLineOrPhrase(LineOrPhrase):
    """
    Extends the LineOrPhrase class (text - ending - position)
    Adds LineType attribute specifying the line's "role" within the text
    """
    def __init__(self):
        super().__init__()
        self.type = LineType.regular

    @staticmethod
    def wrap_line(l: LineOrPhrase):
        t = TypedLineOrPhrase()
        t.text = l.text
        t.start = l.start
        t.ending = l.ending
        return t

    def __repr__(self):
        return '[' + str(self.type) + '] ' + self.text + '->' + self.ending


class ParsedTextQualityEstimate:
    """
    A complex estimate for a text fragment
    - corrupted_prob: the probability of the text being "corrupted".
      Currently equals to extra_line_breaks_prob.
    - extra_line_breaks_prob: the probability (0..100) of the text containing unnecessary
      line breaks (\n).
    - an average line length withing the text (in characters).
    """
    def __init__(self):
        self.corrupted_prob = 0
        self.extra_line_breaks_prob = 0
        self.avg_line_length = 100


class ParsedTextQualityEstimator:
    """
    Estimates the probability of the text passed being somewhat corrupted
    """

    sentence_break_chars = {'.', ';', '!', '?', ','}
    reg_numered_header = re.compile(r'(^[\s]*\(?[a-zA-Z]\)?\s)|(^[\s]*[0-9\.]+[\)]?\s)')
    reg_paragraph_start = re.compile(r'(^\s{2})|(^\t)')
    minimal_paragraph_line_length = 250

    def __init__(self):
        self.estimate = ParsedTextQualityEstimate()
        self.lines = []
        self.proc = LineProcessor()

    def estimate_text(self, text: str) -> ParsedTextQualityEstimate:
        """
        Let's assume the text is:
            Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical
            Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at

            Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a
            Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered

            the undoubtable source.
        :param text: a text containing a number of \n\n sequences, see above
        :return: ParsedTextQualityEstimate: {'avg_line_length': 103, 'extra_line_breaks_prob': 66, 'corrupted_prob': 66}
        """

        self.split_text_on_lines(text)
        # does the text contain unnecessary line breaks?
        self.estimate_extra_line_breaks()
        # wrap up the estimate
        self.estimate.corrupted_prob = self.estimate.extra_line_breaks_prob
        return self.estimate

    def split_text_on_lines(self, text: str):
        self.estimate = ParsedTextQualityEstimate()

        self.lines = [TypedLineOrPhrase.wrap_line(l) for l in
                      self.proc.split_text_on_line_with_endings(text)]
        self.proc.determine_line_length(text)
        self.estimate.avg_line_length = self.proc.line_length

        for line in self.lines:
            self.determine_line_type(line)

    def estimate_extra_line_breaks(self):
        lines_total = len(self.lines)
        if lines_total == 0:
            return

        longest_seq = 0
        current_seq = 0
        total_extra_breaks = 0

        for indx in range(0, len(self.lines)):
            if self.check_line_followed_by_unnecessary_break(indx):
                total_extra_breaks += 1
                current_seq += 1
                longest_seq = max(current_seq, longest_seq)
                continue
            current_seq = 0

        if total_extra_breaks > 1:
            p1 = 100 if longest_seq > lines_total / 3 else int(100 * longest_seq * 2.5 / lines_total)
            p2 = int(100 * total_extra_breaks * 2 / lines_total)
            self.estimate.extra_line_breaks_prob = min(100, max(p1, p2))

    def check_line_followed_by_unnecessary_break(self, line_index: int) -> bool:
        line = self.lines[line_index]
        if line.ending.count('\n') <= 1:
            return False
        if len(line.text) > ParsedTextQualityEstimator.minimal_paragraph_line_length:
            # the whole line could be a paragraph
            return False
        prob_needs_extra = line.type == LineType.header
        if not prob_needs_extra:
            next_line = self.lines[line_index + 1] if line_index < len(self.lines) - 1 else None
            prob_needs_extra = next_line is not None and next_line.type != LineType.regular
        return not prob_needs_extra

    def determine_line_type(self, line: TypedLineOrPhrase):
        p_head = self.estimate_line_is_header_prob(line.text)
        if p_head > 50:
            line.type = LineType.header
            return
        p_par_start = self.estimate_line_is_paragraph_start_prob(line.text)
        if p_par_start > 50:
            line.type = LineType.paragraph_start

    def estimate_line_is_paragraph_start_prob(self, line: str) -> int:
        if ParsedTextQualityEstimator.reg_paragraph_start.search(line):
            return 100
        return 0

    def estimate_line_is_header_prob(self, line: str) -> int:
        line = line.rstrip(' \t')
        if len(line) == 0:
            return 0
        if line[-1] in ParsedTextQualityEstimator.sentence_break_chars:
            return 0
        if ParsedTextQualityEstimator.reg_numered_header.search(line):
            return 100

        if len(line) < self.estimate.avg_line_length * 0.6:
            return 65   # 65% chance the line is a header

        return 35
