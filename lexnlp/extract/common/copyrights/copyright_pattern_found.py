__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from lexnlp.extract.common.pattern_found import PatternFound
import regex as re


class CopyrightPatternFound(PatternFound):
    reg_uppercase = re.compile(r"[\p{Lu}]+", re.UNICODE)

    def __init__(self, ptrn: PatternFound = None):
        super().__init__()
        if ptrn:
            self.name = ptrn.name
            self.start = ptrn.start
            self.end = ptrn.end
            self.probability = ptrn.probability
        else:
            self.name = None    # type: str
            self.start = 0
            self.end = 0
            self.probability = 0
        self.company = ''
        self.start_year = 0
        self.end_year = 0

    def __repr__(self):
        return f'[{self.start}: {self.end}]: "{self.name}", {self.probability}%'

    def get_length(self) -> int:
        return self.end - self.start

    def get_detalization_level(self, text: str) -> int:
        level = 0
        text_part = text[self.start: self.end]
        if self.reg_uppercase.search(text_part):
            level += 1
        if self.company:
            level += 1
        if self.start_year > 0:
            level += 1
        if self.end_year > 0:
            level += 1
        return level

    # override checking when patterns span
    def pattern_worse_than_target(self, p, text: str) -> bool:    # p: PatternFound
        spans = self.start <= p.start <= self.end or \
                self.start <= p.end <= self.end
        if not spans:
            return False
        # what is more detailed?
        self_level = self.get_detalization_level(text)
        p_level = p.get_detalization_level(text)
        if self_level < p_level:
            return True
        if p_level < self_level:
            return False

        # what is shorter?
        return p.get_length() <= self.get_length()
