from collections import Iterable

from typing import Callable, Any

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def collapse_sequence(sequence: Iterable,
                      predicate: Callable[[Any, Any], Any],
                      accumulator: Any = 0.0) -> Any:
    for item in sequence:
        accumulator = predicate(item, accumulator)
    return accumulator


def count_sequence_matches(sequence: Iterable,
                           predicate: Callable[[Any], bool]) -> int:
    return collapse_sequence(sequence,
                             lambda i, a: a + 1 if predicate(i) else a, 0)
