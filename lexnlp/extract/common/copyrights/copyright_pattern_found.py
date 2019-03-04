from lexnlp.extract.common.pattern_found import PatternFound


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class CopyrightPatternFound(PatternFound):
    def __init__(self, ptrn: PatternFound = None):
        super(CopyrightPatternFound, self).__init__()
        if ptrn:
            self.name = ptrn.name
            self.start = ptrn.start
            self.end = ptrn.end
            self.probability = ptrn.probability
        else:
            self.name = None # type: str
            self.start = 0
            self.end = 0
            self.probability = 0
        self.company = ''
        self.start_year = 0
        self.end_year = 0

    def get_length(self) -> int:
        return self.end - self.start

    def get_detalization_level(self) -> int:
        level = 0
        if self.company:
            level += 1
        if self.start_year > 0:
            level += 1
        if self.end_year > 0:
            level += 1
        return level

    # override checking when patterns span
    def pattern_worse_than_target(self, p) -> bool: # p: PatternFound
        spans = self.start <= p.start <= self.end or \
                self.start <= p.end <= self.end
        if not spans:
            return False
        # what is more detailed?
        self_level = self.get_detalization_level()
        p_level = p.get_detalization_level()
        if self_level < p_level:
            return True
        elif p_level < self_level:
            return False

        # what is shorter?
        return p.get_length() <= self.get_length()
