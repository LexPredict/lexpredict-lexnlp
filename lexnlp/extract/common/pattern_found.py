__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PatternFound:
    """
    used inside EsDefinitionsParser and SpanishParsingMethods
    to store intermediate parsing results
    """
    def __init__(self):
        self.name = None    # type: str
        self.start = 0
        self.end = 0
        self.probability = 0

    # pylint: disable=unused-argument
    def pattern_worse_than_target(self, p, text: str) -> bool:  # p: PatternFound
        """
        check what pattern is better then 2 patterns are considered duplicated
        "text" may be used in derived classes
        """
        spans = self.start <= p.start <= self.end and \
                self.start <= p.end <= self.end
        if not spans:
            return False
        return self.name.find(p.name) >= 0
