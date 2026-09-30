from time import monotonic

import pytest

from lexnlp.extract.en.conditions import get_condition_annotations, get_conditions
from lexnlp.extract.en.constraints import get_constraint_annotations, get_constraints


@pytest.mark.parametrize("extractor", [get_conditions, get_constraints])
def test_long_trigger_free_and_near_miss_text_is_bounded(extractor):
    inputs = [
        "a" * 10_000 + ".",
        "a" * 10_000 + " subject tox.",
    ]

    started = monotonic()
    for text in inputs:
        assert list(extractor(text)) == []

    assert monotonic() - started < 1.0


def test_condition_annotations_preserve_multiple_match_spans():
    text = "The Tenant pays, subject to adjustment, until the lease expires."

    annotations = list(get_condition_annotations(text))

    assert [
        (annotation.coords, annotation.condition, annotation.pre, annotation.post) for annotation in annotations
    ] == [
        ((0, 28), "subject to", "The Tenant pays,", ""),
        ((28, 46), "until", "adjustment,", ""),
    ]


def test_constraint_annotations_preserve_multiple_match_spans():
    text = "This is greater than that and within thirty days after notice."

    annotations = list(get_constraint_annotations(text))

    assert [
        (annotation.coords, annotation.constraint, annotation.pre, annotation.post) for annotation in annotations
    ] == [
        ((0, 21), "greater than", "this is", ""),
        ((21, 37), "within", "that and", ""),
        ((37, 55), "after", "thirty days", ""),
    ]


def test_constraint_at_sentence_start_preserves_post_text():
    annotation = next(get_constraint_annotations("After this date everything happens."))

    assert (
        annotation.coords,
        annotation.constraint,
        annotation.pre,
        annotation.post,
    ) == ((0, 35), "after", "", "this date everything happens.")
