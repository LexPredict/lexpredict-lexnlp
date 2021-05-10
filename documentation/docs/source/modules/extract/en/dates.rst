.. _extract_en_dates:

============
:mod:`lexnlp.extract.en.dates`: Extracting date references
============

The :mod:`lexnlp.extract.en.dates` module contains methods that allow for the extraction
of dates from text.  Sample formats that are handled by this module include:

 * February 1, 1998
 * 2017-06-01
 * 1st day of June, 2017
 * 31 October 2016
 * 15th of March 2000

The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_dates


.. currentmodule:: lexnlp.extract.en.dates


Extracting dates
----------------
.. autofunction:: get_dates

Example ::

    >>> import lexnlp.extract.en.dates
    >>> text = "This agreement shall terminate on the 15th day of March, 2020."
    >>> print(list(lexnlp.extract.en.dates.get_dates(text)))
    [datetime.date(2020, 3, 15)]
    >>> text = "This agreement shall terminate on the 2nd of Apr 2030."
    >>> print(list(lexnlp.extract.en.dates.get_dates(text)))
    [datetime.date(2030, 4, 1)]

.. note::
    This method combines both pattern-matching approaches as well as machine learning and NLP
    to remove false positive matches.  If speed is more important than precision, then users
    should examine the `get_raw_dates` method below or train their own model using a smaller
    feature space or faster machine learning model type.  For more details, see the Advanced
    Usage section below.



Advanced usage and customization
----------------
Out of the box, LexNLP uses a cross-validated logistic classifier whose inputs are
the one-character and two-character sequence distributions within a 5-character window
of the potential date match.  The training and assessment data used can be found
in `train_default_model` and unit tests.

.. autofunction:: get_raw_date_list

.. autofunction:: get_raw_dates

.. autofunction:: get_date_features

.. autofunction:: build_date_model

.. autofunction:: train_default_model