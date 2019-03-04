"""Extraction utilities for English.
"""
# Imports
import re
import string
import unicodedata
from itertools import groupby

import nltk


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# Default punctuation to whitelist
VALID_PUNCTUATION = [".", ",", "'", "-", "&", "(", ")"]


def strip_unicode_punctuation(text, valid_punctuation=None):
    """
    This method strips all unicode punctuation that is not whitelisted.
    :param text: text to strip
    :param valid_punctuation: valid punctuation to whitelist
    :return:
    """
    valid_punctuation = valid_punctuation or VALID_PUNCTUATION

    return "".join(c for c in text if (c in valid_punctuation) or not unicodedata.category(c).startswith("P"))


default_grammar = r"""
    NBAR:
        {<DT>?<NNP.*|JJ|\(|\)|,>*<NNP.*>}  # Nouns, Adj-s, brackets, terminated with Nouns
    IN:
        {<CC|IN>}   # &, and, of
    NP:
        {(<NBAR><IN>)*<NBAR>}
"""


class NPExtractor(object):

    exception_sym = ['&', 'and', 'of']
    exception_pos = ['IN', 'CC']
    sym_with_space = ['(', '&']
    sym_without_space = ''.join([i for i in string.punctuation if i not in ['(', '&']])

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

    def get_np(self, text):
        tokenizer_func = self.get_tokenizer()
        tokens = tokenizer_func(text)
        pos_tokens = nltk.tag.pos_tag(tokens)
        chunks = self.chunker.parse(pos_tokens)

        for tree in chunks.subtrees(filter=lambda t: t.label() == 'NP'):
            leaves = self.cleanup_leaves(tree.leaves())
            for np_items in leaves:
                yield self.join(np_items)

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
