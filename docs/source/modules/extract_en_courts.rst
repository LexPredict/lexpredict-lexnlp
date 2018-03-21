.. _extract_en_courts:

============
:mod:`lexnlp.extract.en.courts`: Extracting court references
============

The :mod:`lexnlp.extract.en.courts` module contains methods that allow for the extraction
of court or venue references from text.

.. attention::
    The methods in this module rely heavily on data from the LexPredict Legal Dictionary repository:
    https://github.com/LexPredict/lexpredict-legal-dictionary

    This repository includes courts such as:
     * Australian courts
     * Canadian courts
     * German courts
     * US Federal and State courts

    This data is governed by a separate Creative Commons Attribution Share Alike 4.0 license here:
    https://github.com/LexPredict/lexpredict-legal-dictionary/blob/master/LICENSE


The full list of current unit test cases can be found here:
https://github.com/LexPredict/lexpredict-lexnlp/tree/master/test_data/lexnlp/extract/en/tests/test_courts


.. currentmodule:: lexnlp.extract.en.courts


Extracting courts
----------------
.. autofunction:: get_courts

Example ::

    >>> # Manually set court configuration data
    >>> import lexnlp.extract.en.courts
    >>> text = "The case will be heard in E.D. Va. next month"
    >>> court_config_data = [entity_config(0, "Eastern District of Virginia", 0, ["E.D. Va."]),
        entity_config(1, "Western District of Virginia", 0, ["W.D. Va."])]
    >>> for entity, alias in lexnlp.extract.en.courts.get_courts(text, court_config_data):
        print("entity=", entity)
        print("alias=", alias)
    entity= (0, 'Eastern District of Virginia', 0, [('Eastern District of Virginia', None, False, None), ('E.D. Va.', None, False, None)])
    alias= ('E.D. Va.', None, False, None)

    >>> # Load court configuration data automatically from LexPredict legal dictionaries
    >>> import pandas
    >>> text = "To be heard in either E.D. Va. or S.D.N.Y."
    >>> court_df = pandas.read_csv("https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.5/en/legal/us_courts.csv")
    >>> # Create config objects
    >>> court_config_data = []
    >>> for _, row in court_df.iterrows():
        c = entity_config(row["Court ID"], row["Court Name"], 0, row["Alias"].split(";") if not pandas.isnull(row["Alias"]) else [])
        court_config_data.append(c)
    >>> for entity, alias in lexnlp.extract.en.courts.get_courts(text, court_config_data):
        print("entity=", entity)
        print("alias=", alias)
    entity= (98, 'Eastern District of Virginia', 0, [('Eastern District of Virginia', None, False, None), ('E.D. Va.', None, False, None)])
    alias= ('E.D. Va.', None, False, None)
    entity= (70, 'Southern District of New York', 0, [('Southern District of New York', None, False, None), ('S.D.N.Y.', None, False, None)])
    alias= ('S.D.N.Y.', None, False, None)
