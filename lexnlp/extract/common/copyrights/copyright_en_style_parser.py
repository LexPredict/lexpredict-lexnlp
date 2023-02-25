"""Copyright extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic Copyright extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
import string
from typing import Generator, List, Tuple

from lexnlp.extract.common.annotations.copyright_annotation import CopyrightAnnotation


class CopyrightEnStyleParser:
    reg_company_name = re.compile(r"[\p{Lu}]+[\p{L}\s]*", re.UNICODE)

    reg_valid_company_name = re.compile(r"\p{L}[\p{L}\s,]+", re.UNICODE)

    year_ptn = r"(\d{4}(?:\s*[-,–]\s*\d{4})?)"
    year_ptn_re = re.compile(year_ptn + '$')

    copyright_ptn = fr"((Copyright\W\s*|\(\s*[Cc]\s*\)\s*|©)+\s*{year_ptn}?\s*(.+))"
    copyright_ptn_re = re.compile(copyright_ptn)

    copyright_dates_re = re.compile(r'\d{2,}')

    @staticmethod
    def get_copyrights(
        text: str,
        return_sources: bool = False
    ) -> Generator[CopyrightAnnotation, None, None]:
        for ant in CopyrightEnStyleParser.get_copyright_annotations(text, return_sources):
            if return_sources:
                yield ant.sign, ant.date, ant.name, ant.text
            else:
                yield ant.sign, ant.date, ant.name

    @classmethod
    def extract_phrases_with_coords(cls, sentence: str) -> List[Tuple[str, int, int]]:
        raise NotImplementedError()

    @classmethod
    def get_copyright_annotations(cls, text: str, return_sources=False) -> Generator[CopyrightAnnotation, None, None]:
        """
        Find copyright in text.
        :param text:
        :param return_sources:
        :return:
        """
        # Iterate through sentences
        if not cls.copyright_ptn_re.search(text):
            return

        tagged_phrases = cls.extract_phrases_with_coords(text)

        for phrase, phrase_start, phrase_end in tagged_phrases:
            for match in cls.copyright_ptn_re.finditer(phrase):  # type: re.Match
                cp_text, cp_sign, cp_date, cp_name = match.groups()

                # TODO: catch in the general regex
                if not cp_date:
                    cp_date_at_end = cls.year_ptn_re.search(cp_name)
                    if cp_date_at_end:
                        cp_date = cp_date_at_end.group()
                        cp_name = re.sub(r'{}$'.format(cp_date), '', cp_name)

                start, end = match.span()
                if end > (phrase_end - phrase_start):
                    end = phrase_end - phrase_start
                start += phrase_start
                end += phrase_start
                ant = CopyrightAnnotation(coords=(start, end),
                                          sign=cp_sign.strip(),
                                          date=cp_date,
                                          name=cp_name.strip(string.punctuation +
                                                             string.whitespace))

                if return_sources:
                    ant.text = cp_text.strip()
                cls.split_copyright_date(ant)
                cls.derive_company_name(ant, phrase)
                yield ant

    @classmethod
    def derive_company_name(cls, ant: CopyrightAnnotation, phrase: str) -> None:
        if ant.company:
            ant.company = ant.company.strip(' ,;-(:')
            if cls.reg_valid_company_name.search(ant.company):
                return
            ant.company = ''
        possible_names = [n.group(0) for n in cls.reg_company_name.finditer(ant.name)]
        if not possible_names:
            possible_names = [n.group(0) for n in cls.reg_company_name.finditer(phrase)]
        if possible_names:
            ant.company = cls.take_best_company_name(possible_names)
            ant.company = ant.company.strip(' ,;-(:')

    @classmethod
    def take_best_company_name(cls, names: List[str]) -> str:
        # e.g., ['Huawei', 'permiten que más']
        for name in names:
            if cls.reg_company_name.search(name):
                return name
        return names[0]

    @classmethod
    def split_copyright_date(cls, ant: CopyrightAnnotation) -> None:
        if not ant.date:
            return
        years = [int(y.group()) for y in cls.copyright_dates_re.finditer(ant.date)]
        if len(years) == 2:
            if 10000 > years[0] > 100 and years[1] >= years[0]:
                ant.year_start = years[0]
                ant.year_end = years[1]
                return

        if len(years) == 1 and 10000 > years[0] > 100:
            ant.year_start = years[0]
