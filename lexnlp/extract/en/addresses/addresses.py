"""
Addresses extraction for English language.
"""
import os
import pickle
import re
from typing import Generator, Tuple, List

import nltk
from nltk.tokenize.treebank import TreebankWordTokenizer

from lexnlp.extract.en.addresses import address_features

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

NGRAM_CLASSIFIER_FN = os.path.join(os.path.dirname(__file__), 'addresses_clf.pickle')


class Address:
    def __init__(self, zip_code: str,
                 country: str,
                 state: str,
                 city: str,
                 addr1: str,
                 addr2: str) -> None:
        super().__init__()
        self.zip_code = zip_code
        self.country = country
        self.state = state
        self.city = city
        self.addr1 = addr1
        self.addr2 = addr2 if addr2 != addr1 else None

    def __str__(self) -> str:
        return '{0}, {1}, {2}, {3}, {4}, {5}'.format(self.addr1, self.addr2, self.city, self.state,
                                                     self.country, self.zip_code)

    def members(self):
        return self.zip_code, self.country, self.state, self.city, self.addr1, self.addr2

    def __eq__(self, other):
        if type(other) is type(self):
            return self.members() == other.members()
        else:
            return False

    def __hash__(self):
        return hash(self.members())


class NGramType:
    OTHER = 0
    ADDR_START = 1
    ADDR_MIDDLE = 2
    ADDR_END = 3


TOKENIZER = TreebankWordTokenizer()


def _safe_index(sentence, token, point, safe: bool = False):
    try:
        return sentence.index(token, point)
    except ValueError:
        if safe:
            return None
        else:
            raise ValueError('substring "{}" not found in "{}"'.format(token, sentence))


def align_tokens(tokens, sentence):
    """
    Copy of the same function from nltk fixing processing of double quotes.
    :param tokens:
    :param sentence:
    :return:
    """
    point = 0
    offsets = []
    for token in tokens:
        if token == '``' or token == "''":
            start = _safe_index(sentence, '"', point, True)
            if start is None:
                start = _safe_index(sentence, '\'', point)
            point += 1
        else:
            start = _safe_index(sentence, token, point)
            point = start + len(token)
        offsets.append((start, point))
    return offsets


def load_classifier():
    with open(NGRAM_CLASSIFIER_FN, 'rb') as f:
        return pickle.load(f)


NGRAM_CLASSIFIER = load_classifier()
NGRAM_N = 5


def prepare_ngrams_in_text(text: str, n: int) \
        -> Generator[Tuple[List[int], List[str], int, int], None, None]:
    tokens = TOKENIZER.tokenize(text)
    token_spans = align_tokens(tokens, text)
    tagged_words = nltk.pos_tag(tokens)

    words2 = []
    for i in range(len(tagged_words)):
        span = token_spans[i]
        word = text[span[0]:span[1]]
        pos = tagged_words[i][1]
        features = address_features.get_word_features(word, pos)
        words2.append((word, span, pos, features))

    for i in range(len(words2)):
        word = words2[i][0]
        word_start_pos = words2[i][1][0]
        word_end_pos = words2[i][1][1]
        features = list()
        for j in range(i - n, i + n - 1):
            if 0 <= j < len(words2):
                features.extend(words2[j][3])
            else:
                features.extend(address_features.ZERO_FEATURES)
        yield features, word, word_start_pos, word_end_pos


_MARGIN_TOLERANCE = 3


def cleanup(address: str) -> str:
    address = address.strip('?:!.,;-_ \t')
    address = re.sub(r'\s+', ' ', address)
    return address


def get_addresses(text: str) -> Generator[str, None, None]:
    possible_address_start = None
    possible_address_end = None
    margin = 0
    for ngram_features, _word, word_start_pos, word_end_pos \
            in prepare_ngrams_in_text(text, NGRAM_N):
        ngram_type = NGRAM_CLASSIFIER.predict([ngram_features])

        if possible_address_start is None:
            if ngram_type in (NGramType.ADDR_START, NGramType.ADDR_MIDDLE):
                possible_address_start = word_start_pos
                possible_address_end = word_end_pos
                margin = 0
        else:
            if ngram_type in (NGramType.ADDR_MIDDLE, NGramType.ADDR_END):
                possible_address_end = word_end_pos
                margin = 0
            elif ngram_type == NGramType.OTHER:
                if margin >= _MARGIN_TOLERANCE:
                    if possible_address_end - possible_address_start >= 20:
                        possible_address = text[possible_address_start:possible_address_end]
                        yield cleanup(possible_address)
                    possible_address_end = None
                    possible_address_start = None
                    margin = 0
                else:
                    margin += 1
            else:  # ngram start again
                possible_address_end = word_end_pos
                possible_address_start = word_start_pos
                margin = 0

    if possible_address_start is not None:  # text ends with address
        possible_address = text[possible_address_start:possible_address_end]
        yield cleanup(possible_address)
