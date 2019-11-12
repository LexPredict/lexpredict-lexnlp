from collections import Iterable

from typing import Callable, Any


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
