import pytest

from lexnlp.utils.decorators import safe_failure


def test_safe_failure_preserves_scalar_return_type():
    calls = []

    @safe_failure
    def scalar(value):
        calls.append(value)
        return value * 2

    assert scalar(3) == 6
    assert calls == [3]


def test_safe_failure_invokes_generator_once_and_keeps_partial_results():
    calls = []

    @safe_failure
    def generate():
        calls.append('called')
        yield 1
        raise ValueError('bad input')

    assert list(generate()) == [1]
    assert calls == ['called']


def test_safe_failure_can_reraise_failures():
    @safe_failure
    def scalar():
        raise ValueError('bad input')

    assert scalar() is None
    with pytest.raises(ValueError, match='bad input'):
        scalar(safe_failure=False)


def test_safe_failure_preserves_broad_exception_suppression():
    @safe_failure
    def scalar():
        raise TypeError('programmer error')

    assert scalar() is None
    with pytest.raises(TypeError, match='programmer error'):
        scalar(safe_failure=False)


def test_safe_failure_does_not_suppress_process_control_exceptions():
    @safe_failure
    def scalar():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        scalar()
