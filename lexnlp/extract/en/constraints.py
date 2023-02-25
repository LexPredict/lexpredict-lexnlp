"""Constraint extraction for English.

This module implements basic constraint extraction functionality in English.

Todo:
  * Improved unit tests and case coverage
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import copy
from typing import Generator, List, Optional, Tuple

import regex as re

from lexnlp.extract.common.annotations.constraint_annotation import ConstraintAnnotation
from lexnlp.nlp.en.segments.sentences import get_sentence_list


CONSTRAINT_PHRASES = ['after', 'at least', 'at most', 'before', 'equal to', 'exactly', 'first of', 'greater',
                      'greater of', 'greater than', 'greater than or equal to', 'greatest of', 'last of', 'least of',
                      'lesser', 'lesser of', 'lesser than', 'less than', 'less than or equal to', 'maximum of',
                      'maximum', 'minimum of', 'minimum', 'more than', 'more than or equal to', 'no earlier than',
                      'no later than', 'no less than', 'no more than', 'not equal to', 'not to exceed', 'earlier than',
                      'later than', 'within', 'exceed', 'exceeds', "prior to", "highest", "least"]

CONSTRAINT_PATTERN_TEMPLATE = r'''
(
    (
        (?P<pre>.*?)[\s\.\,\;](?P<constraint>{constraint_pattern}){{1,}}[\s\.\,\;](?P<post>.)*?
    )
    |
    (
        (?P<constraint>{constraint_pattern}){{1,}}[\s\.\,\;](?P<post>.+)
    )
)+?
'''


# ================================
# Patterns for duration matching
# ================================
def create_constraint_pattern(constraint_pattern_template, constraint_phrases):
    """
    Create constraint pattern.
    :param constraint_pattern_template:
    :param constraint_phrases:
    :return:
    """
    # Materialize pattern form intermediate word lists
    pattern_constraint_phrases = copy.copy(constraint_phrases)
    pattern_constraint_phrases.sort(key=len, reverse=True)

    return constraint_pattern_template \
        .format(constraint_pattern="|".join([p.replace(r" ", r"\ ") for p in pattern_constraint_phrases]))


# Materialize pattern and create regex
CONSTRAINT_PATTERN = create_constraint_pattern(CONSTRAINT_PATTERN_TEMPLATE, CONSTRAINT_PHRASES)
RE_CONSTRAINT = re.compile(CONSTRAINT_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)


def get_constraints(
    text: str,
    strict: bool = False,
) -> Generator[Tuple[Optional[str], Optional[str], Optional[str]], None, None]:
    """
    Find possible constraints in natural language.
    :param text:
    :param strict:
    :return:
    """

    # Iterate through all potential matches
    for ant in get_constraint_annotations(text, strict):
        yield ant.constraint, ant.pre, ant.post


def get_constraint_list(
    text: str,
    strict: bool = False,
) -> List[Tuple[Optional[str], Optional[str], Optional[str]]]:
    """
    Find possible constraints in natural language.
    :param text:
    :param strict:
    :return:
    """
    return list(get_constraints(text, strict))


def get_constraint_annotations(text: str, strict: bool = False) -> Generator[ConstraintAnnotation, None, None]:
    """
    Find possible constraints in natural language.
    :param text:
    :param strict:
    :return:
    """

    # Iterate through all potential matches
    for sentence in get_sentence_list(text):
        for match in RE_CONSTRAINT.finditer(sentence.lower()):
            # Get individual group matches
            captures = match.capturesdict()
            num_pre = len(captures["pre"])
            num_post = len(captures["post"])

            # Skip if strict and empty pre/post
            if strict and (num_pre + num_post == 0):
                continue

            # Setup fields
            constraint = captures.get("constraint").pop().lower()
            pre = "".join(captures["pre"])
            post = "".join(captures["post"])

            if num_post == 0 and num_pre == 1:
                combined = "{0} {1}".format(pre, constraint).lower().strip()
                if combined in CONSTRAINT_PHRASES:
                    constraint = combined

            ant = ConstraintAnnotation(coords=match.span(),
                                       constraint=constraint,
                                       pre=pre,
                                       post=post)
            yield ant


def get_constraint_annotation_list(text: str, strict: bool = False) -> List[ConstraintAnnotation]:
    """
    Find possible constraints in natural language.
    :param text:
    :param strict:
    :return: A list of ConstraintAnnotations
    """
    return list(get_constraint_annotations(text, strict))
