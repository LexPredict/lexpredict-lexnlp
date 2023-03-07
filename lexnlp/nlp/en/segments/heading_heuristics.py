# -*- coding: utf-8 -*-

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re


class HeadingHeuristics:
    """
    This class helps to decide which of the two strings
    looks more like a section heading (title)
    """

    # detect section numbering in possible heading
    HEADING_DETECTOR_RE = re.compile(r"(^[IVXC][IVXC\.]*\s)|(^\d[\d\.]*\s)")
    # string longer than MAX_LEN is hardly a heading
    MAX_LEN = 150
    # string longer than MAX_PLAUS_LEN still can be a heading
    MAX_PLAUS_LEN = 100
    # string shorter than MIN_PLAUS_LEN is hardly a heading
    MIN_LEN = 4
    # old title variant's preference
    OLD_PREFERENCE = 7
    # weights in total score:
    # contains title; length is optimal; longer than another; capitalized; starts with numbering; contains linebreak;
    SCORE_WEIGHTS = [10, 10, 5, 5, 10, -20]

    @classmethod
    def is_new_title_better(cls, existing_title: str, possible_title: str) -> bool:
        score_new = cls.get_title_score(existing_title, possible_title)
        if score_new < 0:
            return False
        score_old = cls.get_title_score(possible_title, existing_title) + cls.OLD_PREFERENCE
        return score_old <= score_new

    @classmethod
    def get_title_score(cls, existing_title: str, possible_title: str):
        if len(possible_title) > cls.MAX_LEN:
            return -1000
        if len(possible_title) < cls.MIN_LEN:
            return -1000

        # check if possible_title is a good replacement for section title already found
        contains_title = existing_title.replace(' ', '') in possible_title.replace(' ', '')
        optimal_len = len(possible_title) < cls.MAX_PLAUS_LEN
        capitalized = possible_title.upper() == possible_title
        longer_than = cls.MAX_PLAUS_LEN > len(possible_title) > len(existing_title)
        contains_linebreak = '\n' in possible_title

        starts_with_numbering = cls.HEADING_DETECTOR_RE.search(possible_title) is not None

        ws = cls.SCORE_WEIGHTS
        score = contains_title * ws[0] + optimal_len * ws[1] +\
            longer_than * ws[2] + capitalized * ws[3] +\
            starts_with_numbering * ws[4] + contains_linebreak * ws[5]
        return score
