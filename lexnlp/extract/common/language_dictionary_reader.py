__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import codecs

from typing import Set


class LanguageDictionaryReader:
    """
    This class reads text files, where values are separated by <line_breaks>,
    strips the values if needed and returns them as List or Dict.

    We use this class, e.g., while reading De locale common abbreviations.
    """

    @staticmethod
    def read_str_set(file_path: str,
                     encoding='utf8',
                     strip_symbols=' ') -> Set[str]:
        words = set()
        with codecs.open(file_path, encoding=encoding, mode='r') as fr:
            for line in fr.readlines():
                if not line:
                    continue
                word = line.strip('\n')
                if not word:
                    continue
                if strip_symbols:
                    word = word.strip(strip_symbols)
                words.add(word)

        return words
