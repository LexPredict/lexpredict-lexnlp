"""Condition extraction for English.

This module implements basic condition extraction functionality in English.

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
import regex as re
from typing import Generator, List, Optional, Tuple

from lexnlp.extract.common.annotations.condition_annotation import ConditionAnnotation
from lexnlp.nlp.en.segments.sentences import get_sentence_list


CONDITION_PHRASES = ['if', 'if not', 'when', 'when not', 'where', 'where not', 'unless and until', 'unless',
                     'unless not', 'until', 'until not', 'as soon as', 'as soon as not', 'provided that',
                     'provided that not', 'subject to', 'not subject to', 'upon the occurrence',
                     'subject to', 'conditioned  on', 'conditioned  upon']

CONDITION_PATTERN_TEMPLATE = r'''(?P<pre>.*?)[\s\.\,](?P<condition>{condition_pattern}){{1,}}[\s\.\,](?P<post>.*?)'''


# ================================
# Patterns for condition matching
# ================================
def create_condition_pattern(condition_pattern_template, condition_phrases):
    """
    Create condition pattern.
    :param condition_pattern_template:
    :param condition_phrases:
    :return:
    """
    # Materialize pattern form intermediate word lists
    pattern_condition_phrases = copy.copy(condition_phrases)
    pattern_condition_phrases.sort(key=len, reverse=True)

    return condition_pattern_template.format(
        condition_pattern="|".join(
            [
                p.replace(r" ", r"\ ")
                for p in pattern_condition_phrases
            ]
        )
    )


# Materialize pattern and create regex
CONDITION_PATTERN = create_condition_pattern(CONDITION_PATTERN_TEMPLATE, CONDITION_PHRASES)
RE_CONDITION = re.compile(CONDITION_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)


def get_conditions(
    text: str,
    strict: bool = True,
) -> Generator[Tuple[Optional[str], Optional[str], Optional[str]], None, None]:
    """
    Get conditions possible conditions from natural language.

    Args:
        text (str):
            An input string to search for conditions.

        strict (bool=True):

    Yields:
        Tuples representing conditions.
    """
    for ant in get_condition_annotations(text, strict):
        yield ant.condition, ant.pre, ant.post


def get_condition_list(text, strict: bool = True) -> List[Tuple[Optional[str], Optional[str], Optional[str]]]:
    """
    Get a list of conditions possible conditions from natural language.

    Args:
        text (str):
            An input string to search for conditions.

        strict (bool=True):


    Yields:
        Tuples representing conditions.
    """
    return list(get_conditions(text, strict))


def get_condition_annotations(text: str, strict: bool = True) -> Generator[ConditionAnnotation, None, None]:
    """
    Get ConditionAnnotations.

    Args:
        text (str):
            An input string to search for conditions.

        strict (bool=True):


    Yields:
        ConditionAnnotation
    """

    # Iterate through all potential matches
    for sentence in get_sentence_list(text):
        for match in RE_CONDITION.finditer(sentence):
            # Get individual group matches
            captures = match.capturesdict()
            num_pre = len(captures["pre"])
            num_post = len(captures["post"])

            # Skip if strict and empty pre/post
            if strict and (num_pre == 0 or num_post == 0):
                continue

            ant = ConditionAnnotation(
                coords=match.span(),
                condition=captures["condition"].pop().lower(),
                pre=captures["pre"].pop(),
                post=captures["post"].pop(),
            )
            yield ant


def get_condition_annotation_list(text: str, strict: bool = True) -> List[ConditionAnnotation]:
    """
    Get a list of ConditionAnnotations.

    Args:
        text (str):
            An input string to search for conditions.

        strict (bool=True):


    Returns:
        A list of ConditionAnnotations
    """
    return list(get_condition_annotations(text, strict))
