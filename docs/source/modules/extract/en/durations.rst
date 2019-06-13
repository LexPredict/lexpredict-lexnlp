.. _extract_en_durations:

============
:mod:`lexnlp.extract.en.durations`: Extracting durations
============

The :mod:`lexnlp.extract.en.durations` module contains methods that allow for the extraction
of durations from text.  Statements that are covered by default in this module include:

 * after
 * smallest among

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_durations


.. currentmodule:: lexnlp.extract.en.durations


Extracting constraints
----------------
.. autofunction:: get_durations

Example ::

    >>> import lexnlp.extract.en.durations
    >>> text = "This Agreement shall terminate in nine (9) months."
    >>> print(list(lexnlp.extract.en.durations.get_durations(text)))
    [('month', 9.0, 270.0)]

    >>> import lexnlp.extract.en.durations
    >>> text = "The period shall not exceed a dozen seconds."
    >>> print(list(lexnlp.extract.en.durations.get_durations(text)))
    [('second', 12, 0.0001388888888888889)]

Customizing duration statement extraction
----------------
Duration statement extraction can be customized.  There are three key module
variables that store the default configuration:

 * `DURATION_MAP`: This `List` stores the "trigger" phrases that are used to identify constraint statements.  They are typically adverbial or prepositional phrases.
 * `DURATION_PTN`: This `String` stores the regular expression pattern that drives matching in this module.

The default behavior of this module can be customized by overriding the value of `DURATION_PTN_RE`
with a new regular expression created as the code below demonstrates.  The example below
demonstrates a simple addition of a new phrase::

    >>> # Out of the box behavior
    >>> import lexnlp.extract.en.durations
    >>> text = "The Agreement shall terminate in two fortnights."
    >>> print(list(lexnlp.extract.en.durations.get_durations(text)))
    []

    >>> # Customize the durations
    >>> import regex as re
    >>> import lexnlp.extract.en.amounts
    >>> lexnlp.extract.en.durations.DURATION_MAP["fortnight"] = 14
    >>> lexnlp.extract.en.durations.DURATION_PTN = r"""
    (({num_ptn})
    (?:\s*(?:calendar|business|actual))?[\s-]*
    ({duration_list})s?)(?:\W|$)
    """.format(
        num_ptn=lexnlp.extract.en.amounts.NUM_PTN,
        duration_list='|'.join(lexnlp.extract.en.durations.DURATION_MAP)
    )
    >>> lexnlp.extract.en.durations.DURATION_PTN_RE = re.compile(lexnlp.extract.en.durations.DURATION_PTN,
    re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

    >>> # Run the `get_durations` method again to test
    >>> print(list(lexnlp.extract.en.durations.get_durations(text)))
    [('fortnight', 2, 28)]


