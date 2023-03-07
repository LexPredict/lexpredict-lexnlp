# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from typing import List, Optional

import regex as re
import pandas as pd


class EntityBanListItem:
    def __init__(self,
                 pattern: str,
                 ignore_case: bool = True,
                 is_regex: bool = False,
                 trim_phrase: bool = True):
        """
        :param pattern: string or reg. expression to check on a phrase
        :param ignore_case: ignore case while checking if True
        :param is_regex: compile pattern into regexp if True, else check pattern as a string
        :param trim_phrase: strip phrase of space symbols before checking if True
        """
        self.pattern = pattern
        self.ignore_case = ignore_case
        self.is_regex = is_regex
        self.reg_exp = None
        self.trim_phrase = trim_phrase
        if is_regex:
            self.compile_regex()
        elif ignore_case:
            self.pattern = pattern.lower()

    def __repr__(self):
        flags = []
        if self.ignore_case:
            flags.append('I')
        if self.is_regex:
            flags.append('Re')
        if self.trim_phrase:
            flags.append('T')
        flags_s = ' ' + ','.join(flags) if flags else ''
        return f'"{self.pattern}"{flags_s}'

    def compile_regex(self):
        self.reg_exp = re.compile(self.pattern, re.IGNORECASE) \
            if self.ignore_case else re.compile(self.pattern)

    @classmethod
    def check_list(cls, text: str, banlist) -> bool:
        """
        :param text: phrase to check
        :param banlist: list of EntityBanListItem, type: List[EntityBanListItem]
        :return: True if matches any of the patterns
        """
        for item in banlist:  # type: EntityBanListItem
            if item.check(text):
                return True
        return False

    def check(self, text: str) -> bool:
        if self.trim_phrase:
            text = text.strip()
        if self.reg_exp:
            return self.reg_exp.match(text) is not None
        if self.ignore_case:
            text = (text or '').lower()
        return self.pattern == text

    @classmethod
    def read_from_csv(cls,
                      file_path: str,
                      encoding: str = 'utf-8',
                      strip_patterns: bool = True,
                      separator: str = ';'):
        """
        File columns: PATTERN (str), IGNORE_CASE (int), IS_REGEX (int), TRIM_PHRASE (int)
        "Company;1;0;1" means: pattern="Company", ignore_case=True, is_regex=False, trim_phrase=True
        :param file_path: full path to csv file
        :return: List[EntityBanListItem]
        """
        items = []  # type: List[EntityBanListItem]
        df = pd.read_csv(file_path, encoding=encoding, sep=separator, header=None)
        for _index, row in df.iterrows():
            pattern = row[0]
            if strip_patterns:
                pattern = pattern.strip()
            ignore_case, is_regex, trim_phrase = True, False, True
            columns = len(row)
            if columns > 1:
                ignore_case = bool(row[1])
            if columns > 2:
                is_regex = bool(row[2])
            if columns > 3:
                trim_phrase = bool(row[3])

            item = EntityBanListItem(pattern, ignore_case, is_regex, trim_phrase)
            items.append(item)

        return items


class BanListUsage:
    def __init__(self,
                 banlist: Optional[List[EntityBanListItem]] = None,
                 use_default_banlist: bool = True,
                 append_to_default: bool = False):
        self.banlist = banlist
        self.use_default_banlist = use_default_banlist
        self.append_to_default = append_to_default

    def __repr__(self):
        provided = len(self.banlist) if self.banlist else 0
        return f'{provided} items provided, default={self.use_default_banlist}' + \
               f'append={self.append_to_default}'


default_banlist_usage = BanListUsage()
