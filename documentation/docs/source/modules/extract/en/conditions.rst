.. _extract_en_conditions:

============
:mod:`lexnlp.extract.en.conditions`: Extracting conditional statements
============

The :mod:`lexnlp.extract.en.conditions` module contains methods that allow for the extraction
of conditional statements from text.  Statements that are covered by default in this module are:

 * if
 * if not
 * when
 * when not
 * where
 * where not
 * unless and until
 * unless
 * unless not
 * until
 * until not
 * as soon as
 * as soon as not
 * provided that
 * provided that not
 * subject to
 * not subject to
 * upon the occurrence
 * subject to
 * conditioned  on
 * conditioned  upon


The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_conditions


.. currentmodule:: lexnlp.extract.en.conditions


Extracting conditions
----------------
.. autofunction:: get_conditions

Example ::

    >>> import lexnlp.extract.en.conditions
    >>> text = "This will occur unless something else happens."
    >>> print(list(lexnlp.extract.en.conditions.get_conditions(text)))
    [('unless and until', 'This will occur', '')]

    >>> import lexnlp.extract.en.conditions
    >>> text = "Immediately upon the occurrence of a Change in Control of the Company or the Bank, the Employee shall be paid $125,000.00."
    >>> print(list(lexnlp.extract.en.conditions.get_conditions(text)))
    [('upon the occurrence', 'Immediately', '')]


Customizing conditional statement extraction
----------------

Conditional statement extraction can be customized.  There are two key module
variables that store the default configuration and one function used to create
a matching instance:

 * `CONDITION_PHRASES`: This `List` stores the "trigger" phrases that are used to identify conditional statements.  They are typically conjunctions or conjunction phrases.
 * `CONDITION_PATTERN_TEMPLATE`: This `String` stores the regular expression pattern that drives matching in this module.

.. autofunction:: create_condition_pattern

.. note::
    For more examples and information about conditional statements, see the linguistic resources below:
     * http://www-personal.umich.edu/~jlawler/subordinatingconjunctions.pdf


The default behavior of this module can be customized by overriding the value of `RE_CONDITION`
with a new regular expression created using `create_condition_pattern` above.  The example below
demonstrates a simple addition of a new phrase::

    >>> # Out of the box behavior
    >>> import lexnlp.extract.en.conditions
    >>> text = "This will occur predicated upon something else."
    >>> print(list(lexnlp.extract.en.conditions.get_conditions(text)))
    []

    >>> # Customize the `RE_CONDITION` variable by adding a new phrase
    >>> import regex as re
    >>> my_condition_phrases = lexnlp.extract.en.conditions.CONDITION_PHRASES
    >>> my_condition_phrases.append("predicated upon")
    >>> CONDITION_PATTERN = lexnlp.extract.en.conditions.create_condition_pattern(lexnlp.extract.en.conditions.CONDITION_PATTERN_TEMPLATE, my_condition_phrases)
    >>> lexnlp.extract.en.conditions.RE_CONDITION = re.compile(CONDITION_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

    >>> # Run the `get_conditions` method again to test
    >>> print(list(lexnlp.extract.en.conditions.get_conditions(text)))
    [('predicated upon', 'This will occur', '')]

