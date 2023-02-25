"""
Addresses extraction for English language.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import re
from typing import Generator, Tuple, List

from lexnlp.extract.en.addresses import address_features
from lexnlp.extract.en.preprocessing.span_tokenizer import SpanTokenizer
from lexnlp.extract.common.annotations.address_annotation import AddressAnnotation
from lexnlp.utils.unpickler import renamed_load

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
        return False

    def __hash__(self):
        return hash(self.members())


class NGramType:
    OTHER = 0
    ADDR_START = 1
    ADDR_MIDDLE = 2
    ADDR_END = 3


TOKENIZER = SpanTokenizer()


def _safe_index(sentence, token, point, safe: bool = False):
    try:
        return sentence.index(token, point)
    except ValueError:
        if safe:
            return None
        raise ValueError(f'Substring "{token}" not found in:\n'
                         f'"{sentence}"\n'
                         f'Search start pos: {point}')


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
        if token in ('``', "''"):
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
        return renamed_load(f)


NGRAM_CLASSIFIER = load_classifier()
NGRAM_WINDOW_HALF_WIDTH = 10
NGRAM_WINDOW_STEP = 1


def prepare_ngrams_in_text(
    text: str,
    window_half_width: int,
    window_step: int
) -> Generator[Tuple[List[int], str, int, int], None, None]:
    words2 = []

    for word, pos_token, word_start_pos, word_end_pos in TOKENIZER.get_token_spans(text):
        features = address_features.get_word_features(word, pos_token)
        # our tokenizer returns exact word_end_pos and we need it so that text[word_start_pos:word_end_pos] == word
        words2.append((word, pos_token, word_start_pos, word_end_pos + 1, features))

    i = 0
    len_words2 = len(words2)
    while i < len_words2:
        word, pos_token, word_start_pos, word_end_pos, _ = words2[i]
        features = []
        for j in range(i - window_half_width, i + window_half_width):
            if 0 <= j < len_words2:
                features.extend(words2[j][4])
            else:
                features.extend(address_features.ZERO_FEATURES)
        yield features, word, word_start_pos, word_end_pos
        i += window_step


_MARGIN_TOLERANCE = 2


def cleanup(address: str) -> str:
    address = address.strip('?:!.,;-_ \t')
    address = re.sub(r'\s+', ' ', address)
    return address


def get_address_annotations(text: str) -> Generator[AddressAnnotation, None, None]:
    for address, start, end in get_address_spans(text):
        yield AddressAnnotation(
            coords=(start, end),
            name='',
            locale='en',
            text=text,
        )


def get_addresses(text: str) -> Generator[str, None, None]:
    for addr, _start, _end in get_address_spans(text):
        yield addr


def get_address_spans(text: str) -> Generator[Tuple[str, int, int], None, None]:
    possible_address_start = None
    possible_address_end = None
    margin = 0
    for ngram_features, _word, word_start_pos, word_end_pos \
            in prepare_ngrams_in_text(text, NGRAM_WINDOW_HALF_WIDTH, NGRAM_WINDOW_STEP):
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
                        yield cleanup(possible_address), possible_address_start, possible_address_end
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
        yield cleanup(possible_address), possible_address_start, possible_address_end
