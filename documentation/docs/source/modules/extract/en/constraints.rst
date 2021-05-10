.. _extract_en_constraints:

============
:mod:`lexnlp.extract.en.constraints`: Extracting constraint statements
============

The :mod:`lexnlp.extract.en.constraints` module contains methods that allow for the extraction
of constraint statements from text.  Statements that are covered by default in this module are:

 * after
 * at least
 * at most
 * before
 * equal to
 * exactly
 * first of
 * greater
 * greater of
 * greater than
 * greater than or equal to
 * greatest of
 * last of
 * least of
 * lesser
 * lesser of
 * lesser than
 * less than
 * less than or equal to
 * maximum of
 * maximum
 * minimum of
 * minimum
 * more than
 * more than or equal to
 * no earlier than
 * no later than
 * no less than
 * no more than
 * not equal to
 * not to exceed
 * earlier than
 * later than
 * within
 * exceed
 * exceeds
 * prior to
 * highest
 * least
 * smallest among

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_constraints


.. currentmodule:: lexnlp.extract.en.constraints


Extracting constraints
----------------
.. autofunction:: get_constraints

Example ::

    >>> import lexnlp.extract.en.constraints
    >>> text = "This will occur at most three times."
    >>> print(list(lexnlp.extract.en.constraints.get_constraints(text)))
    [('at most', 'this will occur', '')]

    >>> import lexnlp.extract.en.conditions
    >>> text = "The rate shall be no less than 50 bps."
    >>> print(list(lexnlp.extract.en.constraints.get_constraints(text)))
    [('no less than', 'the rate shall be', '')]


Customizing constraint statement extraction
----------------

Constraint statement extraction can be customized.  There are two key module
variables that store the default configuration and one function used to create
a matching instance:

 * `CONSTRAINT_PHRASES`: This `List` stores the "trigger" phrases that are used to identify constraint statements.  They are typically adverbial or prepositional phrases.
 * `CONSTRAINT_PATTERN_TEMPLATE`: This `String` stores the regular expression pattern that drives matching in this module.

.. autofunction:: create_constraint_pattern

.. note::
    For more examples and information about natural language constraints, see the linguistic resources below:
     * https://www.ijcai.org/Proceedings/16/Papers/111.pdf
     * https://www.sciencedirect.com/science/article/pii/S131915781200002X


The default behavior of this module can be customized by overriding the value of `RE_CONSTRAINT`
with a new regular expression created using `create_constraint_pattern` above.  The example below
demonstrates a simple addition of a new phrase::

    >>> # Out of the box behavior
    >>> import lexnlp.extract.en.constraints
    >>> text = "The applicable rate shall be the smallest among thing A and thing B at time T."
    >>> print(list(lexnlp.extract.en.constraints.get_constraints(text)))
    []

    >>> # Customize the `RE_CONSTRAINT` variable by adding a new phrase
    >>> import regex as re
    >>> my_constraint_phrases = lexnlp.extract.en.constraints.CONSTRAINT_PHRASES
    >>> my_constraint_phrases.append("smallest among")
    >>> CONSTRAINT_PATTERN = lexnlp.extract.en.constraints.create_constraint_pattern(lexnlp.extract.en.constraints.CONSTRAINT_PATTERN_TEMPLATE, my_constraint_phrases)
    >>> lexnlp.extract.en.constraints.RE_CONSTRAINT = re.compile(CONSTRAINT_PATTERN, re.IGNORECASE | re.UNICODE | re.DOTALL | re.MULTILINE | re.VERBOSE)

    >>> # Run the `get_constraints` method again to test
    >>> print(list(lexnlp.extract.en.constraints.get_constraints(text)))
    [('smallest among', 'the applicable rate shall be the', '')]

