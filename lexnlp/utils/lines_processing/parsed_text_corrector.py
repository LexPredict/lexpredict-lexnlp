__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import itertools

from lexnlp.utils.lines_processing.line_processor import LineOrPhrase
from lexnlp.utils.lines_processing.parsed_text_quality_estimator import ParsedTextQualityEstimator


class ParsedTextCorrector:
    """
    Class "corrects" the text given if the ParsedTextQualityEstimator class' instance
    points to one of possible violation types.

    For now the only possible "violation" is a number of "unnecessary" line breaks (\n\n)
    """
    def __init__(self):
        pass

    def correct_if_corrupted(self, text: str) -> str:
        """
        Checks the text and correct if corrupted.
        Let's assume the text is:
            1.1 Etymology

            Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical
            Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at

            Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a
            Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered

            the undoubtable source.
        :param text: a text containing a number of \n\n sequences, see above
        :return: the same text without 2 double line breaks:
            1.1 Etymology

            Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical
            Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at
            Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a
            Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered
            the undoubtable source.
        """
        estimator = ParsedTextQualityEstimator()
        estim = estimator.estimate_text(text)
        if estim.corrupted_prob < 50:
            return text
        if estim.extra_line_breaks_prob > 50:
            text = self.correct_line_breaks(text, estimator)
        return text

    # remove all double (triple ...) line breaks
    def correct_line_breaks(self, text: str,
                            estimator: ParsedTextQualityEstimator = None) -> str:
        if estimator is None:
            estimator = ParsedTextQualityEstimator()
            estimator.split_text_on_lines(text)

        resulted = ''
        lines = estimator.lines

        for index, line in enumerate(lines):
            if estimator.check_line_followed_by_unnecessary_break(index):
                self.normalize_line_ending(line)
            resulted += line.text
            resulted += line.ending
        return resulted

    def normalize_line_ending(self, line: LineOrPhrase):
        line.ending = ''.join(ch for ch, _ in itertools.groupby(line.ending))
