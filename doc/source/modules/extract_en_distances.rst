.. _extract_en_distances:

============
:mod:`lexnlp.extract.en.distances`: Extracting distances
============

The :mod:`lexnlp.extract.en.distances` module contains methods that allow for the extraction
of distance references from text.  Distances that are covered by default in this module include:

 * km
 * kilometer
 * mile
 * miles
 * mi

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_distances


.. currentmodule:: lexnlp.extract.en.distances


Extracting conditions
----------------
.. autofunction:: get_distances

Example ::

    >>> import lexnlp.extract.en.distances
    >>> text = "Within 50 miles of office."
    >>> print(list(lexnlp.extract.en.distances.get_distances(text)))
    [(50.0, 'mile')]


Customizing distance extraction
----------------
Distance extraction can be customized.  There are three key module
variables that store the default configuration and one function used to create
a matching instance:

 * `DISTANCE_TOKEN_MAP`: This `Dictionary` stores the map from tokens to standard distance types.  See customization example below.
 * `DISTANCE_SYMBOL_MAP`: This `Dictionary` stores the map from abbreviations to standard distance types.  See customization example below.
 * `DISTANCE_PTN`: This `String` defines the regular expression pattern used to match distances.

The default behavior of this module can be customized by overriding the value of `DISTANCE_PTN_RE`
with a new regular expression.  The example below demonstrates a simple addition of a new distance::

    >>> # Out of the box behavior
    >>> import lexnlp.extract.en.conditions
    >>> text = "This improvement shall extend for no more than fifteen yards."
    >>> print(list(lexnlp.extract.en.distances.get_distances(text)))
    []

    >>> # Customize the regular expression pattern
    >>> import regex as re
    >>> import lexnlp.extract.en.amounts
    >>> lexnlp.extract.en.distances.DISTANCE_TOKEN_MAP["yard"] = "yard"
    >>> lexnlp.extract.en.distances.DISTANCE_TOKEN_MAP["yards"] = "yard"
    >>> lexnlp.extract.en.distances.DISTANCE_SYMBOL_MAP["yd"] = "yard"
    >>> lexnlp.extract.en.distances.DISTANCE_PTN = r"""
    (({num_ptn})\s*
    ({distance_tokens}|{distance_symbols}))(?:\W|$)
    """.format(
        num_ptn=lexnlp.extract.en.amounts.NUM_PTN.replace('(?:\\W|$)', '').replace('(?<=\\W|^)', ''),
        distance_symbols='|'.join(lexnlp.extract.en.distances.DISTANCE_SYMBOL_MAP),
        distance_tokens='|'.join(lexnlp.extract.en.distances.DISTANCE_TOKEN_MAP)
    )
    >>> lexnlp.extract.en.distances.DISTANCE_PTN_RE = re.compile(lexnlp.extract.en.distances.DISTANCE_PTN,
    re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE)

    >>> # Run the method again to test
    >>> print(list(lexnlp.extract.en.distances.get_distances(text)))
    [(15, 'yard')]

