__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from nltk import word_tokenize, pos_tag
from typing import Tuple, Generator

from lexnlp.extract.common.text_beautifier import TextBeautifier


class SpanTokenizer:
    @staticmethod
    def get_token_spans(txt: str) -> \
            Generator[Tuple[str, str, int, int], None, None]:
        """
        returns: [('word', 'token', (word_start, word_end)), ...]
        """
        words = word_tokenize(txt)
        tokens = pos_tag(words)
        offset = 0
        last_symbol = len(txt) - 1

        for word, token in tokens:
            next_offset = txt.find(word, offset)
            if next_offset < 0:
                transf_word = TextBeautifier.find_transformed_word(
                    txt, word, offset)
                if transf_word:
                    word, next_offset = transf_word

            offset = next_offset if next_offset >= 0 else offset + 1
            offset = min(offset, last_symbol)

            right_margin = offset + len(word)

            yield word, token, offset, right_margin - 1
            offset = right_margin
