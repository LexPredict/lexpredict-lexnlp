"""Copyright extraction for English using NLTK and NLTK pre-trained maximum entropy classifier.

This module implements basic Copyright extraction functionality in English relying on the pre-trained
NLTK functionality, including POS tagger and NE (fuzzy) chunkers.

Todo: -
"""

# Imports
import re
import string
from typing import Generator

from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.extract.en.utils import NPExtractor

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


YEAR_PTN = r"(\d{4}(?:\s*-\s*\d{4})?)"
YEAR_PTN_RE = re.compile(YEAR_PTN + '$')

COPYRIGHT_PTN = r"((Copyright\W|\([Cc]\)\s*|©)+\s*{}?\s*(.+))".format(YEAR_PTN)
COPYRIGHT_PTN_RE = re.compile(COPYRIGHT_PTN)

grammar = r"""
    NBAR:
        {<NNP.*|JJ|CD|NN|\(|\)|,>*<NNP.*|CD>}  # Nouns, Adj-s, brackets, terminated with Nouns/Numbers
    IN:
        {<CC|IN>}   # &, and, of
    NP:
        {(<NBAR><IN>)*<NBAR>}
"""


class CopyrightNPExtractor(NPExtractor):

    allowed_sym = ['&', 'and', 'of', '©']
    allowed_pos = ['IN', 'CC', 'NN']

    @staticmethod
    def strip_np(np):
        return np.strip(string.punctuation.replace('(', '') + string.whitespace)


np_extractor = CopyrightNPExtractor(grammar=grammar)


def get_copyright(text, return_sources=False) -> Generator:
    """
    Find copyright in text.
    :param text:
    :param return_sources:
    :return:
    """
    # Iterate through sentences
    if COPYRIGHT_PTN_RE.search(text):
        for sentence in get_sentence_list(text):
            for phrase in np_extractor.get_np(sentence):
                cps = COPYRIGHT_PTN_RE.findall(phrase)
                for cp_text, cp_sign, cp_date, cp_name in cps:
                    # TODO: catch in the general regex
                    if not cp_date:
                        cp_date_at_end = YEAR_PTN_RE.search(cp_name)
                        if cp_date_at_end:
                            cp_date = cp_date_at_end.group()
                            cp_name = re.sub(r'{}$'.format(cp_date), '', cp_name)
                    ret = (cp_sign.strip(),
                           cp_date.replace(' ', ''),
                           cp_name.strip(string.punctuation + string.whitespace))
                    if return_sources:
                        ret += (cp_text.strip(),)
                    yield ret
