__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import datetime
import regex as re
from typing import List, Tuple


class YearParser:
    """
    finds years in the string passed
    """
    def __init__(self):
        self.max_year = datetime.datetime.now().year + 1
        self.reg_year = re.compile(r"\d{4}")

    def check_year_ok(self, year: int, min_year: int = 1800, max_year=0):
        max_year = max_year if max_year > 0 else self.max_year
        return min_year <= year <= max_year

    def get_years_with_coords_from_string(self,
                                          text: str, min_year: int = 1800,
                                          max_year=0) -> List[Tuple[int, int, int]]:
        years = []  # List[Tuple[int, int, int]]
        for m in self.reg_year.finditer(text):
            year = int(m.group())
            if self.check_year_ok(year, min_year, max_year):
                years.append((year, m.start(), m.end()))
        return years


year_parser = YearParser()
