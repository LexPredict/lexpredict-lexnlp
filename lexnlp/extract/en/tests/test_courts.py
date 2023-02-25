#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Court/jurisdiction unit tests for English.

This module implements unit tests for the court/jurisdiction extraction functionality in English.

Todo:
    * Re-introduce known bad cases with better main data or more flexible approach
    * More pathological and difficult cases
"""

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import csv
import os
import pandas

from lexnlp.extract.en.dict_entities import DictionaryEntry, DictionaryEntryAlias
from lexnlp.extract.en.courts import _get_courts
from lexnlp.tests import lexnlp_tests


BAD_EXAMPLES = ["""13.  Governing Law;  Submissions to  Jurisdiction.  This Agreement shall be
deemed to be a contract made under the laws of the State of New York and for all
purposes  shall be  construed  in  accordance  with those laws.  The Company and
Employee  unconditionally consent to submit to the exclusive jurisdiction of the
New York State Supreme Court,  County of New York or the United States  District
Court for Southern  District of New York for any actions,  suits or  proceedings
arising  out of or relating  to this  letter and the  transactions  contemplated
hereby  (and agree not to  commence  any  action,  suit or  proceeding  relating
thereto  except in such courts),  and further agree that service of any process,
summons,  notice or document by  registered  mail to the address set forth above
shall be effective service of process for any action, suit or proceeding brought
against the Company or the Employee, as the case may be, in any such court.""",
                """THE  GUARANTOR HEREBY  IRREVOCABLY  SUBMITS  ITSELF TO THE EXCLUSIVE  JURISDICTION  OF BOTH THE
SUPREME  COURT OF THE STATE OF NEW YORK,  NEW YORK COUNTY AND THE UNITED  STATES
DISTRICT COURT FOR THE SOUTHERN  DISTRICT OF NEW YORK, AND ANY APPEAL THEREFROM,
FOR THE  PURPOSE  OF ANY SUIT,  ACTION  OR OTHER  PROCEEDING  ARISING  OUT OF OR
RELATING TO THIS GUARANTY,  AND HEREBY WAIVES,  AND AGREES NOT TO ASSERT, BY WAY
OF MOTION,  AS A DEFENSE OR OTHERWISE,  IN ANY SUIT,  ACTION OR PROCEEDING,  ANY
CLAIM THAT IT IS NOT PERSONALLY  SUBJECT TO THE  JURISDICTION OF THE ABOVE-NAMED
COURTS  FOR ANY  REASON  WHATSOEVER,  THAT SUCH SUIT,  ACTION OR  PROCEEDING  IS
BROUGHT IN AN INCONVENIENT FORUM OR THAT THIS GUARANTY MAY NOT BE ENFORCED IN OR
BY SUCH COURTS.""",
                ]


def test_courts():
    court_df = pandas \
        .read_csv("https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts"
                  ".csv")

    # Create config objects
    court_config_list = []
    for _, row in court_df.iterrows():
        court_config_list.append(build_dictionary_entry(row))
    lexnlp_tests.test_extraction_func_on_test_data(_get_courts, court_config_list=court_config_list,
                                                   actual_data_converter=lambda actual:
                                                   [cc[0].name for cc in actual])


def test_courts_rs():
    """
    Test court extraction with return sources.
    :return:
    """

    # Read main data
    # Load court data
    court_df = pandas \
        .read_csv("https://raw.githubusercontent.com/LexPredict/lexpredict-legal-dictionary/1.0.2/en/legal/us_courts"
                  ".csv")

    # Create config objects
    court_config_list = []
    for _, row in court_df.iterrows():
        court_config_list.append(build_dictionary_entry(row))

    lexnlp_tests.test_extraction_func_on_test_data(_get_courts,
                                                   court_config_list=court_config_list,
                                                   actual_data_converter=lambda actual: [cc[0].name for cc in actual])


def test_courts_longest_match():
    """
    Tests the case when there are courts having names/aliases being one a substring of another.
    In such case the court having longest alias should be returned for each conflicting matching.
    But for the case when there is another match of the court having shorter alias in that conflict,
    they both should be returned.
    :return:
    """
    courts_config_fn = os.path.join(os.path.dirname(lexnlp_tests.this_test_data_path()), 'us_courts.csv')
    courts_config_list = []
    with open(courts_config_fn, 'r', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            aliases = []
            if row['Alias']:
                aliases = [DictionaryEntryAlias(r) for r in row['Alias'].split(';')]
            cc = DictionaryEntry(id=int(row['Court ID']),
                                 name=row['Court Type'] + '|' + row['Court Name'],
                                 priority=0,
                                 name_is_alias=False,
                                 aliases=aliases,
                               )
            cc.aliases.append(DictionaryEntryAlias(row['Court Name']))
            courts_config_list.append(cc)

    lexnlp_tests.test_extraction_func_on_test_data(_get_courts, court_config_list=courts_config_list,
                                                   actual_data_converter=lambda actual:
                                                   [tuple(c[0].name.split('|')) for c in actual],
                                                   debug_print=True)


def build_dictionary_entry(row):
    aliases = []
    if not pandas.isnull(row["Alias"]):
        aliases = [DictionaryEntryAlias(r) for r in row['Alias'].split(';')]
    return DictionaryEntry(
        int(row['Court ID']), row['Court Name'], 0, aliases=aliases)
