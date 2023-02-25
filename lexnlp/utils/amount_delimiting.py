__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# -*- coding: utf-8 -*-

import locale
from typing import Dict, FrozenSet, List, NamedTuple, Optional, Tuple, Set
from lexnlp.extract.all_locales.languages import LocaleContextManager


# https://en.wikipedia.org/wiki/Decimal_separator


DELIMITERS: FrozenSet = frozenset((
    '\u0020',  # U+0020   SPACE (HTML &#32;)
    '\u0027',  # U+0027 ' APOSTROPHE (HTML &#39; · &apos;)
    '\u002C',  # U+002C , COMMA (HTML &#44; · &comma;)
    '\u002E',  # U+002E . FULL STOP (HTML &#46; · &period;) - Full stop punctuation mark.
    '\u00B7',  # U+00B7 · MIDDLE DOT (HTML &#183; · &middot;, &CenterDot;, &centerdot;)
    '\u2009',  # U+2009   THIN SPACE (HTML &#8201; · &thinsp;, &ThinSpace;)
    '\u202F',  # U+202F   NARROW NO-BREAK SPACE (HTML &#8239;)
    '\u02D9',  # U+02D9 ˙ DOT ABOVE (HTML &#729; · &DiacriticalDot;, &dot;)
))


class DelimitedBlock(NamedTuple):
    """
    Examples:
        - .25, represented as <length=2, delimiter=".">
        - ,000, represented as <length=3, delimiter=",">
        - '500, represented as <length=3, delimiter="'">
    """
    length: int
    delimiter: str


def get_delimited_blocks(
    text: str,
) -> Optional[Tuple[Set[str], List[DelimitedBlock]]]:
    """
    Splits text on delimiters into `DelimitedBlocks` containing the block length
    and its preceding delimiter.

    Examples:
        - 17.569     --> [ <3.> ], corresponding to 569
        - 10,000,000 --> [ <3,> , <3,> ], corresponding to ,000 and ,000
        - 15'000.67  --> [ <3'> , <2.> ], corresponding to '000 and .67
    """
    start = 0
    delimiter = None
    delimiters: Set[str] = set()
    blocks: List[DelimitedBlock] = []

    for count, character in enumerate(text):
        if character in DELIMITERS:
            delimiters.add(character)
            if delimiter is not None:
                blocks.append(
                    DelimitedBlock(
                        length=count - start - 1,
                        delimiter=delimiter
                    )
                )
            start = count
            delimiter = character
    try:
        blocks.append(DelimitedBlock(length=count - start, delimiter=delimiter))
    except NameError:
        # `text` is an empty string, so `count` was never initialized
        return None
    return delimiters, blocks


def check_block_grouping(
    blocks: List[DelimitedBlock],
    decimal_delimiter: str,
    grouping: List[int],
) -> bool:
    """
    Args:
        blocks: DelimitedBlocks, in-order from left to right
        decimal_delimiter: Typically a period or comma.
        grouping: a GNU locale LC_NUMERIC grouping.
            Example, de_DE: [3, 3, 0]
            Example, en_IN: [3, 2, 0]

    Notes:
        https://www.gnu.org/software/libc/manual/html_node/General-Numeric.html

    Iterates backwards over the blocks. If a block's length does not meet the
    permitted length at a given block index, then two checks are performed.
    If the block's delimiter is the same as the decimal delimiter and the block
    index is greater than zero, then we immediately fail and return False.
    If the block's delimiter is the same as the decimal delimiter and
    the block index is zero, we record that the decimal delimiter has been
    encountered. If the same block delimiter is encountered again, we
    immediately fail and return False.
    """
    len_grouping: int = len(grouping)
    permitted_length: int = grouping[0]
    encountered_delimiters: Set[str] = set()

    for index, block in enumerate(reversed(blocks)):

        if index < len_grouping:
            if grouping[index] != 0:
                permitted_length = grouping[index]

        if block.length != permitted_length:
            block_delimiter = block.delimiter
            if block_delimiter == decimal_delimiter:
                if index > 0:
                    return False
                encountered_delimiters.add(block_delimiter)
            else:
                return False

        elif block.delimiter in encountered_delimiters:
            return False

    return True


def infer_delimiters(
    text: str,
    _locale: str,
) -> Optional[Dict[str, Optional[str]]]:
    """
    Infers decimal and group delimiters based on the input text, falling back
    on GNU locales when needed.

    Args:
        text: an input string of digits and delimiters
        _locale: an input string like `en_US` or `de_CH`

    Returns:
        A dictionary with two keys:
        - decimal_delimiter
        - group_delimiter
        The respective values can either be a character (the delimiter)
        or `None` for when the delimiter could not be inferred.

        `None` is returned when neither delimiter can be inferred, usually
        because the digits are improperly formatted (misaligned grouping).

    Warning:
        For locales in which the period/full stop is used as a grouping delimiter,
        then inputted IPv4 addresses will be understood as integers greater
        than 10^9 (short-scale billions). Example: "255.255.255.255"
    """
    if not text.isnumeric():
        temp_text = text
        for delimiter in DELIMITERS:
            temp_text = temp_text.replace(delimiter, '')
        if not temp_text.isnumeric():
            return None

    # TODO: be careful with the locale string!
    #   - ".UTF-8" is hardcoded... will this always be correct?
    #   - exception handling for when locales are not available
    with LocaleContextManager(locale.LC_NUMERIC, f'{_locale}.UTF-8'):
        locale_conventions = locale.localeconv()
        decimal_delimiter: str = locale_conventions['decimal_point']
        group_delimiter: str = locale_conventions['thousands_sep']
        grouping: List[int] = locale_conventions['grouping']

    delimiters, blocks = get_delimited_blocks(text)
    len_delimiters: int = len(delimiters)

    if len_delimiters > 2:
        # `text` contains more than two unique delimiters, and is invalid
        return None

    if len_delimiters == 0:
        # `text` is an integer without delimiters
        return {
            'decimal_delimiter': decimal_delimiter,
            'group_delimiter': group_delimiter
        }

    if len_delimiters == 2:
        decimal_delimiter = ''
        group_delimiter = ''

        # `text` is a floating point number greater than one
        for delimiter in delimiters:
            if delimiter == blocks[-1].delimiter:
                decimal_delimiter = delimiter
            else:
                group_delimiter = delimiter

        if decimal_delimiter and group_delimiter:
            return {
                'decimal_delimiter': decimal_delimiter,
                'group_delimiter': group_delimiter
            }

        if not check_block_grouping(blocks, decimal_delimiter, grouping):
            return None

        return {
            'decimal_delimiter': decimal_delimiter,
            'group_delimiter': group_delimiter
        }

    # len_delimiters == 1
    if len(blocks) == 1:
        block: DelimitedBlock = blocks[0]
        delimiter: str = delimiters.pop()

        if block.length == 3 and block.delimiter != decimal_delimiter:
            return {
                'decimal_delimiter': None,
                'group_delimiter': block.delimiter
            }

        if block.length == grouping[0]:
            # `text` is an integer
            return {
                'decimal_delimiter': decimal_delimiter,
                'group_delimiter': delimiter if delimiter != decimal_delimiter else group_delimiter
            }

        # `text` is a floating point number less than one
        return {
            'decimal_delimiter': block.delimiter,
            'group_delimiter': group_delimiter if group_delimiter != block.delimiter else None
        }

    # other cases
    if not check_block_grouping(blocks, decimal_delimiter, grouping):
        return None
    return {
        'decimal_delimiter': decimal_delimiter if decimal_delimiter not in delimiters else None,
        'group_delimiter': delimiters.pop() or group_delimiter
    }
