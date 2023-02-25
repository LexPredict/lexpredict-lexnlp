"""Extraction utilities for English.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import re
import nltk
import string
import unicodedata
from itertools import groupby
from typing import Generator, List, Tuple
from lexnlp.utils.pos_adjustments import TokenPosTagAdjustment
from lexnlp.extract.common.annotations.phrase_position_finder import PhrasePositionFinder


# Default punctuation to accept


VALID_PUNCTUATION = [".", ",", "'", "-", "&", "(", ")"]


def strip_unicode_punctuation(text, valid_punctuation=None):
    """
    This method strips all unicode punctuation that is not accepted.
    :param text: text to strip
    :param valid_punctuation: valid punctuation to accept
    :return:
    """
    valid_punctuation = valid_punctuation or VALID_PUNCTUATION

    return "".join(c for c in text if (c in valid_punctuation) or not unicodedata.category(c).startswith("P"))


def replace_upper_words_with_titled(text: str):
    """
    This method replaces all uppercase words with titled ones.
    :param text: text to process
    :return: text with no upper words
    """
    titled_upper_words = sorted(
        [i.title() for i in re.findall(r'[a-zA-Z]+', text) if i.upper() == i],
        key=len
    )[::-1]
    words = re.findall(r'[a-zA-Z]+', text)

    for i in titled_upper_words:
        text = text.replace(i.upper(), i)
    return text
    

default_grammar = r"""
    NBAR:
        {<DT>?<NNP.*|JJ|POS|\(|\)|,>*<NNP.*>}  # DeTerminer, Proper Noun, Adjective, brackets, terminated by Proper Noun
    IN:
        {<CC|IN>}   # Coordinating Conjunction, Preposition/Subordinating Conjunction
    NP:
        {(<NBAR><IN>)*<NBAR>}
"""


class NPExtractor:

    exception_sym = ['&', 'and', 'of']
    exception_pos = ['IN', 'CC']
    sym_with_space = ['(', '&']
    sym_without_space = [i for i in string.punctuation if i not in '(&/'] + ["'s"]
    replacements = [
        [(r'(\w)&(\w)', r'\1-=AND=-\2'), ('-=AND=-', '&')]
    ]
    token_pos_tag_adjustments: List[TokenPosTagAdjustment] = []

    def __init__(self, grammar=None):
        grammar = grammar or default_grammar
        self.chunker = nltk.RegexpParser(grammar)

    def get_tokenizer(self):
        tokenizer = nltk.tokenize.TreebankWordTokenizer
        tokenizer.PUNCTUATION[4] = (re.compile(r'[;@#$%]', re.UNICODE), ' \\g<0> ')
        return tokenizer().tokenize

    def cleanup_leaves(self, leaves):
        leaves = [l for l in
                  [list(group) for key, group in groupby(
                      leaves, key=lambda k: k[0] not in self.exception_sym and k[1] in self.exception_pos)]
                  if l[0][1] not in self.exception_pos or l[0][0] in self.exception_sym]
        return leaves

    def get_np(self, text: str) -> Generator[str, None, None]:
        text = self.replace(text)
        tokenizer_func = self.get_tokenizer()
        tokens = tokenizer_func(text)
        pos_tokens = nltk.tag.pos_tag(tokens)
        for adjustment in self.token_pos_tag_adjustments:
            pos_tokens = [*map(adjustment, pos_tokens)]
        chunks = self.chunker.parse(pos_tokens)
        for tree in chunks.subtrees(filter=lambda t: t.label() == 'NP'):
            leaves = self.cleanup_leaves(tree.leaves())
            for np_items in leaves:
                yield self.replace(self.join(np_items), back=True)

    def replace(self, text, back=False):
        for _in, _out in self.replacements:
            _from, _to = _out if back else _in
            text = re.sub(_from, _to, text)
        return text

    def get_np_with_coords(self, text: str) -> List[Tuple[str, int, int]]:
        phrases = list(self.get_np(text))
        tagged_phrases = PhrasePositionFinder.find_phrase_in_source_text(
            text, phrases)
        return tagged_phrases

    def join(self, np_items):
        np = ''
        last_pos = None
        for n, current_pos in enumerate(np_items):
            item, _ = current_pos
            sep = self.sep(n, current_pos, last_pos)
            np += sep + item
            last_pos = current_pos
        return self.strip_np(np)

    def sep(self, n, current_pos, last_pos):
        return ' ' if n and current_pos[0] not in self.sym_without_space\
                      and last_pos[0] not in "(" else ""

    @staticmethod
    def strip_np(np):
        return np.strip(string.punctuation.replace(')', '') + string.whitespace)
