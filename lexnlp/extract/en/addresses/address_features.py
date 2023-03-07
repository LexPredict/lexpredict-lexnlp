"""
Features extraction for addresses detecting classifier.
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import json
import os
import re
import string
from datetime import datetime
from email.utils import parseaddr
from typing import List

import nltk
import pycountry
from dateutil import parser as dateparser
import pickle


cwd = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


def _norm(s: str) -> str:
    return s.upper()


def _load_set_from_lines(fn, normalize: bool = False):
    with open(os.path.join(cwd, fn), 'r', encoding='utf-8') as f:
        if normalize:
            return {_norm(l.strip()) for l in f.readlines()}
        return {l.strip() for l in f.readlines()}


STREET_SUFFIXES = _load_set_from_lines('street_suffixes.csv', normalize=True)
BUILDING_SUFFIXES = _load_set_from_lines('building_suffixes.csv', normalize=True)
STREET_DIRECTIONS = _load_set_from_lines('street_directions.csv', normalize=True)

DATE_MIN = datetime(1600, 1, 1)
DATE_MAX = datetime(2300, 1, 1)


def is_datetime(word: str) -> bool:
    if len(word) < 6:
        return False
    try:
        dt = dateparser.parse(word, ignoretz=True)
        if dt < DATE_MIN or dt > DATE_MAX:
            return False
        return True

    # pylint: disable=broad-except
    except Exception:
        return False


URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def is_url(word: str) -> bool:
    return URL_REGEX.fullmatch(word) is not None


def is_single_initial(word: str) -> bool:
    return len(word) == 2 and word[0].isupper() and word[1] == '.'


def is_uppercase_char(word: str) -> bool:
    return len(word) == 1 and word[0].isupper()


def is_lowercase_char(word: str) -> bool:
    return len(word) == 1 and word[0].islower()


def is_email(word: str) -> bool:
    return bool('@' in word and parseaddr(word))


ZIP_CODE = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')


def is_zip_code(s: str) -> bool:
    return bool(ZIP_CODE.fullmatch(s))


def build_country_words():
    words = set()
    for c in pycountry.countries:
        if hasattr(c, 'alpha_2'):
            words.update(_norm(c.alpha_2).split(' '))
        if hasattr(c, 'alpha_3'):
            words.update(_norm(c.alpha_3).split(' '))
        if hasattr(c, 'name'):
            words.update(_norm(c.name).split(' '))
        if hasattr(c, 'official_name'):
            words.update(_norm(c.official_name).split(' '))

    words.discard('')
    words.discard('AND')
    words.discard('OF')
    return words


def build_provinces_words():
    res = set()
    for province in _load_set_from_lines('provinces.txt', normalize=True):
        res.update(province.split(' '))
    res.discard('')
    res.discard(' ')
    res.add('OBLAST')
    return res


def _pickle_load(fn: str):
    with open(fn, 'rb') as f:
        return pickle.load(f)


POS_TAG_SET_INDEX_FN = os.path.join(cwd, 'nltk_pos_tag_indexes.json')

POS_TAG_SET_INDEX = json.load(open(POS_TAG_SET_INDEX_FN, 'r'))

COUNTRY_WORDS = build_country_words()

PROVINCES_WORDS = build_provinces_words()

CITY_NAME_WORDS = _pickle_load(os.path.join(cwd, 'city_name_words.pickle'))

FEATURE_WORD_LEN = 21

ZERO_FEATURES = [0 for _i in range(FEATURE_WORD_LEN)]


def get_word_features(word: str, part_of_speech: str) -> List[int]:
    if not word:
        return ZERO_FEATURES

    word_norm = _norm(word)
    word_no_dots = word_norm.strip('.')
    is_upper = word.isupper()
    all_digits = all(ch.isdigit() for ch in word)
    res = [
        POS_TAG_SET_INDEX.get(part_of_speech or '') or 0,  # part of speech
        int(is_upper or word.istitle()),  # init_cap
        int(is_upper),  # all_caps
        int(all_digits or any(ch.isdigit() for ch in word)),  # contains_digits
        int(all_digits),  # all_digits
        int(all(ch == '.' or ch.isupper() for ch in word)),  # acronym
        int(all(ch in string.punctuation for ch in word)),  # punctuation
        int(is_datetime(word)),  # datetime
        # int(is_url(word)),  # url
        int('\'' in word),  # contraction
        int(is_single_initial(word)),
        int(is_uppercase_char(word)),  # uppercase_char
        int(is_lowercase_char(word)),  # lowercase_char
        int('-' in word),  # contains_dash
        int(len(word) > 5 and all(ch.isdigit() or ch in ' -()' for ch in word)),  # phone
        # int(is_email(word)),  # email
        int(word_no_dots in STREET_SUFFIXES),  # street_suffix
        int(word_no_dots in BUILDING_SUFFIXES),  # building
        int(word_norm in STREET_DIRECTIONS),  # street directions
        int(is_zip_code(word)),
        int(word_norm in COUNTRY_WORDS),
        int(word_norm in PROVINCES_WORDS),
        int(word_norm in CITY_NAME_WORDS)
    ]

    return res


def prepare_pos_tagset_index_file():
    # Building tagset right from nltk requires some manual manipulations on file downloading.
    # Caching them in a json file.
    tagset = {k: i + 1 for i, k in
              enumerate(sorted(nltk.help.load('help/tagsets/upenn_tagset.pickle').keys()))}
    json.dump(tagset, open(POS_TAG_SET_INDEX_FN, 'w'))


if __name__ == '__main__':
    prepare_pos_tagset_index_file()
