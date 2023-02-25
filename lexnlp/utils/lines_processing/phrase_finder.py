__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
from typing import List, Tuple


PhraseMatch = Tuple[str, int, int]


class PhraseFinder:
    """
    The class contains a collection of short string (usually 1 or 2 or 3 words)
    PhraseFinder searches for these strings (phrases) in the text given, either
    ignoring or regarding the case
    """

    def __init__(self, phrase_set: List[str], extra_format_function=None):
        self.extra_format_function = extra_format_function
        self.word_re_ig = dict((v, self.word_to_regex(v, True)) for v in phrase_set)
        self.word_re_cs = dict((v, self.word_to_regex(v, False)) for v in phrase_set)

    def word_to_regex(self, word: str, ignore_case: bool) -> str:
        # " Amtsgericht Stuttgart" ->  re("Amtsgericht[\s]+Stuttgart")
        subphrase = word.replace(r'\t', ' ').strip(' ').replace('  ', ' ').replace(' ', r'[\s]+')
        if self.extra_format_function is not None:
            subphrase = self.extra_format_function(subphrase)
        sps = '(\\b|\\s)'
        return re.compile(sps + subphrase + sps, re.IGNORECASE | re.UNICODE) if ignore_case else \
            re.compile(sps + subphrase + sps, re.UNICODE)

    def find_word(self, phrase: str, ignore_case: bool = True) -> List[PhraseMatch]:
        """
        :param phrase: "Tis better using France than trusting France: let us be back'd with God and with the seas"
        :param ignore_case: True
        :return: [ ('better', 4, 9), (' let us ', 46, 52) ]

        PhraseFinder instance had been initialized like
            PhraseFinder([' let us ', 'better', 'the sea'])
        """
        matches = []
        match_dict = self.word_re_ig if ignore_case else self.word_re_cs

        for k, v in match_dict.items():
            for match in v.finditer(phrase):
                matches.append((k, match.start(), match.end()))
        return matches
